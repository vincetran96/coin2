"""This file is to be used in CLI

One use case is for testing.
"""
import argparse
import json
import logging
import os
import socket
import uuid
import time
from pathlib import Path
from typing import List, NoReturn

from app.configs import KAFKA_FETCH_TOPICS, INSERTER_KAFKA_GROUP_ID
from app.etl.save_raw import consume_from_kafka
from common.consts import KAFKA_CONSUME_BATCHSIZE, LOG_FORMAT
from common.kafka import create_consumer
from data.clickhouse.base_inserter import BaseInserter


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Consume from Kafka and write batches to disk")
    p.add_argument("-t", "--topic", type=str, required=True, help="Kafka topic")
    p.add_argument("--timeout", type=float, default=1.0, help="Poll timeout (seconds)")
    p.add_argument("--write_batchsize", type=int, default=KAFKA_CONSUME_BATCHSIZE, help="Batch size for writes")
    p.add_argument("--write_timeout", type=int, default=120, help="Timeout for writes")
    p.add_argument("--output_dir", type=str, required=True, help="Output dir")
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    args = _parse_args()
    topic = args.topic
    timeout = args.timeout
    write_batchsize = args.write_batchsize
    write_timeout = args.write_timeout
    output_dir = args.output_dir

    try:
        consume_from_kafka(
            topic=topic, group_id=INSERTER_KAFKA_GROUP_ID, poll_timeout=timeout,
            write_batchsize=write_batchsize, write_timeout=write_timeout, output_dir=output_dir
        )
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
