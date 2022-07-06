import time
from . base import Agent, Status
import json
from .. config import logger
from .. connectors import MQTTConnector

class MQTTAgent(Agent):
    def __init__(self, config_path="./wisemq-config.json", queue_size: int = 100):
        super().__init__(config_path, queue_size)

    def process_sys_control(self, msg):
        """控制方法

        msg: {"agent":(name, value)}
        """
        try:
            update_status = json.loads(msg)
            for data_id, update_status in update_status.items():
                update_status_name = update_status[0]
                update_status_value = update_status[1]
                # 只能对SWITCH产生作用
                if self.id != data_id:
                    continue
                # 更新状态
                for status_name, status_obj in self.statuses.items():
                    # 查询
                    if update_status_name == status_name and (status_obj.type == Status.SWITCH or status_obj.type == Status.SIGNAL):
                        # 切换
                        status_obj.value = update_status_value
                        # 调用回调函数
                        if status_obj.type == Status.SIGNAL:
                            status_obj.call_func(update_status_value)
                        else:
                            status_obj.call_func(update_status_value)
                        return True
        except Exception as e:
            logger.info(f"SYSTEM CONTROL ERROR: {e}")
            print(e)

    def run(self):
        logger.info("进入主程序...")
        # 用户名默认与密码一致
        self.mqtt_connector = MQTTConnector(
            username=self._config_data["user"], 
            password=self._config_data["user"], 
            host=self._brokers["host"], 
            port=self._brokers["port"]
            )
        # 设置客户端的订阅地址
        self.mqtt_connector.scubscribe_sys(self.process_sys_control)
        logger.info("开启Agent的数据捕获...")
        self._start_data_capture()

        logger.info("开始上传Agent数据...")
        while not self._stop:
            msg = self.iter()
            status_serailizer = self.get_status_serailize()
            if msg:
                self.mqtt_connector.publish_data(self.id, msg, status_serailizer)
            else:
                time.sleep(0.1)

        logger.info("中止Agent运行")
        