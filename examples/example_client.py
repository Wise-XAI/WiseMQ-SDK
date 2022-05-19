import time

from wisemq.client import Session
from wisemq.client import Data, Status


def call_func_for_status_3():
    print("Process for status 3...")
    time.sleep(1)


def call_func_for_status_4():
    print("Process for status 4...")
    time.sleep(1)


class TData(Data):
    # 初始化状态参数
    statuses = {
        "status1": Status(value="test"), 
        "status2": Status(value="only test"), 
        "status3": Status(Status.SWITCH, value=0, call_func=call_func_for_status_3), 
        "status4": Status(Status.SWITCH, value=1, call_func=call_func_for_status_4), 
    }

    def capture_data(self):
        number = 0
        while True:
            try:
                number += 1
                data = {
                    "name": "test",
                    "data1": "111111",
                    "data2": "NOT BAD",
                }
                self.candidate_queue.put(data)
                self.set_status("status1", str(number))
                time.sleep(5)  # 0.5s获取数据
            except Exception as e:
                print(e)
                raise e
# 创建      
data1 = TData(id="fc2acc09a52a43fca34fc5a45ad195fe")
# data2 = TData(id="fa2052d7c67f48958977e65b1bca1770")

session1 = Session("/home/dongbox/work/wisemq_sdk/wisemq-config.json")
session1.commit(data1)
# session1.commit(data2)
session1.run()
