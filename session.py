"""
    数据交互: 处理Dataset数据集的数据
    自动通过所定义方式对数据集合进行保存处理并将提交信息传递给服务器
"""
import time
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List
from paho.mqtt import client as mqtt_client

from dataset import Dataset, Data

from utils.config import logger
import json


class MQTTService:
    def __init__(self, config_data, dataset_list: List[Dataset]):
        """
            传入broker_info与根据data_list来进行上传
            config_data: data所对应的broker信息
            dataset_list: 所需处理的MQTT类型的data对象列表
        :param data_list:
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
        self.sys_topic = f"{self.username}/$SYS"

        self._create_client_depend_on_broker()
        self._register_to_sys()

    def create_mqtt_client(self, client_id, host, port):
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

    def _register_to_sys(self):
        """注册Data的Topic地址"""
        client = list(self._clients.values())[0]
        register_data = []
        for ds in self._dataset_list:
            for data in ds.data_list:
                assert "/" not in data.name, "Data命名不能含有/" 
                assert len(data.name) <= 50, "Data命名应少于50字符" 
                # topic
                target_data_topic = f'{self.username}/{ds.name}/{data.name}'
                
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

        client.publish(self.sys_topic, json.dumps({"data_list": register_data}))
        logger.info(f"Registered Data number: {len(register_data)}")

    def _create_client_depend_on_broker(self):
        """根据broker数量床架client数量"""
        broker_info = []
        broker_dataset_map = {}  # 作为映射
        for index, ds in enumerate(self._dataset_list):
            dataset_name = ds.name
            # 存在不一样的broker则创建
            if ds.broker not in broker_info:
                broker_info.append(ds.broker)
                # 创建client
                client = self.create_mqtt_client(f'Client_{self.username}_{index}', host=ds.broker[0], port=ds.broker[1])
                # 以index作为key来识别
                self._clients[dataset_name] = client

                broker_dataset_map[str(broker_info)] = dataset_name
            else:
                last_dataset_name = broker_dataset_map[str(broker_info)]
                # 存在同样的broker则赋值
                client = self._clients[last_dataset_name]
                self._clients[dataset_name] = client

    def choose_client(self):
        return list(self._clients.values())[0]

    def scubscribe_sys(self, call_func):
        """订阅"""
        client = self.choose_client()
        def on_message(client, userdata, msg):
            # 调用回调函数
            call_func(msg)

        client.subscribe(self.sys_topic)
        logger.info("Subscribed $SYS...")
        client.on_message = on_message

    def publish_data(self):
        """
            根据topic信息进行推送
        :param topic_dict:
        :return:
        """
        # 生成data的topic地址：Username/dataset/data.name，发布
        for ds in self._dataset_list:
            cur_client = self._clients[ds.name]
            for data in ds.data_list:
                target_data_topic = f'{self.username}/{ds.name}/{data.name}'
                content = data.iter()
                result = cur_client.publish(target_data_topic, str(content))
                status = result[0]
                if status == 0:
                    logger.info(f"Published {content} to Topic:{target_data_topic}")
                else:
                    logger.info(f"Failed to send message to topic {target_data_topic}")


    def run(self):
        """
        - 数据持续性推送
        """
        try:
            # 之后改为异步
            self.create_client_depend_on_broker()
            self.stop = False

            while not self.stop:
                self.publish_data()
                time.sleep(5)
        except Exception:
            raise

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

    def __init__(self):
        self._config_data = self._validate_config()
        self.dataset_list = self._validate_dataset()

        self._stop = False
        self.task_pool = ThreadPoolExecutor(3)

    def _validate_config(self):
        """读取配置文件"""
        file_path = "./wiseai-config.json"
        with open(file_path, 'r') as f:
            context = f.read()
        try:
            data = json.loads(context)
            return data
        except:
            raise json.JSONDecodeError("请重新下载wiseai-config.json文件")

    def _validate_dataset(self):
        """校验dataset并添加到列表中"""
        dataset = self._config_data.get("dataset")
        assert dataset, "请重新下载wiseai-config.json文件"
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

        # 匹配并添加数据智能体到数据集合
        for ds in self.dataset_list: 
            if ds.name == data.dataset_id:
                ds.add(data)


    def process_sys_control(self, msg):
        """控制方法
        msg: ["status1"]
        """
        # 传递string
        content = json.loads(msg.payload.decode())
        print(content)
        for ds in self.dataset_list:
            # 智能体
            for data in ds.data_list:
                # 信息
                for ex in data.extra_info:
                    print(ex.name)
                    if content == ex.name:
                        print(ex.name)
                        ex.call_func()
                        break


    def run(self):
        self.mqtt_service = MQTTService(self._config_data, self.dataset_list)
        # self.task_pool.submit(, self.process_sys_control)
        # 然后将run方法放入线程执行
        self.mqtt_service.scubscribe_sys(self.process_sys_control)
        logger.info("进入主程序...")
        # self.mqtt_service.run()
        while not self._stop:
            time.sleep(1)
            self.mqtt_service.publish_data()

    def close(self):
        self._stop = True
