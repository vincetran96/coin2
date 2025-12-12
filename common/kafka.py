"""Kafka
"""
# pylint: disable-all
# noqa: E501
import json
import logging
from contextlib import closing
from typing import Any, List

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from common.configs import Config, OsVariable


def acked(err, msg):
    """Ack callback, used for delivery
    """
    if err is not None:
        logging.error("Msg delivery failed: {}".format(err))
    else:
        logging.info("Msg delivered to topic: {}, partition: {}".format(msg.topic(), msg.partition()))


def create_producer() -> Producer:
    """Create a Kafka producer
    """
    return Producer({
        "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
    })


def create_consumer(
    group_id: str,
    auto_commit: bool = True,
    auto_offset_reset: str = "earliest",
) -> Consumer:
    """Create a Kafka consumer
    """
    return closing(
        Consumer({
            "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER),
            "group.id": group_id,
            "enable.auto.commit": auto_commit,
            "auto.offset.reset": auto_offset_reset
        })
    )


def create_admin_client():
    """Create an admin client
    """
    return AdminClient({
        "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
    })


def create_new_topics(topics: List[str], num_partitions: int, replication_factor: int) -> None:
    """Create new topics

    Args:
        topics (List[str]): topics
        num_partitions (int): number of partitions
        replication_factor (int): replication factor
    """
    client = create_admin_client()
    ops = client.create_topics(
        [
            NewTopic(
                topic=topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            ) for topic in topics
        ]
    )
    for topic, f in ops.items():
        try:
            f.result()
            logging.info("Topic {} created".format(topic))
        except (Exception, ) as exc:
            logging.error("Failed to create topic {}: {}".format(topic, exc))


def send_to_kafka(producer: Producer, topic: str, data_list: List[dict], data_key: str = None):
    """Send data (as a list of dict) to Kafka

    Source: https://github.com/confluentinc/confluent-kafka-python

    Args:
        producer (Producer): Kafka producer
        topic (str): Topic
        data_list (List[dict]): List of data
        data_key (str): Dictionary key to use as the key for the message; Must exist in the data element
    """
    for data in data_list:
        producer.poll(timeout=0)
        producer.produce(
            topic=topic,
            value=json.dumps(data).encode("utf-8"),
            key=data[data_key].encode("utf-8") if data_key is not None else None
        )
    producer.flush()
    logging.info(f"Finished sending {len(data_list)} records to Kafka")
