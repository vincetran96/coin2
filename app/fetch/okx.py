"""Fetch data from OKX

Rate limit: https://www.okx.com/docs-v5/en/#overview-websocket-overview
"""
# pylint: disable-all
# noqa: E501
import asyncio
import json
import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor
from random import random
from typing import Any, List, NoReturn

import requests
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

from common.consts import KAFKA_BATCHSIZE, LOG_FORMAT
from common.kafka import create_producer
from app.consts import ASYNCIO_SLEEP, REST_TIMEOUT
from app.fetch.kafka import send_to_kafka


HTTP_URI = "https://www.okx.com/api/v5"
WS_URI = "wss://wsaws.okx.com:8443/ws/v5/business"
KAFKA_TOPIC = "ws-okx"  # Use OS env var
BACKOFF_TIME = 3.0
SLEEP_BETWEEN_CONNECTIONS = 1/3  # Each second is limited to 3 connections
MAX_SYMBOLS_PER_CONNECTION = 200  # Manually adjusted


def get_symbols(limit: int = 1000, inst_type: str = "SPOT") -> List[str]:
    """Get all symbols

    Args:
        limit (int): Number of symbols to return
        inst_type (str): Instance type
            - SPOT, MARGIN

    Returns:
        List[str]

    """
    resp = requests.get(f"{HTTP_URI}/public/instruments?instType={inst_type}", timeout=REST_TIMEOUT)
    resp.raise_for_status()
    return [d['instId'] for d in resp.json()['data']][:limit]


async def _subscribe(symbols: List[str], con_id: int) -> NoReturn:
    """Subscribe to symbols candle lines data, 1m interval

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID

    """
    backoff_delay = BACKOFF_TIME
    kafka_producer = create_producer()

    while True:
        try:
            async with websockets.connect(uri=WS_URI, ping_timeout=60) as con:
                await con.send(
                    message=json.dumps({
                        "op": "subscribe",
                        "args": [
                            {
                                "channel": "candle1m",
                                "instId": symbol
                            }
                            for symbol in symbols
                        ]
                    })
                )
                logging.info(f"Connection {con_id}: Successful, num symbols: {len(symbols)}")

                backoff_delay = BACKOFF_TIME
                data_list = []
                async for msg_ in con:
                    msg = json.loads(msg_)
                    if isinstance(msg, dict):
                        if "event" in msg:
                            if msg["event"] == "subscribe":
                                # logging.warning(f"Received non-error msg, probably confirmation:\n{msg}")
                                pass
                            else:
                                raise ValueError("Something wrong with our subscribe msg")
                        elif ("arg" in msg) and ("data" in msg):
                            data = {
                                'exchange': 'okx',
                                'symbol': msg['arg']['instId'],
                                'timestamp': int(msg['data'][0][0]),
                                'open_': msg['data'][0][1],
                                'high_': msg['data'][0][2],
                                'low_': msg['data'][0][3],
                                'close_': msg['data'][0][4],
                                'volume_': msg['data'][0][5],
                            }
                            data_list.append(data)
                    else:
                        # Send the remaining data_list to kafka?
                        raise ValueError(f"Something wrong with received msg:\n{msg}")
                    if len(data_list) >= KAFKA_BATCHSIZE:
                        logging.info(f"Connection {con_id}: Sending data list to kafka")
                        send_to_kafka(
                            producer=kafka_producer, topic=KAFKA_TOPIC, data_list=data_list
                        )
                        data_list = []
                    await asyncio.sleep(ASYNCIO_SLEEP)

        except (ConnectionClosed, InvalidStatusCode) as exc:
            logging.error(f"Connection {con_id}: Raised exception: {exc} - reconnecting...")
            await asyncio.sleep(backoff_delay)
            backoff_delay *= (1 + random())


def run_subscribe(symbols: List[str], con_id: int):
    """Run a single subscribe connection

    i.e., subscribe to `symbols` with a new connection

    """
    asyncio.run(_subscribe(symbols=symbols, con_id=con_id))


def run_subscribe_threads(symbols: List[str], batchsize: int):
    """Run subscribe in threads

    Args:
        symbols (List[str]): List of symbols
        batchsize (int): Number of symbols to subscribe per connection

    """
    max_workers = math.ceil(len(symbols) / batchsize)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(0, len(symbols), batchsize):
            futures.append(
                executor.submit(
                    run_subscribe,
                    symbols=symbols[i:i + batchsize],
                    con_id=int(i / batchsize)
                )
            )
            logging.info(f"Sleeping for {SLEEP_BETWEEN_CONNECTIONS:.2f}s")  # Delay submitting futures
            time.sleep(SLEEP_BETWEEN_CONNECTIONS)


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    symbols = get_symbols(limit=None)
    batchsize = MAX_SYMBOLS_PER_CONNECTION
    max_workers = math.ceil(len(symbols) / batchsize)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(symbols), batchsize):
            executor.submit(
                run_subscribe,
                symbols=symbols[i:i + batchsize],
                con_id=int(i / batchsize)
            )
            logging.info(f"Sleeping for {SLEEP_BETWEEN_CONNECTIONS:.2f}s")  # Delay submitting futures
            time.sleep(SLEEP_BETWEEN_CONNECTIONS)
