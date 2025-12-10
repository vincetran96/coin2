"""Administrative operations for fetching work,
meant to be run once and exit
"""
import logging

from common.consts import LOG_FORMAT
from common.kafka import create_new_topics
from app.configs import KAFKA_ETL_TOPICS


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    create_new_topics(topics=KAFKA_ETL_TOPICS, num_partitions=6, replication_factor=2)
