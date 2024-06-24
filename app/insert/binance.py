"""Consume data from Kafka
"""
# pylint: disable-all
# noqa: E501
import logging
from typing import List, NoReturn

from common.consts import LOG_FORMAT
from common.kafka import create_consumer


KAFKA_TOPIC = "ws-binance"  # Use OS env var


def consume_from_kafka(topics: List[str], group_id: str, timeout: float) -> NoReturn:
    """Consume from Kafka
    Source: https://github.com/confluentinc/confluent-kafka-python

    Args:
        topics (List[str]): List of topics
        group_id (str): group ID of this consumer
        timeout (float): timeout when polling a message
    """
    with create_consumer(group_id=group_id, enable_auto_commit=False) as consumer:
        consumer.subscribe(topics)
        while True:
            msg_ = consumer.poll(timeout=timeout)
            if msg_:
                if msg_.error():
                    logging.error(f"Consumer error: {msg_.error()}")
                    continue
                msg = msg_.value().decode("utf-8")
                _, timestamp = msg_.timestamp()
                offset = msg_.offset()
                logging.info(f"Received message:\n{msg}\n, timestamp: {timestamp}\n, offset: {offset}")


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    consume_from_kafka(topics=[KAFKA_TOPIC], group_id="ws-consumer", timeout=1.0)
