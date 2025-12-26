"""Script to test the availablity of Kafka cluster
"""
import logging

from common.configs import Config, OsVariable
from common.utils.connections import is_socket_open


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ch_host = Config.os_get(OsVariable.CLICKHOUSE_HOST.value)
    ch_port = Config.os_get(OsVariable.CLICKHOUSE_NATIVE_PORT.value)
    logging.info(f"Checking ClickHouse server at {ch_host}:{ch_port}")
    is_socket_open(f"{ch_host}:{ch_port}")
