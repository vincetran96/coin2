"""Kafka functionalities related to the app
"""
import logging
import time
from typing import Dict, Callable, List, Optional

from confluent_kafka import Consumer

from common.kafka import create_consumer, create_producer, send_to_kafka
from data.interfaces import DataInserter


class KafkaAccSender():
    """
    Convenient class for accumulating some data and sending it to Kafka.

    When calling `send()`, it checks if the length of the data is at least `batchsize`,
    or if the time elapsed is at least `send_timeout`. If yes, data is produced to Kafka.
    """
    def __init__(self, topic: str, batchsize: int, send_timeout: int, data_key: Optional[str] = None):
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


class KafkaAccDbInserter():
    """
    Convenient class for consuming data from Kafka, accumulating data, and inserting it to a target table.

    When calling the insert method, it checks if the length of the data is at least `batchsize`,
    or if the time elapsed is at least `send_timeout`. If yes, we attempt to insert.
    """
    # TODO: Too many params, may need refactor
    def __init__(
        self,
        topic: str,
        batchsize: int,
        wait_timeout: int,
        group_id: str,
        target_tbl: str,
        db_inserter: DataInserter,
        extract_fields: List[str],
        poll_timeout: int = 3,
        msg_processor: Callable = lambda x: x
    ):
        """
        The `msg_processor` callable should not be a costly operation, because it operates on every single message.

        Args:
            batchsize (int): Minimum number of messages to accumulate before attempting insert
            wait_timeout (int): Maximum duration in seconds to wait for msgs to arrive before attempting insert
            group_id (str): Kafka consumer group ID
            extract_fields (List[str]): List of fields to extract from message
            poll_timeout (int): Timeout in seconds when polling messages from Kafka
            msg_processor (Callable): A function taking in the msg dict and outputing processed dict
        """
        self.data_list = []
        self.batchsize = batchsize
        self.wait_timeout = wait_timeout
        self.batch_start_time = time.monotonic()

        self.topic = topic
        self.target_tbl = target_tbl
        self.extract_fields = extract_fields
        self.poll_timeout = poll_timeout
        self.msg_processor = msg_processor

        # Private
        self._consumer: Consumer = create_consumer(group_id=group_id, auto_commit=False)
        self._db_inserter = db_inserter

    def add(self, data: Dict):
        self.data_list.append(self.msg_processor(data))

    def insert_to_tbl(self, consumer: Consumer, db_inserter: DataInserter, force: bool = False):
        if self.data_list:
            if (
                force
                or len(self.data_list) >= self.batchsize
                or time.monotonic() - self.batch_start_time >= self.wait_timeout
            ):
                db_inserter.insert(tbl_name=self.target_tbl, data=self.data_list, field_names=self.extract_fields)

                # Reset and commit
                self.data_list = []
                self.batch_start_time = time.monotonic()
                consumer.commit()

    def run_consume(self, max_runtime: Optional[float] = None):
        """Run the consume process and insert

        Args:
            max_runtime (Optional[float]): Maximum runtime in seconds; if reached, the consume loop will exit
        """
        logging.info(f"Start consuming from topic: {self.topic}")
        start = time.monotonic()
        with self._consumer as consumer, self._db_inserter as db_inserter:
            consumer.subscribe([self.topic])
            while True:
                if max_runtime is not None and (time.monotonic() - start) >= max_runtime:
                    logging.info(f"Max runtime reached ({max_runtime}s); flushing and exiting consume loop.")
                    break

                msg_ = consumer.poll(timeout=self.poll_timeout)
                if msg_:
                    if msg_.error():
                        logging.error(f"Consumer error: {msg_.error()}")
                        continue
                    raw = msg_.value()
                    if raw is None:
                        continue
                    msg = raw.decode("utf-8")
                    self.add(msg)
                self.insert_to_tbl(consumer=consumer, db_inserter=db_inserter)

            # Final flush for any remaining data
            self.insert_to_tbl(consumer=consumer, db_inserter=db_inserter, force=True)

        logging.info(f"Consumption loop from topic {self.topic} stopped!")
