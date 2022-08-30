"""
    数据交互: 处理Dataset数据集的数据
    自动通过所定义方式对数据集合进行保存处理并将提交信息传递给服务器
"""
import json
import time
from paho.mqtt import client as mqtt_client

from .config import logger



RESULT_CODES = {
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
}

def get_random_str():
    import uuid
    return str(uuid.uuid4()).replace("-", "")

class MQTTConnector:
    def __init__(self, username:str=None, password: str=None, host="localhost", port=1883):
        """使用MQTT进行数据传输

        Args:

        """
        random_str = get_random_str()
        client_id = f'Client_{username}-{random_str}' if username else f'MQTT_CLIENT_FOR_TEST'
        self._client = mqtt_client.Client(client_id)

        self.__host = host
        self.__port = port
        self._client.username_pw_set(username, password)
        # self._client = self.create_mqtt_client(client_id, host, port)
        self.sys_topic = f"/wisemq/v1/{username}/$SYS"
        self.username = username
        self._client.on_connect = self._on_connect
        self._client.on_log = self._on_log
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        
        self.__is_connected = False
        self.stopped = False

        self.connect()

    def _on_log(self, client, userdata, level, buf):
        #     if isinstance(buf, Exception):
        #         log.exception(buf)
        #     else:
        #         log.debug("%s - %s - %s - %s", client, userdata, level, buf)
        pass

    def _on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        logger.info("Received data from WISEMQ: %s" % decoded_payload)
        self.agent_callback_func(decoded_payload)
        # self.disconnect()

    def _on_publish(self, client, userdata, result):
        pass

    def _on_disconnect(self, client, userdata, result_code):
        prev_level = logger.level
        logger.setLevel("DEBUG")
        logger.debug("Disconnected client: %s, user data: %s, result code: %s", str(client), str(userdata),
                  str(result_code))
        logger.setLevel(prev_level)

    def _on_connect(self, client, userdata, flags, result_code, *extra_params):
        if self.__connect_callback:
            time.sleep(.05)
            self.__connect_callback(self, userdata, flags, result_code, *extra_params)
        if result_code == 0:
            self.__is_connected = True
            logger.info("connection SUCCESS")
        else:
            if result_code in RESULT_CODES:
                logger.error("connection FAIL with error %s %s", result_code, RESULT_CODES[result_code])
            else:
                logger.error("connection FAIL with unknown error")

    def reconnect_delay_set(self, min_delay=1, max_delay=120):
        """The client will automatically retry connection. Between each attempt it will wait a number of seconds
         between min_delay and max_delay. When the connection is lost, initially the reconnection attempt is delayed
         of min_delay seconds. It’s doubled between subsequent attempt up to max_delay. The delay is reset to min_delay
          when the connection complete (e.g. the CONNACK is received, not just the TCP connection is established)."""
        self._client.reconnect_delay_set(min_delay, max_delay)

    def is_connected(self):
        return self.__is_connected

    def connect(self, callback=None, min_reconnect_delay=1, timeout=120, keepalive=120):
        self._client.connect(self.__host, self.__port, keepalive=keepalive)
        self.reconnect_delay_set(min_reconnect_delay, timeout)
        self._client.loop_start()
        self.__connect_callback = callback
        self.reconnect_delay_set(min_reconnect_delay, timeout)
        while not self.__is_connected and not self.stopped:
            logger.info("Trying to connect to %s...", self.__host)
            time.sleep(1)

    def disconnect(self):
        self._client.disconnect()
        logger.debug(self._client)
        logger.debug("Disconnecting from WISEMQ")
        self.__is_connected = False
        self._client.loop_stop()

    def scubscribe_sys(self, call_func):
        """订阅系统消息"""
        self.agent_callback_func = call_func
        self._client.subscribe(self.sys_topic)
        # print("system: ", self.sys_topic)
        logger.info("Subscribed $SYS...")

    def _generate_agent_data_topic_name(self):
        """生成主题名字"""
        return '/wisemq/v1/data'

    def _generate_agent_status_topic_name(self):
        """生成Agent的状态主题"""
        return '/wisemq/v1/status'

    def _generate_agent_key(self, content):
        """添加agent_key"""
        content["wisemq_agent_key"] = self.username
        return json.dumps(content)
           
    def publish_data(self, msg: dict, statuses: dict):
        """根据topic信息进行推送

        :return:
        """
        if msg:
            target_agent_topic = self._generate_agent_data_topic_name()
            result = self._client.publish(target_agent_topic, self._generate_agent_key(msg))
            status = result[0]
            if status == 0:
                logger.info(f"Published content to Topic:{target_agent_topic}")
            else:
                logger.info(f"Failed to send message to topic {target_agent_topic}")
            # print(target_agent_topic)
        # 正常上传状态信息
        target_agent_sys_topic = self._generate_agent_status_topic_name()
        # print(target_agent_sys_topic)
        result = self._client.publish(target_agent_sys_topic, self._generate_agent_key(statuses))
        status = result[0]
        if status == 0:
            logger.info(f"Published status to Topic:{target_agent_sys_topic}")
        else:
            logger.info(f"Failed to send message to topic {target_agent_sys_topic}")
        time.sleep(0.5)

    def close(self):
        self._client.loop_stop(force=True)
        self._client = None



