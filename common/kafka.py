"""Kafka
"""
# noqa: E501
import logging
from contextlib import closing
from typing import List

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
    # return Producer(
    #     {
    #         "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
    #     }
    # )

    return Producer({
        "bootstrap.servers": "100.71.94.50:9094"
    })


def create_consumer(
    group_id: str,
    auto_offset_reset: str = "earliest",
    enable_auto_commit: bool = True
) -> Consumer:
    """Create a Kafka consumer
    """
    return closing(
        Consumer({
            "bootstrap.servers": "100.71.94.50:9094",
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": enable_auto_commit
        })
    )


def create_admin_client():
    """Create an admin client
    """
    return AdminClient(
        {"bootstrap.servers": "100.71.94.50:9094"}
    )


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
        except (Exception, ) as e:
            logging.error("Failed to create topic {}: {}".format(topic, e))
