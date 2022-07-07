import time
import datetime
# dev
import sys
sys.path.append('/home/dongbox/work/WiseMQ-SDK/')

from wisemq.client import Status, MQTTAgent
from queue import Full

def call_func_for_status_2(data):
    print(f"Processing for status 3...: 当前接受到参数： {data}.")
    print("Process for status 2...")
    time.sleep(1)


cur_status = "online"

def call_func_for_status_3(data):
    global cur_status
    print(data)
    if data == "reload_lastest":
        print("执行上一个")
        cur_status = "process"
    elif data != "pause":
        # cur_status = "download"
        print("接收到SIGNAL指令")
        print(f"Processing for status 3...: 当前请求地址为： {data}.")
        print("保存为状态记录")
        time.sleep(5)
        cur_status = "failed"
        
        # cur_status = "process"
    else:
        cur_status = "online"



class MyMQTTAgent(MQTTAgent):
    OFFLINE_TIME_STATUS = Status(10)

    # 初始化状态参数
    statuses = {
        "current_feedback": Status(value="online"), 
        "status2": Status(value=0, type=Status.SWITCH, call_func=call_func_for_status_2), 
        "current_schedule": Status(value="http://我是请求地址.com", type=Status.SIGNAL, call_func=call_func_for_status_3), 
    }

    def capture_data(self):
        while True:
            try:
                data = {
                    "name": "test",
                    "data1": "GOOD",
                    "data2": "NOT BAD",
                    "updated_date": str(datetime.datetime.now())
                }
                if cur_status == "download":
                    self.set_status("current_feedback", "downloading")
                elif cur_status == "online":
                    self.set_status("current_feedback", "online")
                elif cur_status == "process":
                    self.set_status("current_feedback", "processing")
                elif cur_status == "failed":
                    self.set_status("current_feedback", "failed")

                print(cur_status)
                self.candidate_queue.put_nowait(data)
                time.sleep(.1)  # 0.5s获取数据

            except Full:
                time.sleep(.2)  # 0.5s获取数据

# 创建
my_agent = MyMQTTAgent()
my_agent.run()
