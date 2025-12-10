"""Watch the raw data directory, push events to Kafka
"""
# pylint: disable-all
# noqa: E501
import logging
import os
import time
from dataclasses import asdict
from typing import NoReturn

from watchdog.events import FileSystemEvent, FileSystemEventHandler, LoggingEventHandler
from watchdog.observers import Observer

from common.consts import KAFKA_PRODUCE_TIMEOUT
from app.kafka import KafkaAccSender


KAFKA_TOPIC = "watch-raw"


class MyEventHandler(FileSystemEventHandler):
    def on_closed(self, event: FileSystemEvent) -> None:
        print(event)


class KafkaEventHandler(LoggingEventHandler):
    def __init__(self, kafka_sender, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sender = kafka_sender

    def on_closed(self, event: FileSystemEvent) -> None:
        """Add the event to the sender
        """
        self._sender.add(asdict(event))


def watch_dir(dir: str) -> NoReturn:
    """
    Watch directory for filesystem changes and push such events to Kafka

    Args:
        dir (str):
    """
    observer = Observer()
    kafka_sender = KafkaAccSender(topic=KAFKA_TOPIC, batchsize=10, send_timeout=KAFKA_PRODUCE_TIMEOUT)
    event_handler = KafkaEventHandler(kafka_sender=kafka_sender)
    observer.schedule(event_handler, dir, recursive=True)
    observer.start()
    try:
        while True:
            observer.join(1)
            kafka_sender.send()
    finally:
        observer.stop()
        observer.join()
