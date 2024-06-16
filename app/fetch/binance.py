"""Fetch data from Binance
"""
# pylint: disable-all
# noqa: E501
import asyncio
import json
import logging
from random import random
from typing import Any, List, NoReturn

import requests
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

from common.kafka import acked, create_kafka_producer


HTTP_URI = "https://api.binance.com/api/v3"
WS_URI = "wss://stream.binance.com:9443/ws"
KAFKA_TOPIC = "ws-binance"  # Use OS env var
BACKOFF_MIN_SECS = 2.0
ASYNCIO_SLEEPTIME = 0.01


def send_to_kafka(producer: Any, topic: str, data_list: List[dict]):
    """Send data to Kafka"""
    for data in data_list:
        producer.produce(topic=topic, key=data['symbol'], value=json.dumps(data), callback=acked)
    producer.flush()


def get_symbols() -> List[str]:
    """Get all symbols

    Returns:
        List[str]
    """
    resp = requests.get(f"{HTTP_URI}/exchangeInfo", timeout=60)
    resp.raise_for_status()
    return [d['symbol'] for d in resp.json()['symbols']][:100]
    # return ["ETHBTC"]


async def subscribe_(symbols: List, i: int = 0) -> NoReturn:
    """Subscribe to symbols"""
    backoff_delay = BACKOFF_MIN_SECS
    kafka_producer = create_kafka_producer()
    while True:
        try:
            async with websockets.connect(WS_URI) as con:
                params = [f'{symbol.lower()}@kline_1m' for symbol in symbols]
                await con.send(
                    message=json.dumps({
                        "method": "SUBSCRIBE",
                        "params": params,
                        "id": i
                    })
                )
                logging.info(f"Connection {i}: Successful")
                backoff_delay = BACKOFF_MIN_SECS
                data_list = []
                while True:
                    msg = json.loads(await con.recv())
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
                            logging.info(f"Data:\n{data}")
                    if len(data_list) >= 100:
                        send_to_kafka(
                            producer=kafka_producer,
                            topic=KAFKA_TOPIC,
                            data_list=data_list
                        )
                    await asyncio.sleep(ASYNCIO_SLEEPTIME)
        except (ConnectionClosed, InvalidStatusCode) as exc:
            logging.error(f"Connection {i}: Raised exception: {exc} - reconnecting...")
            await asyncio.sleep(backoff_delay)
            backoff_delay *= (1 + random())


async def subscribe_symbols(symbols: List, batchsize: int = 100):
    """Subscribe to symbols in batch"""
    await asyncio.gather(
        *(
            subscribe_(symbols=symbols[i:i + batchsize], i=int(i / batchsize))
            for i in range(0, len(symbols), batchsize)
        )
    )


def run_subscribe():
    """Run subscribe"""
    asyncio.run(subscribe_symbols(symbols=get_symbols(), batchsize=100))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_subscribe()
