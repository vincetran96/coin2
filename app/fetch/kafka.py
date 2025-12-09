"""Kafka functionalities related to fetch
"""
import json
import logging
from typing import Any, List


def send_to_kafka(producer: Any, topic: str, data_list: List[dict]):
    """Send data (as a list of dict) to Kafka

    Source: https://github.com/confluentinc/confluent-kafka-python

    Args:
        producer (Producer): Kafka producer
        topic (str): Topic
        data_list (List[dict]): List of data
    """
    for data in data_list:
        producer.poll(timeout=0)
        producer.produce(topic=topic, key=data["symbol"], value=json.dumps(data))
    producer.flush()
    logging.info(f"Finish send data to kafka, num records: {len(data_list)}")
