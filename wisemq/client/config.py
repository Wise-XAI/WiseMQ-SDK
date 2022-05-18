"""
环境配置变量
"""

import logging

# HOST = "http://localhost"
HOST = "http://wisemq.wise-xai.com"
# PORT = 8000
PORT = 80
API_HOST_URL = HOST + ":" + str(PORT)

ERROR_CODES = [400, 401, 403, 406]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("[WISEAI]")
