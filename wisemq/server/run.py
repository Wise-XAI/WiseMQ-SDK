import requests

from .utils.urls import URLS
from .utils.config import logger, WISEMQ_API_SERVER


class WiseMQInterface:
    def __init__(self, WISEMQ_API_SERVER=WISEMQ_API_SERVER):
        """Class to initiate call to WiseMQ backend

        Arguments:
            APIKEY {[string]} -- The authentication token corresponding to WiseMQ
            WISEMQ_API_SERVER {[string]} -- It should be set to https://wisemq.wise-xai.com # For production server
        """
        self.TOKEN = str()
        self.WISEMQ_API_SERVER = WISEMQ_API_SERVER

    def _get_request_headers(self):
        """Function to get the header of the EvalAI request in proper format

        Returns:
            [dict]: Authorization header
        """
        headers = {"Authorization": "Bearer " + self.TOKEN}
        return headers

    def _make_request(self, url, method, data=None, json=None):
        """Function to make request to WiseMQ interface

        Args:
            url ([str]): URL of the request
            method ([str]): Method of the request
            data ([dict], optional): Data of the request. Defaults to None.

        Returns:
            [JSON]: JSON response data
        """
        headers = self._get_request_headers()
        try:
            response = requests.request(
                method=method, url=url, headers=headers, data=data, json=json
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            try:
                logger.info(response.json())
                logger.error("The server isn't able establish connection with WiseMQ")
                return False, response.json()
            except Exception as e:
                return False, e
                
        return True, response.json()

    def _return_url_per_environment(self, url):
        """Function to get the URL for API

        Args:
            url ([str]): API endpoint url to which the request is to be made

        Returns:
            [str]: API endpoint url with EvalAI base url attached
        """
        base_url = "{0}".format(self.WISEMQ_API_SERVER)
        url = "{0}{1}".format(base_url, url)
        return url

    def _general_get_request(self, url):
        """General GET request to url."""
        url = self._return_url_per_environment(url)
        response = self._make_request(url, "GET")
        return response

    def auth_token(self, token):
        """认证用户token"""
        url = self._return_url_per_environment(URLS.auth_token.value)
        response = self._make_request(url, "POST", json={"token": token})
        return response

    def refresh_token(self, token):
        """刷新用户token"""
        url = self._return_url_per_environment(URLS.token_refresh.value)
        response = self._make_request(url, "POST", json={"refresh": token})
        return response

    def auth_user(self, username, password):
        """认证用户登录"""
        url = self._return_url_per_environment(URLS.auth_user.value)
        json_data = {
            "username": username,
            "password": password
        }
        response = self._make_request(url, "POST", json=json_data)
        return response

    def get_user_device_list(self, token, category=""):
        """获取用户设备列表"""
        self.TOKEN = token
        return self._general_get_request(URLS.get_user_device_list.value.format(category))
    
    def get_device_status(self, token, device_id):
        """获取单个设备信息"""
        self.TOKEN = token

        url = URLS.get_device_status.value.format(device_id=device_id)
        return self._general_get_request(url)

    def get_device_list_status(self, token, devices):
        """获取用户设备列表"""
        self.TOKEN = token
        json_data = {
            "devices": devices
        }
        url = self._return_url_per_environment(URLS.get_device_list_status.value)
        response = self._make_request(url, "GET", json=json_data)
        return response

    def update_status(self, token, device_id, name, value):
        """更新状态"""
        self.TOKEN = token

        url = URLS.update_status.value.format(device_id=device_id)
        url = self._return_url_per_environment(url)
        json_data = {
            "update_status": {
                "name": name,
                "value": value
            }
        }
        response = self._make_request(url, "PUT", json=json_data)
        return response

    def update_device_name(self, token, device_id, new_name):
        """更新设备名称"""
        self.TOKEN = token
        url = URLS.update_device_name.value.format(device_id=device_id)
        url = self._return_url_per_environment(url)
        json_data = {
            "new_device_name": new_name,
        }
        response = self._make_request(url, "PUT", json=json_data)
        return response