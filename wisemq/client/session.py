"""
    数据交互: 处理Dataset数据集的数据
    自动通过所定义方式对数据集合进行保存处理并将提交信息传递给服务器
"""
import time
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict
from paho.mqtt import client as mqtt_client

from .agent import Data
from .config import logger


class MQTTService:
    def __init__(self, config_data: Dict, dataset: List[Data]):
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

        self._dataset = dataset
        self._clients = {}
        self.stop = False
        self.sys_topic = f"/{self.username}/$SYS"

        self._create_client_depend_on_broker()
        # self._register_to_sys()

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

    def _generate_topic_name(self, data_name: str):
        """生成主题名字"""
        return f'/{self.username}/{data_name}'

    def _choose_client(self):
        """默认选择第一个为订阅所使用的client"""
        return list(self._clients.values())[0]

    def _create_client_depend_on_broker(self):
        """根据broker数量创建client数量"""
        broker_info = []
        broker_dataset_map = {}  # 作为映射
        for index, data in enumerate(self._dataset):
            data_id = data.id
            # 存在不一样的broker则创建
            if data.broker not in broker_info:
                broker_info.append(data.broker)
                # 创建client
                client = self.create_mqtt_client(
                    f'Client_{self.username}_{index}', host=data.broker[0], port=data.broker[1])
                # 以index作为key来识别
                self._clients[data_id] = client

                broker_dataset_map[str(broker_info)] = data_id
            else:
                last_dataset_name = broker_dataset_map[str(broker_info)]
                # 存在同样的broker则赋值
                client = self._clients[last_dataset_name]
                self._clients[data_id] = client

    def publish_data(self):
        """根据topic信息进行推送

        :return:
        """

        for data in self._dataset:
            cur_client = self._clients[data.id]
            content = data.iter()
            # 有内容再上传
            if content:
                # 生成data的topic地址：/Username/dataset/data.name，发布
                target_data_topic = self._generate_topic_name(data.id)
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
        # 配置文件
        self._config_data = self._validate_config()
        # dataset
        self.brokers = self._validate_broker()
        self.dataset = list()
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

    def _validate_broker(self):
        """校验dataset并添加到列表中"""
        dataset = self._config_data.get("dataset")
        assert dataset, "请重新下载wisemq-config.json文件"
        data_dict = dict()

        for ds in dataset:
            data_dict[ds["name"]] = (ds["broker"]["host"], ds["broker"]["port"])
        return data_dict

    def commit(self, data: Data):
        """
        数据提交: 提交dataset与data的基本信息于服务器进行确认
        :return:
        """
        # 校验控制信息
        extra_info = data.extra_info
        for exinfo in extra_info:
            exinfo.validate()
        # 1. 校验data的ID是否存在
        data_id = data.id
        if data_id not in self.brokers:
            raise KeyError(f"数据智能体 {data_id} 不存在")
        
        # 2. 添加broker信息
        data.broker = self.brokers[data_id]
        # 3. 添加进列表
        self.dataset.append(data)


    def process_sys_control(self, msg):
        """控制方法

        msg: ["status1"]

        """
        # 传递string
        content = json.loads(msg.payload.decode())
        for data in self.dataset:
            # 智能体
            # 信息
            for ex in data.extra_info:
                if content == ex.name:
                    ex.call_func()
                    break

    def _start_data_capture(self):
        """Start function capture in all Data."""
        for data in self.dataset:
            self.task_pool.submit(data.capture_data)

    def run(self):
        logger.info("进入主程序...")
        self.mqtt_service = MQTTService(self._config_data, self.dataset)
        # self.mqtt_service.scubscribe_sys(self.process_sys_control)
        logger.info("开启数据捕获...")
        self._start_data_capture()
        logger.info("开始上传数据...")

        while not self._stop:
            self.mqtt_service.publish_data()

    def close(self):
        self._stop = True
