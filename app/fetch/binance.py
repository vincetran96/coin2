"""Fetch data from Binance

Rate limit:
  - https://binance-docs.github.io/apidocs/spot/en/#limits
  - https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#websocket-limits
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

from common.consts import KAFKA_BATCHSIZE, LOG_FORMAT
from common.kafka import create_producer
from app.consts import ASYNCIO_SLEEP, REST_TIMEOUT
from app.fetch.kafka import send_to_kafka


HTTP_URI = "https://api.binance.com/api/v3"
WS_URI = "wss://stream.binance.com:443/ws"
KAFKA_TOPIC = "ws-binance"  # Use OS env var
BACKOFF_TIME = 3.0
SLEEP_BETWEEN_CONNECTIONS = 0.6  # Every 5 mins is limited to 500 connections
MAX_SYMBOLS_PER_CONNECTION = 200  # Manually adjusted


def get_symbols(limit: int = 1000) -> List[str]:
    """Get all symbols
    Source: https://binance-docs.github.io/apidocs/spot/en/#exchange-information

    Args:
        limit (int): Number of symbols to return

    Returns:
        List[str]

    """
    resp = requests.get(f"{HTTP_URI}/exchangeInfo", timeout=REST_TIMEOUT)
    resp.raise_for_status()
    return [d['symbol'] for d in resp.json()['symbols']][:limit]


async def _subscribe(symbols: List[str], con_id: int = 0) -> NoReturn:
    """Subscribe to symbols candle lines data, 1m interval

    Source:
      - https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams-for-utc
      - https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#klinecandlestick-streams-for-utc

    For each message received,
      - Check for the confirmation of whether our subscribe message is successful
      - Else, process the data

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID

    """
    backoff_delay = BACKOFF_TIME
    kafka_producer = create_producer()
    async for con in websockets.connect(uri=WS_URI):
        try:
            await con.send(
                message=json.dumps({
                    "method": "SUBSCRIBE",
                    "id": con_id,
                    "params": [
                        f"{symbol.lower()}@kline_1s"
                        for symbol in symbols
                    ]
                })
            )
            logging.info(f"Connection {con_id}: Successful, num symbols: {len(symbols)}")

            backoff_delay = BACKOFF_TIME
            data_list = []
            async for msg_ in con:
                msg = json.loads(msg_)
                if (
                    ("result" in msg and msg["result"])
                    or ("error" in msg)
                ):
                    raise ValueError(f"Something wrong with our subscribe msg:\n{msg}")
                elif "s" not in msg:
                    pass
                else:
                    data = {
                        'exchange': 'binance',
                        'symbol': msg['s'],
                        'timestamp': int(msg['k']['t']),
                        'open_': msg['k']['o'],
                        'high_': msg['k']['h'],
                        'low_': msg['k']['l'],
                        'close_': msg['k']['c'],
                        'volume_': msg['k']['v'],
                    }
                    data_list.append(data)
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


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    symbols = get_symbols(limit=None)
    batchsize = MAX_SYMBOLS_PER_CONNECTION
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
