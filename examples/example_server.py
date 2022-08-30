# dev
import sys
sys.path.append('/home/dongbox/work/WiseMQ-SDK/')

from wisemq.server import WiseMQInterface

AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjkyNzg0ODAzLCJpYXQiOjE2NjEyNDg4MDMsImp0aSI6ImVjNGM2ZWQyYjhjODQ1MjFiMjI5ZDE3ZDExMjFjODE5IiwidXNlcl9pZCI6MX0.NFYFbF0aMiIBaQPCMxyeeFt7x1JpIk_VjZ5Z2djdb1E"

wisemq_interface = WiseMQInterface(AUTH_TOKEN)

print(wisemq_interface.get_user_device_list())
# print(wisemq_interface.get_device_status("mockdevice1"))
# print(wisemq_interface.update_status("mockdevice1", "status2", 1))
# print(wisemq_interface.update_device_name("mockdevice1", "测试设备一号"))