"""Fetch data from Bitfinex

Rate limit: https://docs.bitfinex.com/docs/requirements-and-limitations#websocket-rate-limits
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
from typing import List, NoReturn

import requests
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

from common.consts import KAFKA_PRODUCE_BATCHSIZE, KAFKA_PRODUCE_TIMEOUT, LOG_FORMAT
from app.consts import ASYNCIO_SLEEP, REST_TIMEOUT
from app.kafka import KafkaAccSender


HTTP_URI = "https://api-pub.bitfinex.com/v2"
WS_URI = "wss://api-pub.bitfinex.com/ws/2"
KAFKA_TOPIC = "ws-bitfinex"
BACKOFF_TIME = 3.0
SLEEP_BETWEEN_CONNECTIONS = 3  # Each minute is limited to 20 connections
MAX_CHANNELS_PER_CONNECTION = 25


def get_symbols(limit: int = 1000) -> List[str]:
    """Get all symbols

    Source: https://docs.bitfinex.com/reference/rest-public-conf#listing-requests

    Args:
        limit (int): Number of symbols to return

    Returns:
        List[str]

    """
    resp = requests.get(f"{HTTP_URI}/conf/pub:list:pair:exchange", timeout=REST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()[0][:limit]


async def _subscribe(symbols: List[str], con_id: int) -> NoReturn:
    """Subscribe to symbols candle lines data, 1m interval

    Source:
      - https://docs.bitfinex.com/reference/ws-public-candles

    For each message received,
      - Check for the confirmation of whether our subscribe message is successful
      - Else, process the data

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID

    """
    backoff_delay = BACKOFF_TIME
    kafka_acc_sender = KafkaAccSender(
        topic=KAFKA_TOPIC, batchsize=KAFKA_PRODUCE_BATCHSIZE, send_timeout=KAFKA_PRODUCE_TIMEOUT, key="symbol"
    )
    channel_symbol = {}

    async for con in websockets.connect(uri=WS_URI):
        try:
            for symbol in symbols:
                await con.send(
                    message=json.dumps({
                        "event": "subscribe",
                        "channel": "candles",
                        "key": f"trade:1m:t{symbol}"
                    })
                )
            logging.info(f"Connection {con_id}: Successful, num symbols: {len(symbols)}")

            backoff_delay = BACKOFF_TIME
            async for msg_ in con:
                msg = json.loads(msg_)
                if "event" in msg:
                    if msg["event"] == "subscribed":
                        channel_symbol[msg["chanId"]] = msg["key"]
                    elif msg["event"] == "info":
                        pass
                    else:
                        raise ValueError(f"Something wrong with our subscribe msg:\n{msg}")
                elif msg[1] == "hb":
                    pass
                elif isinstance(msg[1], list) and isinstance(msg[1][0], list):
                    pass
                else:
                    data = {
                        'exchange': 'bitfinex',
                        'symbol': channel_symbol[msg[0]],
                        'timestamp': int(msg[1][0]),
                        'open_': msg[1][1],
                        'high_': msg[1][3],
                        'low_': msg[1][4],
                        'close_': msg[1][2],
                        'volume_': msg[1][5],
                    }
                    kafka_acc_sender.add(data)
                kafka_acc_sender.send()
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


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    symbols = get_symbols(limit=None)
    batchsize = MAX_CHANNELS_PER_CONNECTION
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
        for future in futures:
            future.result()
