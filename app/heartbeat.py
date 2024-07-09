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
        is_socket_open(Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER))
        sleep(10)
