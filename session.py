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
        self.create_client_depend_on_broker()
    

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


    def create_client_depend_on_broker(self):
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
                time.sleep(1)
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
        extro_info = data.extro_info
        for exinfo in extro_info:
            exinfo.validate()
        
        if len(self.dataset_list) > 1:
            # 验证data名称定义
            assert data.dataset_id, f"请设置{data.name}所属的数据集合"

        # 匹配并添加数据智能体到数据集合
        for ds in self.dataset_list: 
            if ds.name == data.dataset_id:
                ds.add(data)


    def run(self):
        self.mqtt_service = MQTTService(self._config_data, self.dataset_list)
        # self.task_pool.submit(self.mqtt_service.run)
        # 然后将run方法放入线程执行
        logger.info("进入主程序...")
        # self.mqtt_service.run()
        while not self._stop:
            time.sleep(1)
            self.mqtt_service.publish_data()

    def close(self):
        self._stop = True
