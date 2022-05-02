"""
记录所用到的请求地址
"""
from enum import Enum


class URLS(Enum):
    login = "/api/user/login"
    dataset_create = "/api/dataset/create_dataset"
    file_data_upload = "/api/dataset/upload_file"
    update_heartbeat = "/api/dataset/update_heartbeat"


