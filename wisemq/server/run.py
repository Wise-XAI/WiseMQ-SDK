import requests

from .utils.urls import URLS
from .utils.config import logger, WISEMQ_API_SERVER


class WiseMQInterface:
    def __init__(self, APIKEY, WISEMQ_API_SERVER=WISEMQ_API_SERVER):
        """Class to initiate call to WiseMQ backend

        Arguments:
            APIKEY {[string]} -- The authentication token corresponding to WiseMQ
            WISEMQ_API_SERVER {[string]} -- It should be set to https://wisemq.wise-xai.com # For production server
        """

        self.APIKEY = APIKEY
        self.WISEMQ_API_SERVER = WISEMQ_API_SERVER

    def _get_request_headers(self):
        """Function to get the header of the EvalAI request in proper format

        Returns:
            [dict]: Authorization header
        """
        headers = {"ApplicationKey": self.APIKEY}
        return headers

    def _make_request(self, url, method, data=None):
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
                method=method, url=url, headers=headers, data=data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.info("The server isn't able establish connection with WiseMQ")
            logger.info(f"Error Message: {response.json()}")
            raise
        return response.json()

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
        url = self.return_url_per_environment(url)
        response = self._make_request(url, "GET")
        return response

    def create_wisemq_user(self, data):
        """
        Args:
            data ([dict]): User Data to be created
            The necessary key is `user_token`

        Returns:
            [JSON]: JSON response data
        """
        url = URLS.create_wisemq_user.value
        url = self.return_url_per_environment(url)
        response = self._make_request(url, "post", data=data)
        return response

    def get_client_config_file(self, user_token):
        """Get User Config FILE

        Args:
            user_token: Token when created MQTT User.
        Returns:
            File Download
        """
        url = URLS.get_client_config_file.value.format(token=user_token)
        return self._general_get_request(url)

    def create_dataset(self, user_token):
        """Create Dataset for a user

        Args:
            user_token: Token when created MQTT User.
        Returns:
            200, created dataset infomation.

        """
        url = URLS.create_dataset.value.format(token=user_token)
        return self._general_get_request(url)

    def get_dataset_list(self, user_token):
        """Get Dataset List for a user

        Args:
            user_token: Token when created MQTT User.
        Returns:
            200, dataset list.

        """
        url = URLS.get_dataset_list.value.format(token=user_token)
        return self._general_get_request(url)

    def get_dataset_info(self, user_token, dataset_pk):
        """Get Single Dataset Information included data list in it.

        Args:
            user_token: Token when created MQTT User.
        Returns:
            200, dataset info.
        """
        url = URLS.get_dataset_list.value.format(token=user_token, dataset_pk=dataset_pk)
        return self._general_get_request(url)

    def get_data_info(self, user_token, data_pk):
        """Get Single Data Information.

        Args:
            user_token: Token when created MQTT User.
            data_pk: Data model primary key.
        Returns:
            200, dataset info.
        """
        url = URLS.get_data_info.value.format(token=user_token, data_pk=data_pk)
        return self._general_get_request(url)

    def get_messages(self, user_token, data_pk):
        """Get MQTT message in Data

        Args:
            user_token: Token when created MQTT User.
            data_pk: Data model primary key.
        Returns:
            200, message list.

        """
        url = URLS.get_messages.value.format(token=user_token, data_pk=data_pk)
        return self._general_get_request(url)

    def update_command(self, user_token, data_pk):
        """Command that control corresponding client session. 

        Args:
            user_token: Token when created MQTT User.
            data_pk: Data model primary key.
        Returns:
            200, updated extra information

        """
        url = URLS.update_command.value.format(token=user_token, data_pk=data_pk)
        url = self.return_url_per_environment(url)
        response = self._make_request(url, "PATCH")
        return response
