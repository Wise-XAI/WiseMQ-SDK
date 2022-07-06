import time
import datetime
# dev
import sys
sys.path.append('/home/dongbox/work/WiseMQ-SDK/')

from wisemq.client import Status, MQTTAgent


def call_func_for_status_2(data):
    print(f"Processing for status 3...: 当前接受到参数： {data}.")
    print("Process for status 2...")
    time.sleep(1)


def call_func_for_status_3(data):
    print("接收到SIGNAL指令")
    print(f"Processing for status 3...: 当前请求地址为： {data}.")
    print("保存为状态记录")
    time.sleep(1)


class MyMQTTAgent(MQTTAgent):
    # 初始化状态参数
    statuses = {
        "status1": Status(value="test"), 
        "status2": Status(Status.SWITCH, value=0, call_func=call_func_for_status_2), 
        "current_schedule": Status(Status.SIGNAL, value="http://我是请求地址.com", call_func=call_func_for_status_3), 
    }

    def capture_data(self):
        number = 1
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
my_agent = MyMQTTAgent()
my_agent.run()
