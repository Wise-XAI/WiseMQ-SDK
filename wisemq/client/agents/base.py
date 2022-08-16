"""
数据统一格式
- class Agent
"""
import abc
import json
from queue import Queue, Empty
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

class Status:
    """控制方法"""
    SWITCH = "switch"
    ONLY_SHOW = "only_show"
    SIGNAL = "signal"
    
    def __init__(self, value=0, type=None, call_func=None):
        self._type = type or self.ONLY_SHOW
        self._value = value  # show的时候为string格式，switch的时候则为0、1，signal时为特定值并提供控制
        if not call_func:
            self._call_func = lambda : None
        else:
            self._call_func = call_func

    def is_switch(self):
        self._type = self.SWITCH
    
    def is_show(self):
        self._type = self.ONLY_SHOW

    @property
    def type(self):
        return self._type
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        # 开关类型
        if self._type == self.SWITCH and v not in [0, 1]:
            raise ValueError("value格式错误!, 程序中止！！！")
        # 显示类型
        if self._type == self.ONLY_SHOW and not isinstance(v, str):
            raise ValueError("value格式错误!, 程序中止！！！")
        self._value = v

    @property
    def call_func(self):
        return self._call_func

    @call_func.setter
    def call_func(self, v):
        self._call_func = v

    def validate(self):
        """定义当前Status的状态校验方法"""
        assert self._type == self.ONLY_SHOW or self._type == self.SWITCH or self._type == self.SIGNAL, f"{self.name}中类型设置错误"
        if self._type == self.SWITCH: 
            assert self._value == 0 or self._value == 1, f"智能体类型为SWITCH时, value必须为0 | 1"
            assert self._call_func, f"智能体类型为SWITCH时, 必须设置回调函数进行相应操作"
        return True
        

class Agent:
    """
        Agent的基本单位
        其中需要定义获取方法以及其基本信息
    """
    _repr_indent = 4
    statuses: Dict[str, Status] = dict()



    def __init__(self, config_path, queue_size: int = 100):
        self.config_path = config_path
        # 配置文件
        self._config_data = self._validate_config()
        self._id = self._config_data.get("agent")
        self._brokers = self._validate_broker()

        self.candidate_queue = Queue(maxsize=queue_size)  # 排队等待上传队列
        self.step = 0  # 记录执行步骤
        self._stop = False
        self.task_pool = ThreadPoolExecutor(5)

    # -----------------字符输出函数-----------------

    def extra_repr(self) -> str:
        return ""

    def __repr__(self) -> str:
        head = "Data " + self.name
        body = self.extra_repr().splitlines()
        lines = [head] + [" " * self._repr_indent + line for line in body]
        return "\n".join(lines)

    def _validate_config(self):
        """读取配置文件，确认配置文件地址存在否则抛出异常"""
        try:
            with open(self.config_path, 'r') as f:
                context = f.read()
        except FileNotFoundError:
            raise FileNotFoundError("查询不到配置文件，请申请并下载wisemq-config.json文件!!!")

        try:
            data = json.loads(context)
            return data
        except:
            raise json.JSONDecodeError("格式错误，请重新下载wisemq-config.json文件!!!")

    def _validate_broker(self):
        """校验data并添加其中的broker到字典中"""
        broker = self._config_data.get("broker")
        assert broker, "格式错误，请重新下载wisemq-config.json文件!!!"
        broker_dict = {
            "host": broker["host"], 
            "port": broker["port"]
        }
        return broker_dict

    @property
    def id(self) -> str:
        return self._id
        
    @abc.abstractmethod
    def capture_data(self):
        """
            数据捕获自定义方法，需要将所捕获的数据放置到candidate_queue队列中等待上传
        :return:
        """
        # self.candidate_queue.put()

    def iter(self):
        """获取数据

        :return: Item or False
        """
        self.step += 1
        try:
            item = self.candidate_queue.get_nowait()
            return item
        except Empty:
            return False

    def set_status(self, name, value):
        """更新Data的状态
        
        Args:
            - name: 状态名称
            - value: 更新的值
        """
        for status_name, status_obj in self.statuses.items():
            if name == status_name:
                status_obj.value = value
                return True

        raise KeyError(f"Status {name} 不存在")

    def get_status_serailize(self):
        """获取Data状态的序列化"""
        serialize_data = {}
        for status_name, status_obj in self.statuses.items():
            serialize_data[status_name] = {
                "value": status_obj.value,
                "type": status_obj.type
            }
        return serialize_data


    def _start_data_capture(self):
        """Start function capture in all Data."""
        self.task_pool.submit(self.capture_data)

    @abc.abstractmethod
    def run(self):
        """主函数"""

    def close(self):
        self._stop = True