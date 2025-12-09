"""Configs for app
"""
KAFKA_FETCH_TOPICS = [
    "ws-binance",
    "ws-bitfinex",
    "ws-bybit",
    "ws-okx"
]

INSERTER_KAFKA_GROUP_ID = "inserter-consumer"
