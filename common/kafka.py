"""Kafka
"""
from confluent_kafka import Producer

from common.configs import Config, OsVariable


def acked(err, msg):
    """Ack callback, used for delivery
    """
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


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
            "bootstrap.servers": "localhost:9095"
        }
    )
