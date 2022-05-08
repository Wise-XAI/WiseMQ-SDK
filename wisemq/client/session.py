"""
    数据交互: 处理Dataset数据集的数据
    自动通过所定义方式对数据集合进行保存处理并将提交信息传递给服务器
"""
import time
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict
from paho.mqtt import client as mqtt_client

from .dataset import Dataset, Data
from .utils.config import logger


class MQTTService:
    def __init__(self, config_data: Dict, dataset_list: List[Dataset]):
        """传入broker_info与根据data_list来进行上传

        Args:
            config_data: data所对应的broker信息
            dataset_list: 所需处理的MQTT类型的data对象列表

        """
        self._config_data = config_data

        user = self._config_data.get("user")
        assert user, "请重新下载wiseai-config.json文件"

        self.username = user.get("username")
        self.password = user.get("password")
        assert self.username or self.password, "请重新下载wiseai-config.json文件"

        self._dataset_list = dataset_list
        self._clients = {}
        self.stop = False
        self.sys_topic = f"/{self.username}/$SYS"

        self._create_client_depend_on_broker()
        self._register_to_sys()

    def create_mqtt_client(self, client_id: str, host: str, port: str):
        """创建client"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT Broker!")
            else:
                logger.info("Failed to connect, return code %d\n", rc)
        # Set Connecting Client ID
        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username=self.username, password=self.password)
        client.connect(host, port)
        client.loop_start()
        return client

    def _generate_topic_name(self, dataset_name: str, data_name: str):
        """生成主题名字"""
        return f'/{self.username}/{dataset_name}/{data_name}'

    def _choose_client(self):
        """默认选择第一个为订阅所使用的client"""
        return list(self._clients.values())[0]

    def _register_to_sys(self):
        """注册Data的Topic地址"""
        client = self._choose_client()
        register_data = []
        for ds in self._dataset_list:
            for data in ds.data_list:
                assert "/" not in data.name, "Data命名不能含有/"
                assert len(data.name) <= 50, "Data命名应少于50字符"
                # topic
                target_data_topic = self._generate_topic_name(ds.name, data.name)

                # extra_info
                extra_info_list = list()
                for ex in data.extra_info:
                    cur_extra_info = {
                        "name": ex.name,
                        "type": ex.type,
                        "value": ex.value
                    }
                    extra_info_list.append(cur_extra_info)
                register_data.append([target_data_topic, extra_info_list])

        msg = json.dumps({"data_list": register_data})
        client.publish(self.sys_topic, msg)
        logger.info(f"Registered Data number: {len(register_data)}")

    def _create_client_depend_on_broker(self):
        """根据broker数量创建client数量"""
        broker_info = []
        broker_dataset_map = {}  # 作为映射
        for index, ds in enumerate(self._dataset_list):
            dataset_name = ds.name
            # 存在不一样的broker则创建
            if ds.broker not in broker_info:
                broker_info.append(ds.broker)
                # 创建client
                client = self.create_mqtt_client(
                    f'Client_{self.username}_{index}', host=ds.broker[0], port=ds.broker[1])
                # 以index作为key来识别
                self._clients[dataset_name] = client

                broker_dataset_map[str(broker_info)] = dataset_name
            else:
                last_dataset_name = broker_dataset_map[str(broker_info)]
                # 存在同样的broker则赋值
                client = self._clients[last_dataset_name]
                self._clients[dataset_name] = client

    def scubscribe_sys(self, call_func):
        """订阅"""
        client = self._choose_client()

        def on_message(client, userdata, msg):
            # 调用回调函数
            call_func(msg)

        client.on_message = on_message
        client.subscribe(self.sys_topic)
        logger.info("Subscribed $SYS...")

    def publish_data(self):
        """根据topic信息进行推送

        :return:
        """

        for ds in self._dataset_list:
            cur_client = self._clients[ds.name]
            for data in ds.data_list:
                content = data.iter()
                # 有内容再上传
                if content:
                    # 生成data的topic地址：/Username/dataset/data.name，发布
                    target_data_topic = self._generate_topic_name(ds.name, data.name)
                    result = cur_client.publish(target_data_topic, str(content))
                    status = result[0]
                    if status == 0:
                        logger.info(f"Published {content} to Topic:{target_data_topic}")
                    else:
                        logger.info(f"Failed to send message to topic {target_data_topic}")

    def close(self):
        self.stop = True
        for _, client in self._clients:
            client.loop_stop(force=True)
        self._clients = {}


class Session:
    """
    abstractmethod:
        - commit() 提交数据集合
        - run() 推送数据集合
    """

    def __init__(self, config_path: str = "./wisemq-config.json"):
        self.config_path = config_path
        self._config_data = self._validate_config()
        self.dataset_list = self._validate_dataset()

        self._stop = False
        self.task_pool = ThreadPoolExecutor(5)

    def _validate_config(self):
        """读取配置文件"""
        with open(self.config_path, 'r') as f:
            context = f.read()
        try:
            data = json.loads(context)
            return data
        except:
            raise json.JSONDecodeError("请重新下载wisemq-config.json文件")

    def _validate_dataset(self):
        """校验dataset并添加到列表中"""
        dataset = self._config_data.get("dataset")
        assert dataset, "请重新下载wisemq-config.json文件"
        dataset_list = list()
        for ds in dataset:
            dataset = Dataset(name=ds["name"], broker=(ds["broker"]["host"], ds["broker"]["port"]))
            dataset_list.append(dataset)
        return dataset_list

    def commit(self, data: Data):
        """
        数据提交: 提交dataset与data的基本信息于服务器进行确认
        :return:
        """
        # 校验控制信息
        extra_info = data.extra_info
        for exinfo in extra_info:
            exinfo.validate()

        if len(self.dataset_list) > 1:
            # 验证data名称定义
            assert data.dataset_id, f"请设置{data.name}所属的数据集合"
        elif len(self.dataset_list) == 0:
            raise ValueError("数据集合不存在，请向管理员进行申请")
        # 匹配并添加数据智能体到数据集合,校验用户所设置的dataset是否存在
        if data.dataset_id not in [ds.name for ds in self.dataset_list]:
            raise KeyError(f'{data.name}的数据集合ID不存在，请确认配置文件信息是否匹配')

        for ds in self.dataset_list:
            if ds.name == data.dataset_id:
                ds.add(data)

    def process_sys_control(self, msg):
        """控制方法

        msg: ["status1"]

        """
        # 传递string
        content = json.loads(msg.payload.decode())
        for ds in self.dataset_list:
            # 智能体
            for data in ds.data_list:
                # 信息
                for ex in data.extra_info:
                    if content == ex.name:
                        ex.call_func()
                        break

    def _start_data_capture(self):
        """Start function capture in all Data."""
        for ds in self.dataset_list:
            for data in ds.data_list:
                self.task_pool.submit(data.capture_data)

    def run(self):
        logger.info("进入主程序...")
        self.mqtt_service = MQTTService(self._config_data, self.dataset_list)
        self.mqtt_service.scubscribe_sys(self.process_sys_control)
        logger.info("开启数据捕获...")
        self._start_data_capture()
        logger.info("开始上传数据...")

        while not self._stop:
            self.mqtt_service.publish_data()

    def close(self):
        self._stop = True
