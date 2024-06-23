"""Administrative operations for fetching work
"""
import logging

from common.consts import LOG_FORMAT
from common.kafka import create_new_topics


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    create_new_topics(
        topics=["ws-binance"],  # replace with OS env var
        num_partitions=6,
        replication_factor=2
    )
