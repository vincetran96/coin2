"""Fetch data from Binance
"""
# pylint: disable-all
# noqa: E501
import asyncio
import json
import logging
from random import random
from typing import List, NoReturn

import requests
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

from common.consts import KAFKA_BATCHSIZE, LOG_FORMAT
from common.kafka import create_producer
from app.fetch.kafka import send_to_kafka


HTTP_URI = "https://api.binance.com/api/v3"  # Use OS env var
WS_URI = "wss://stream.binance.com:9443/ws"  # Use OS env var
KAFKA_TOPIC = "ws-binance"  # Use OS env var
BACKOFF_MIN_SECS = 2.0
ASYNCIO_SLEEPTIME = 0.05


def get_symbols(limit: int = 1000) -> List[str]:
    """Get all symbols

    Args:
        limit (int): Number of symbols to return

    Returns:
        List[str]
    """
    resp = requests.get(f"{HTTP_URI}/exchangeInfo", timeout=60)
    resp.raise_for_status()
    return [d['symbol'] for d in resp.json()['symbols']][:limit]


async def _subscribe(symbols: List[str], con_id: int = 0) -> NoReturn:
    """Subscribe to symbols candle lines data, 1m interval

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID
    """
    backoff_delay = BACKOFF_MIN_SECS
    kafka_producer = create_producer()
    while True:
        try:
            async with websockets.connect(uri=WS_URI) as con:
                await con.send(
                    message=json.dumps({
                        "method": "SUBSCRIBE",
                        "params": [f"{symbol.lower()}@kline_1m" for symbol in symbols],
                        "id": con_id
                    })
                )
                logging.info(f"Connection {con_id}: Successful, symbols: {symbols}")

                backoff_delay = BACKOFF_MIN_SECS
                data_list = []
                async for msg_ in con:
                    msg = json.loads(msg_)
                    if isinstance(msg, dict):
                        if (
                            ("result" in msg and msg["result"])
                            or ("error" in msg)
                        ):
                            raise ValueError("Something wrong with our subscribe msg")
                        elif "s" not in msg:
                            logging.warning("Something wrong with received msg, skip it")
                        else:
                            data = {
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
                    await asyncio.sleep(ASYNCIO_SLEEPTIME)

        except (ConnectionClosed, InvalidStatusCode) as exc:
            logging.error(f"Connection {con_id}: Raised exception: {exc} - reconnecting...")
            await asyncio.sleep(backoff_delay)
            backoff_delay *= (1 + random())


async def subscribe_symbols(symbols: List, batchsize: int):
    """Subscribe to symbols in batch"""
    await asyncio.gather(*(
        _subscribe(symbols=symbols[i:i + batchsize], con_id=int(i / batchsize))
        for i in range(0, len(symbols), batchsize)
    ))


def run_subscribe(symbols: List[str], batchsize: int):
    """Run subscribe

    Args:
        symbols (List[str]): List of symbols
        batchsize (int): Number of symbols to subscribe per connection

    """
    asyncio.run(subscribe_symbols(symbols=symbols, batchsize=batchsize))


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    run_subscribe(
        symbols=get_symbols(limit=None), batchsize=100
    )
