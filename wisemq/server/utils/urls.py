from enum import Enum


class URLS(Enum):

    # user
    create_wisemq_user = "/api/v1/mq/create_wisemq_user"
    get_client_config_file = "/api/v1/mq/{token}/get_client_config_file"
    get_user_info = "/api/v1/mq/{token}/get_user_info"
    # dataset
    create_dataset = "/api/v1/mq/{token}/create_dataset"
    get_dataset_list = "/api/v1/mq/{token}/get_dataset_list"
    get_dataset_info = "/api/v1/mq/{token}/dataset/{dataset_pk}/get_info"
    # data
    get_data_info = "/api/v1/mq/{token}/data/{data_pk}/get_info"
    get_messages = "/api/v1/mq/{token}/data/{data_pk}/get_messages"
    update_command = "/api/v1/mq/{token}/data/{data_pk}/update_command"



