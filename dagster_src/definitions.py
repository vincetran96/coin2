"""Dagster top-leveldefinitions
"""
from dagster import Definitions

from dagster_src.assets.ohlcv.binance import binance_ohlcv_brz, binance_ohlcv_slv, binance_ohlcv_clickhouse
from dagster_src.jobs import binance_ohlcv_brz_job, binance_ohlcv_slv_ch_job
from dagster_src.resources import ClickHouseResource, IcebergResource
from dagster_src.schedules import binance_ohlcv_brz_20m, binance_ohlcv_slv_ch_5m


defs = Definitions(
    resources={
        "iceberg": IcebergResource(),
        "clickhouse": ClickHouseResource(),
    },
    assets=[
        binance_ohlcv_brz, binance_ohlcv_slv, binance_ohlcv_clickhouse
    ],
    jobs=[
        binance_ohlcv_brz_job, binance_ohlcv_slv_ch_job
    ],
    schedules=[
        binance_ohlcv_brz_20m, binance_ohlcv_slv_ch_5m
    ],
)
