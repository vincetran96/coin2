"""Kafka
"""
import logging

from confluent_kafka import Producer

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
        {
            "bootstrap.servers": "100.71.94.50:9094"
        }
    )
