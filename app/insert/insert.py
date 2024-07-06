"""Consume data from Kafka
"""
# pylint: disable-all
# noqa: E501
import logging
import time
from typing import List, NoReturn

from common.consts import KAFKA_BATCHSIZE, LOG_FORMAT
from common.kafka import create_consumer
from app.configs import KAFKA_FETCH_TOPICS


def consume_from_kafka(topics: List[str], group_id: str, timeout: float, batchsize: int) -> NoReturn:
    """Consume websocket data from Kafka
    Source: https://github.com/confluentinc/confluent-kafka-python

    Args:
        topics (List[str]): List of topics
        group_id (str): group ID of this consumer
        timeout (float): timeout when polling a message

    """
    with create_consumer(group_id=group_id, auto_commit=False) as consumer:
        consumer.subscribe(topics)
        count = 0
        start_ts = time.monotonic()
        while True:
            msg_ = consumer.poll(timeout=timeout)
            if msg_:
                if msg_.error():
                    logging.error(f"Consumer error: {msg_.error()}")
                    continue
                msg = msg_.value().decode("utf-8")
                _, timestamp = msg_.timestamp()
                offset = msg_.offset()
                count += 1
                logging.info(
                    f"Received msg:\n{msg}\n, timestamp: {timestamp}\n, offset: {offset}"
                )
            if count >= batchsize:
                elapsed_ts = time.monotonic() - start_ts
                count = 0
                start_ts = time.monotonic()
                consumer.commit()
                logging.info(
                    f"Processed {batchsize} msg in {elapsed_ts:.2f} secs ({batchsize / elapsed_ts:.2f} msg/s)"
                )


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    consume_from_kafka(
        topics=KAFKA_FETCH_TOPICS, group_id="ws-consumer", timeout=1.0, batchsize=KAFKA_BATCHSIZE
    )
