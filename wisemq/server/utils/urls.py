from enum import Enum


class URLS(Enum):

    # user
    auth_user = "/api/v1/user/login"
    token_refresh = "/api/v1/user/refresh_token"
    auth_token = "/api/v1/user/auth_token"
    get_user_device_list = "/api/v1/device/get_user_device_list?page_size=1000&category={}"
    get_device_list_status = "/api/v1/device/get_device_list_status"
    get_device_status = "/api/v1/device/get_device_status?device_id={device_id}"
    update_status = "/api/v1/device/update_status?device_id={device_id}"
    update_device_name = "/api/v1/device/update_device_name?device_id={device_id}"



