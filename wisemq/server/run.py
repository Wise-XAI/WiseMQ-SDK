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
            except:
                raise requests.exceptions.RequestException
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
        url = self._return_url_per_environment(url)
        response = self._make_request(url, "GET")
        return response

    def create_wisemq_user(self, data):
        """
        Args:
            data ([dict]): User Data to be created
            data: {
                "user_token": "APIKEY"
            }
            The necessary key is `user_token`

        Returns:
            [JSON]: JSON response data
        """
        url = URLS.create_wisemq_user.value
        url = self._return_url_per_environment(url)
        response = self._make_request(url, "post", data=data)
        return response

    def get_client_config_file(self, user_token, agent):
        """Get User Config FILE

        Args:
            user_token: Token when created MQTT User.
            agent: Agent KEY.
        Returns:
            File Download
        """
        url = URLS.get_client_config_file.value.format(token=user_token, agent=agent)
        url = self._return_url_per_environment(url)

        headers = self._get_request_headers()
        try:
            response = requests.request(
                method="GET", url=url, headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            try:
                logger.info(response.json())
                logger.error("The server isn't able establish connection with WiseMQ")
            except:
                raise requests.exceptions.RequestException(response.json())
        return response

    def get_user_info(self, user_token):
        """Get User Info

        Args:
            user_token: Token when created MQTT User.
        Returns:
            User Information
        """
        url = URLS.get_user_info.value.format(token=user_token)
        return self._general_get_request(url)

    def create_data_agent(self, user_token, number_of_data):
        """Create Dataset for a user

        Args:
            user_token: Token when created MQTT User.
            number_of_data: Nmuber of data that supposed to create.
        Returns:
            200, created dataset infomation.

        """
        data = {"number_of_data": number_of_data}
        url = URLS.create_data_agent.value.format(token=user_token)
        url = self._return_url_per_environment(url)
        response = self._make_request(url, "post", data=data)
        return response

    def get_data_agent_list(self, user_token):
        """Get Dataset List for a user

        Args:
            user_token: Token when created MQTT User.
        Returns:
            200, dataset list.

        """
        url = URLS.get_data_agent_list.value.format(token=user_token)
        return self._general_get_request(url)

    def get_data_agent_info(self, user_token, agent):
        """Get Single Data Information.

        Args:
            user_token: Token when created MQTT User.
            agent: Agent model primary name.
        Returns:
            200
        """
        url = URLS.get_data_agent_info.value.format(token=user_token, agent=agent)
        return self._general_get_request(url)

    def get_messages(self, user_token, agent, offset=None, limit=None):
        """Get MQTT message in Data

        Args:
            user_token: Token when created MQTT User.
            data_name: Data model primary name.
            offset: Offset for messages.
            limit: Limited number of messages.
        Returns:
            200, message list.

        """
        if not offset:
            offset = 0

        if not limit:
            limit = 20

        url = URLS.get_messages.value.format(token=user_token, agent=agent, offset=offset, limit=limit)
        return self._general_get_request(url)

    def update_status(self, user_token, agent, json):
        """Command that control corresponding client session. 

        Args:
            - user_token: Token when created MQTT User.
            - agent: agent.
            - json: status name, which the type is switch.
        Returns:
            200, updated extra information

        """
        url = URLS.update_status.value.format(token=user_token, agent=agent)
        url = self._return_url_per_environment(url)
        response = self._make_request(url, "PATCH", json=json)
        return response
