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

from common.consts import LOG_FORMAT
from app.etl.watch_raw import watch_dir


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Watch filesystem changes in a directory and push to Kafka")
    p.add_argument("--dir", type=str, required=True, help="Directory to watch")
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    args = _parse_args()
    dir = args.dir

    try:
        watch_dir(dir=dir)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
