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
            self.candidate_queue.put(r"TESTSSSSSSSSSSSS!!!")
            time.sleep(5)

    def iter(self):
        time.sleep(1)
        return "TESTSSSSSSSSSSSS!!!"
# 创建
data1 = TData(name="data1")

data1.set_dataset_id(id="968722f9da9a42cc8acc0c6c5607755e") 

session1 = Session()
session1.commit(data1)
session1.run()
