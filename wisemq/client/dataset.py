"""
数据统一格式
- class Data
- class Dataset
"""
import abc
from queue import PriorityQueue, Empty
from typing import List


class SingleExtroInfo:
    """控制方法"""
    SWITCH = "switch"
    ONLY_SHOW = "only_show"

    def __init__(self, name, type=None, value=0, call_func=None):
        self.name = name
        self._type = type or self.ONLY_SHOW
        self._value = value  # show的时候为string格式，switch的时候则为0、1
        self._call_func = call_func

    def is_switch(self):
        self._type = self.SWITCH
    
    def is_show(self):
        self._type = self.ONLY_SHOW
    
    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    @value.setter
    def value(self, v):
        assert v == 0 or v == 1 or isinstance(v, str), "value格式错误!" 
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
            assert self._value == 0 or self._value == 1, f"{self.name}中类型为SWITCH时, value必须为0 | 1"
            assert self._call_func, f"{self.name}中类型为SWITCH时, 必须设置回调函数进行相应操作"
        return True
        

class Data:
    """
        数据的基本单位
        其中需要定义获取方法以及其基本信息
        name: 唯一识别符
    """

    extra_info = set()

    def __init__(self, name: str,
                 queue_size: int = 100,
                 ):
        self.name = name
        # self.hidden = False
        self.candidate_queue = PriorityQueue(maxsize=queue_size)  # 排队等待上传队列
        self.step = 0  # 记录执行步骤
        self.dataset_id = None

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

    def set_dataset_id(self, id):
        """设置Data所属的Dataset"""
        self.dataset_id = id


class Dataset:
    """
    通用数据集合
    name: 唯一识别符
    broker: 节点
    data_list: 数据集合
    """
    _repr_indent = 4

    def __init__(self, name: str, broker=(None, None)) -> None:
        self._name = name.lower()
        self._broker = broker
        self.data_list: List[Data] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def broker(self) -> str:
        return self._broker

    def add(self, data: Data):
        """
        添加data到数据集合
        """
        if self.check(data):
            self.data_list.append(data)
        else:
            raise ValueError("Data has existed.\n"
                             "Please check the data's name and ensure not repeat!!")

    def check(self, data: Data):
        """
        检查data名称是否对应
        """
        for di in self.data_list:
            if di.name == data.name:
                return False
        return True

    # -----------------字符输出函数-----------------
    def __len__(self) -> int:
        return len(self.data_list)

    def extra_repr(self) -> str:
        return ""

    def __repr__(self) -> str:
        head = "Dataset " + self.name
        body = [f"Number of data: {self.__len__()}, {[di.name for di in self.data_list]}"]
        body += self.extra_repr().splitlines()
        lines = [head] + [" " * self._repr_indent + line for line in body]
        return "\n".join(lines)

