import time
import datetime
import logging
# dev
import sys
sys.path.append('/home/dongbox/work/WiseMQ-SDK/')

from wisemq.client import Status, MQTTAgent
from queue import Full

logger = logging.getLogger("[CLIENT]")
# logger.setLevel(level=logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
#                     level=logging.DEBUG,
#                     filename='output.log',
#                     filemode='w')

file_handler = logging.FileHandler('worker.log')
file_handler.setLevel(level=logging.DEBUG)
# file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
file_handler.setLevel(level=logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)




def call_func_for_status_2(data):
    logger.info(f"Processing for status 3...: 当前接受到参数： {data}.")
    logger.info("Process for status 2...")
    time.sleep(1)


cur_status = "online"

def call_func_for_status_3(data):
    global cur_status
    # print(data)
    if data == "reload_lastest":
        logger.info("执行上一个")
        cur_status = "process"
    elif data != "pause":
        # cur_status = "download"
        logger.info("接收到SIGNAL指令")
        logger.info(f"Processing for status 3...: 当前请求地址为： {data}.")
        logger.info("保存为状态记录")
        time.sleep(5)
        cur_status = "failed"
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

                # print(cur_status)
                self.candidate_queue.put_nowait(data)
                time.sleep(1)  # 0.5s获取数据
            except Full:
                time.sleep(.2)  # 0.5s获取数据
            except Exception as e:
                logger.exception(e)
# 创建
my_agent = MyMQTTAgent()
my_agent.run()
