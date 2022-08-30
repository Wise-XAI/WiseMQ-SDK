import logging

# HOST = "http://localhost"
HOST = "https://wiseagent.wise-xai.com"
# PORT = 8000
PORT = 443
WISEMQ_API_SERVER = HOST + ":" + str(PORT)

ERROR_CODES = [400, 401, 403, 406]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("[WISEMQ]")
