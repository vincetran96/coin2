"""App heartbeat
"""
import logging
from time import sleep

from common.configs import Config, OsVariable
from common.utils.connections import is_socket_open


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while True:
        kafka_host, kafka_port = Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER).split(":")
        is_socket_open(kafka_host, int(kafka_port))
        sleep(5)
