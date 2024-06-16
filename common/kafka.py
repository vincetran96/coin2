"""Kafka
"""
import logging

from typing import List

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from common.configs import Config, OsVariable


def acked(err, msg):
    """Ack callback, used for delivery
    """
    if err is not None:
        logging.error("Message delivery failed: {}".format(err))
    else:
        logging.info("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


def create_kafka_producer() -> Producer:
    """Create a Kafka producer
    """
    # return Producer(
    #     {
    #         "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
    #     }
    # )

    return Producer(
        {"bootstrap.servers": "100.71.94.50:9094"}
    )


def create_kafka_admin_client():
    """Create an admin client
    """
    return AdminClient(
        {"bootstrap.servers": "100.71.94.50:9094"}
    )


def create_new_topics(topics: List[str], num_partitions: int, replication_factor: int) -> None:
    """Create new topics

    Args:
        topics: topics
        num_partitions: number of partitions
        replication_factor: replication factor
    """
    client = create_kafka_admin_client()
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
        except (Exception, ) as e:
            logging.error("Failed to create topic {}: {}".format(topic, e))
