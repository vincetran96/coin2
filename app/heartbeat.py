"""App heartbeat
"""
import argparse
import logging
import os
from time import sleep

from common.consts import LOG_FORMAT
from common.configs import Config, OsVariable
from common.utils.connections import is_socket_open


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    while True:
        kafka_host, kafka_port = "100.71.94.50", "9094"  # replace with OS env var
        is_socket_open(kafka_host, int(kafka_port))
        sleep(10)
