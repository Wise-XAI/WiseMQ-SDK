
### 用法介绍
#### 上传文件类型的Data，使用例子如下所示：
```python
import time
from session import Session
from dataset import Dataset, Data

class TData(Data):
    # 继承Data，对其中的capture_data方法进行重写，定义一个while循环保持文件的上传
    def capture_data(self):
        while True:
            file_path = ""  # update this path in this loop
            self.candidate_queue.put(file_path)
            time.sleep(5)

# 定于额外状态的显示，格式为: List[Dict["name", "value"]]
def get_extra_info():
    return [{"name": "status1", "value": 0}, {"name": "status2", "value": 1}]

# 定义data1实现文件上传
data1 = TData(name="data1", description="A data demo in example")
# 定义dataset1维
dataset1 = Dataset(name="dataset1", description="A dataset demo in example")
# 添加data
dataset1.add(data1)
# 定义session1启动程序
session1 = Session(username="yourusername", password="yourpassword")
# 更新heartbeat的额外信息获取方法
session1.heartbeat.update_extra_info(get_extra_info)
# 提交数据用于服务器核验
session1.commit(dataset1)
# 启动
session1.run()
```