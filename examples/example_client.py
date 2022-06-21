import time

from wisemq.client import Session
from wisemq.client import Data, Status
import datetime

def call_func_for_status_2():
    print("Process for status 2...")
    time.sleep(1)


def call_func_for_status_3(data):
    print("接收到SIGNAL指令")
    print(f"Processing for status 3...: 当前请求地址为： {data}.")
    print("保存为状态记录")
    time.sleep(1)


class TData(Data):
    # 初始化状态参数
    statuses = {
        "status1": Status(value="test"), 
        "status2": Status(Status.SWITCH, value=0, call_func=call_func_for_status_2), 
        "current_schedule": Status(Status.SIGNAL, value="http://我是请求地址.com", call_func=call_func_for_status_3), 
    }

    def capture_data(self):
        number = 323
        while True:
            try:
                number += 1
                data = {
                    "name": "test",
                    "data1": "GOOD",
                    "data2": "NOT BAD",
                    "updated_date": str(datetime.datetime.now())
                }
                self.candidate_queue.put(data)
                self.set_status("status1", str(number))
                time.sleep(5)  # 0.5s获取数据
            except Exception as e:
                print(e)
                raise e
# 创建
data1 = TData(id="162bcc2d0f6340c5938535071d3645ab")
# data2 = TData(id="fa2052d7c67f48958977e65b1bca1770")

session1 = Session("/home/dongbox/work/wisemq_sdk/wisemq-config.json")
session1.commit(data1)
# session1.commit(data2)
session1.run()
