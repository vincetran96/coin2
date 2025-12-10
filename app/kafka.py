"""Kafka functionalities related to the app
"""
import time
from typing import Dict

from common.kafka import create_producer, send_to_kafka


class KafkaAccSender():
    """
    Convenient class for accumulating data and sending it to Kafka.

    When calling `send()`, it checks if the length of the data is at least `batchsize`,
    or if the time elapsed is at least `send_timeout`. If yes, data is produced to Kafka.
    """
    def __init__(self, topic: str, batchsize: int, send_timeout: int, data_key: str = None):
        """
        Args:
            key (str): Dictionary key to use as the key for the message; Must exist in the data element
        """
        self.data_list = []
        self.batchsize = batchsize
        self.send_timeout = send_timeout
        self.start_time = time.monotonic()

        self.topic = topic
        self.key = data_key

        # Private
        self._producer = create_producer()

    def add(self, data: Dict):
        self.data_list.append(data)

    def send(self):
        if self.data_list:
            if len(self.data_list) >= self.batchsize or time.monotonic() - self.start_time >= self.send_timeout:
                send_to_kafka(producer=self._producer, topic=self.topic, data_list=self.data_list, data_key=self.key)
                
                # Reset
                self.data_list = []
                self.start_time = time.monotonic()
