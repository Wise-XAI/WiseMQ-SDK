"""
数据统一格式
- class Data
- class Dataset
"""
import abc
from queue import PriorityQueue, Empty
from typing import List, Dict


class Status:
    """控制方法"""
    SWITCH = "switch"
    ONLY_SHOW = "only_show"

    def __init__(self, type=None, value=0, call_func=None):
        self._type = type or self.ONLY_SHOW
        self._value = value  # show的时候为string格式，switch的时候则为0、1
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
        if self._type == self.SWITCH:
            assert v == 0 or v == 1
        # 显示类型
        if self._type == self.ONLY_SHOW:
            assert isinstance(v, str), "value格式错误!" 
        self._value = v

    @property
    def call_func(self):
        return self._call_func

    @call_func.setter
    def call_func(self, v):
        self._call_func = v

    def validate(self):
        # 类型
        assert self._type == self.ONLY_SHOW or self._type == self.SWITCH, f"{self.name}中类型设置错误"
        if self._type == self.SWITCH: 
            assert self._value == 0 or self._value == 1, f"智能体类型为SWITCH时, value必须为0 | 1"
            assert self._call_func, f"智能体类型为SWITCH时, 必须设置回调函数进行相应操作"
        return True
        

class Data:
    """
        数据的基本单位
        其中需要定义获取方法以及其基本信息
    """
    _repr_indent = 4
    statuses: Dict[str, Status] = dict()

    def __init__(self, id: str, queue_size: int = 100):
        self._id = id
        self._broker = None
        # self.hidden = False
        self.candidate_queue = PriorityQueue(maxsize=queue_size)  # 排队等待上传队列
        self.step = 0  # 记录执行步骤

    @property
    def id(self) -> str:
        return self._id

    @property
    def broker(self) -> str:
        return self._broker

    @broker.setter
    def broker(self, value):
        self._broker = value
        
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
            if name == status_name and status_obj.type == Status.SWITCH:
                status_obj.value = value
                return 
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
    # -----------------字符输出函数-----------------

    def extra_repr(self) -> str:
        return ""

    def __repr__(self) -> str:
        head = "Data " + self.name
        body = self.extra_repr().splitlines()
        lines = [head] + [" " * self._repr_indent + line for line in body]
        return "\n".join(lines)