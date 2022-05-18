import time

from wisemq.client import Session
from wisemq.client import Data, SingleExtroInfo


def call_func_for_status_3():
    print("Process for status 3...")
    time.sleep(1)


def call_func_for_status_4():
    print("Process for status 4...")
    time.sleep(1)


class TData(Data):
    """自动生成data的新topic"""
    extra_info = (
        SingleExtroInfo("status1", value="test"), 
        SingleExtroInfo("status2", value="only test"), 
        SingleExtroInfo("status3", SingleExtroInfo.SWITCH, value=0, call_func=call_func_for_status_3),
        SingleExtroInfo("status4", SingleExtroInfo.SWITCH, value=1, call_func=call_func_for_status_4),
        )

    def capture_data(self):
        while True:
            data = {
                "name": "test",
                "data1": "111111",
                "data2": "NOT BAD",
            }
            self.candidate_queue.put(data)
            time.sleep(0.5)  # 0.5s获取数据

# 创建
data1 = TData(id="45448b3d5fa34aab9711ac806ed131f0")
data2 = TData(id="fa2052d7c67f48958977e65b1bca1770")

session1 = Session("/home/dongbox/work/wisemq_sdk/wisemq-config.json")
session1.commit(data1)
session1.commit(data2)
session1.run()
