from enum import Enum


class URLS(Enum):

    # user
    create_wisemq_user = "/api/v1/mq/create_wisemq_user"
    get_client_config_file = "/api/v1/mq/{token}/get_client_config_file"
    get_user_info = "/api/v1/mq/{token}/get_user_info"
    # data
    create_data_agent = "/api/v1/mq/{token}/create_data_agent"
    get_data_agent_list = "/api/v1/mq/{token}/get_data_agent_list"
    get_data_agent_info = "/api/v1/mq/{token}/data/{data_pk}/get_info"
    get_messages = "/api/v1/mq/{token}/data/{data_pk}/get_messages?offset={offset}&limit={limit}"
    update_status = "/api/v1/mq/{token}/data/{agent}/update_status"



