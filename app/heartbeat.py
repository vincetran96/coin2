"""App heartbeat
"""
import logging
from time import sleep

from common.consts import LOG_FORMAT
from common.configs import Config, OsVariable
from common.utils.connections import is_socket_open


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    while True:
        kafka_bootstrap_server = Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
        logging.info(f"Checking Kafka bootstrap server at {kafka_bootstrap_server}")
        is_socket_open(kafka_bootstrap_server)
        sleep(10)
