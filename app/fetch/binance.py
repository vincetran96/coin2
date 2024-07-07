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
from app.consts import ASYNCIO_SLEEP, REST_TIMEOUT
from app.fetch.kafka import send_to_kafka


HTTP_URI = "https://api.binance.com/api/v3"
WS_URI = "wss://stream.binance.com:9443/ws"
KAFKA_TOPIC = "ws-binance"  # Use OS env var
BACKOFF_TIME = 2.0
MAX_SYMBOLS_PER_CONNECTION = 100


def get_symbols(limit: int = 1000) -> List[str]:
    """Get all symbols

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

    Args:
        symbols (List[str]): List of symbols
        con_id (int): Connection ID

    """
    backoff_delay = BACKOFF_TIME
    kafka_producer = create_producer()
    while True:
        try:
            async with websockets.connect(uri=WS_URI) as con:
                await con.send(
                    message=json.dumps({
                        "method": "SUBSCRIBE",
                        "id": con_id,
                        "params": [
                            f"{symbol.lower()}@kline_1m"
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
                        if (
                            ("result" in msg and msg["result"])
                            or ("error" in msg)
                        ):
                            raise ValueError("Something wrong with our subscribe msg")
                        elif "s" not in msg:
                            logging.warning(f"Received non-error msg, probably confirmation:\n{msg}")
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
        symbols=get_symbols(limit=None), batchsize=MAX_SYMBOLS_PER_CONNECTION
    )
