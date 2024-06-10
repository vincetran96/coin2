"""Kafka
"""
from confluent_kafka import Producer

from common.configs import Config, OsVariable


def acked(err, msg):
    """Ack callback, used for delivery
    """
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


def kafka_producer() -> Producer:
    """Create a Kafka producer
    """
    # return Producer(
    #     {
    #         "bootstrap.servers": Config.os_get(OsVariable.KAFKA_BOOTSTRAP_SERVER)
    #     }
    # )
    return Producer(
        {
            "bootstrap.servers": "localhost:9094"
        }
    )
