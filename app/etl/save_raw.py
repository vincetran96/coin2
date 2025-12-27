"""Consume data from Kafka, save to raw files
"""
# pylint: disable-all
# noqa: E501
import json
import logging
import os
import socket
import uuid
import time
from pathlib import Path
from typing import List, NoReturn

from common.kafka import create_consumer
from data.clickhouse.base_inserter import ClickHouseBaseInserter


def _make_unique_filename(
    dir_path: str,
    topic: str = None,
    partition: int = None,
    start_offset: int = None,
    end_offset: int = None,
    ext: str = "json"
) -> str:
    """Private function
    
    Make a unique file name when saving from Kafka
    
    Returns:
        str
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    ts = time.time_ns()
    host = socket.gethostname()
    pid = os.getpid()
    uid = uuid.uuid4().hex[:8]
    parts = []
    if topic:
        parts.append(topic)
    parts += [host, f"pid{pid}", f"ts{ts}", uid]
    if partition is not None:
        parts.append(f"part{partition}")
    if start_offset is not None and end_offset is not None:
        parts.append(f"offset{start_offset}-{end_offset}")
    filename = "_".join(parts) + f".{ext}"

    return str(Path(dir_path) / filename)


def consume_from_kafka(
    topic: str,
    group_id: str,
    poll_timeout: float,
    write_batchsize: int,
    write_timeout: int,
    output_dir: str
) -> NoReturn:
    """Consume websocket data from a Kafka topic

    Source: https://github.com/confluentinc/confluent-kafka-python

    Currently we set the write batch size equal to the Kafka batch size.
    We consume from only one topic because each exchange's message schema can be different.

    We assume that the message string follows a JSON-like format, and thus
    we convert it to a dict first before writing to disk.

    Args:
        topic (str): Topic name
        group_id (str): Group ID of this consumer
        poll_timeout (float): Timeout when polling a message
        write_batchsize (int):
        write_timeout (int): Timeout (in secs) to wait before writing the data batch to disk
        output_dir (str):

    """
    logging.info(f"Start consuming from topic: {topic}")
    with create_consumer(group_id=group_id, auto_commit=False) as consumer:
        consumer.subscribe([topic])
        data = []
        batch_start_offset, batch_end_offset = None, None
        start_ts = time.monotonic()
        partition, offset = None, None
        while True:
            msg_ = consumer.poll(timeout=poll_timeout)
            if msg_:
                if msg_.error():
                    logging.error(f"Consumer error: {msg_.error()}")
                    continue

                # Extract message metadata
                msg = msg_.value().decode("utf-8")
                _, timestamp = msg_.timestamp()
                try:
                    partition = msg_.partition()
                    offset = msg_.offset()
                except Exception:
                    logging.info("No partition and offset info found, resetting these variables")
                    partition, offset = None, None
                if batch_start_offset is None and offset is not None:
                    batch_start_offset = offset
                if offset is not None:
                    batch_end_offset = offset
                
                # Accumulate message data into batch
                data.append(json.loads(msg))

            # Write data to disk when there is data, and batchsize or timeout reached
            if data and (len(data) >= write_batchsize or time.monotonic() - start_ts >= write_timeout):
                elapsed_ts = time.monotonic() - start_ts
                try:
                    filename = _make_unique_filename(
                        output_dir, topic=topic, partition=partition, start_offset=batch_start_offset, end_offset=batch_end_offset
                    )
                    with open(filename, "w") as outfile:
                        json.dump(data, outfile)
                except Exception as exc:
                    logging.exception("Failed to write batch to file: %s", exc)
                finally:
                    logging.info(f"Processed {len(data)} msgs in {elapsed_ts:.2f} secs ({write_batchsize / elapsed_ts:.2f} msgs/s)")
                    data = []
                    batch_start_offset, batch_end_offset = None, None
                    start_ts = time.monotonic()
                    consumer.commit()
