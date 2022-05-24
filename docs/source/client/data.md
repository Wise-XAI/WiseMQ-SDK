数据智能体
=============

### 智能体的定义
初始化智能体的时候需指明对应ID，便于网站对不同ID进行特定分类以及确定显示位置。
ID可查看配置文件或是在网站中进行查看

智能体中有两个参数是用户可进行操作的，第一个是`statuses`，对应到智能体的状态列表；第二个是`candidate_queue`，对应为数据上传队列。
用户继承Data类对`capture_data`方法进行重写，其中需为循环堵塞捕获数据。

```python
from wisemq.client import Data
class MyData(Data):
    def capture_data(self):
        while True:
            try:
                data = get_data()  # 这里的get_data为用户自定义的方法
                self.candidate_queue.put(data)
            except Exception as e:
                print(e)
```

### 智能体的状态
智能体的状态由`Status`类负责，其中包含`ONLY_SHOW`和`SWITCH`两种类型，前者仅支持数值的显示，后者为开关类型，用于调用客户端中用户自定义的回调函数。

```python
from wisemq.client import Data, Status

def call_func_for_status_3():
    print("Process for status 3...")


def call_func_for_status_4():
    print("Process for status 4...")

class MyData(Data):
    # 定义当前智能体状态
    statuses = {
        "status1": Status(value="test 1"),  # status1: 仅显示数值
        "status2": Status(value="test 2"),  # status2: 仅显示数值
        "status3": Status(Status.SWITCH, value=0, call_func=call_func_for_status_3),  # status3: 开关类型，用户可通过界面控制客户端，处理回调函数为call_func_for_status_3
        "status4": Status(Status.SWITCH, value=1, call_func=call_func_for_status_4),  # status4: 开关类型，用户可通过界面控制客户端，处理回调函数为call_func_for_status_4
    }

    def capture_data(self):
        while True:
            try:
                # 捕获数据
                data = get_data()  # 这里的get_data为用户自定义的方法
                self.candidate_queue.put(data)
                # 更新状态
                self.set_status("status1", "update status1")  # 更新status1数值为"update status1"
                self.set_status("status2", "update status2"))  # 更新status2数值为"update status2"
                self.set_status("status3", 1))  # 更新status3为1
                self.set_status("status3", 0))  # 更新status4为1
            except Exception as e:
                print(e)
```

### 智能体的实例化与提交
智能体实例化的时候需要传入用户在网站所申请Data的ID进行实例化，对应ID将被用于更多的分类展示或分类处理。
实例化后需要提交到会话，由会话负责维护接下来的数据上传与状态更新。

```python
my_data = MyData(id="{{ Your Data ID}}")
session.commit(my_data)
```

