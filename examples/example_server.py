from server import WiseMQInterface

AUTH_TOKEN = ""

wisemq_interface = WiseMQInterface(AUTH_TOKEN, "http://localhost:8000")

print(wisemq_interface.get_dataset_list(token="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"))