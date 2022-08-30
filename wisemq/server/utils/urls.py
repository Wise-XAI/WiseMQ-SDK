from enum import Enum


class URLS(Enum):

    # user
    # create_wisemq_user = "/api/v1/mq/create_wisemq_user"
    # get_user_info = "/api/v1/mq/{token}/get_user_info"
    # agent
    # create_data_agent = "/api/v1/mq/{token}/create_data_agent"
    get_user_device_list = "/api/v1/device/get_user_device_list?page_size=1000"
    get_device_status = "/api/v1/device/get_device_status?device_id={device_id}"
    # get_client_config_file = "/api/v1/mq/{token}/agent/{agent}/get_client_config_file"
    # get_data_agent_info = "/api/v1/mq/{token}/agent/{agent}/get_info"
    # get_messages = "/api/v1/mq/{token}/agent/{agent}/get_messages?offset={offset}&limit={limit}"
    update_status = "/api/v1/device/update_status?device_id={device_id}"
    update_device_name = "/api/v1/device/update_device_name?device_id={device_id}"



