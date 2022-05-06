"""
环境配置变量
"""

import os
from os.path import expanduser
import logging

AUTH_TOKEN_DIR = expanduser("~/.wise/")
AUTH_TOKEN_FILE_NAME = "token.json"
# HOST = "http://localhost"
HOST = "http://platform.wise-xai.com"
# PORT = 8000
PORT = 80
API_HOST_URL = HOST + ":" + str(PORT)

AUTH_TOKEN_PATH = os.path.join(AUTH_TOKEN_DIR, AUTH_TOKEN_FILE_NAME)
ERROR_CODES = [400, 401, 403, 406]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("[WISEAI]")
