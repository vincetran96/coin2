"""Fetch data from Bitfinex
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
from app.fetch.kafka import send_to_kafka


HTTP_URI = "https://api-pub.bitfinex.com/v2"  # Use OS env var
WS_URI = "wss://api-pub.bitfinex.com/ws/2"  # Use OS env var
KAFKA_TOPIC = "ws-bitfinex"  # Use OS env var
BACKOFF_MIN_SECS = 3.0
ASYNCIO_SLEEPTIME = 0.05
SLEEP_BETWEEN_CONNECTIONS = 3  # Each minute is limited to 20 connections
MAX_CHANNELS_PER_CONNECTION = 25


def get_symbols(limit: int = 1000) -> List[str]:
    """Get all symbols

    Args:
        limit (int): Number of symbols to return

    Returns:
        List[str]
    """
    resp = requests.get(f"{HTTP_URI}/conf/pub:list:pair:exchange", timeout=60)
    resp.raise_for_status()
    return resp.json()[0][:limit]


async def _subscribe(symbols: List[str], con_id: int) -> NoReturn:
    """Subscribe to symbols candle lines data, 1m interval

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID
    """
    backoff_delay = BACKOFF_MIN_SECS
    kafka_producer = create_producer()
    channel_symbol = {}

    async def _subscribe_one(symbol: str, con: Any):
        """Subscribe to one symbol"""
        await con.send(
            message=json.dumps({
                "event": "subscribe",
                "channel": "candles",
                "key": f"trade:1m:t{symbol}"
            })
        )

    while True:
        try:
            async with websockets.connect(uri=WS_URI) as con:
                await asyncio.gather(*(_subscribe_one(symbol, con) for symbol in symbols))
                logging.info(f"Connection {con_id}: Successful, symbols: {symbols}")

                backoff_delay = BACKOFF_MIN_SECS
                data_list = []
                async for msg_ in con:
                    msg = json.loads(msg_)
                    if isinstance(msg, dict):
                        if "event" in msg:
                            if msg["event"] == "subscribed":
                                channel_symbol[msg["chanId"]] = msg["key"]
                            elif msg["event"] == "error":
                                raise ValueError("Something wrong with our subscribe msg")
                    elif isinstance(msg, list):
                        if len(msg) == 2 and len(msg[1]) == 6:
                            data = {
                                'symbol': channel_symbol[msg[0]],
                                'timestamp': int(msg[1][0]),
                                'open_': msg[1][1],
                                'high_': msg[1][3],
                                'low_': msg[1][4],
                                'close_': msg[1][2],
                                'volume_': msg[1][5],
                            }
                            # logging.info(f"Data: {data}")
                            data_list.append(data)
                    if len(data_list) >= KAFKA_BATCHSIZE:
                        logging.info(f"Connection {con_id}: Sending data list to kafka")
                        send_to_kafka(
                            producer=kafka_producer, topic=KAFKA_TOPIC, data_list=data_list
                        )
                        data_list = []
                    await asyncio.sleep(ASYNCIO_SLEEPTIME)

        except (ConnectionClosed, InvalidStatusCode) as exc:
            logging.error(f"Connection {con_id}: Raised exception: {exc} - reconnecting...")
            await asyncio.sleep(backoff_delay)
            backoff_delay *= (1 + random())


def run_subscribe(symbols: List[str], con_id: int):
    """Run a single subscribe connection"""
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
            logging.info(f"Sleeping for {SLEEP_BETWEEN_CONNECTIONS}s")
            time.sleep(SLEEP_BETWEEN_CONNECTIONS)
        # for future in futures:
        #     future.result()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    run_subscribe_threads(
        symbols=get_symbols(limit=None), batchsize=MAX_CHANNELS_PER_CONNECTION
    )
