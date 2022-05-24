快速开始
=============
快速开始中创建了一个最简单的智能体。
```python

from wisemq.client import Session, Data

# 继承Data实现capture_data方法用于捕获数据
class MyData(Data):
    def capture_data(self):
        while True:
            ...
            self.candidate_queue.put(data)
                
# 实例化
my_data = MyData(id="{{ Your Data ID}}")

# 实例化一个会话
session1 = Session()
# 提交所要上传数据的智能体
session1.commit(my_data)
# 开启会话
session1.run()

```


