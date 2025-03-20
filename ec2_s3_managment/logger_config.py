import logging
from ec2_s3_managment.ec2_s3_constants import LOGGER_OUT_PATH, LOGGER_NAME
# Configure the logger
open(LOGGER_OUT_PATH, 'w').close()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGGER_OUT_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(LOGGER_NAME)
logger.info("=== Logger Start ===")