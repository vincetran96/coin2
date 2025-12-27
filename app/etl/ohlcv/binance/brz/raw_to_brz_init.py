"""Script to init the Bronze layer for OHLCV from Binance source
"""
import logging

import daft
import daft.functions as F
from daft import col, DataType

from common.consts import LOG_FORMAT
from common.catalog import get_catalog, create_namespace_if_not_exists
from data.iceberg.consts import BINANCE_NAMESPACE
from models.iceberg.ohlcv.brz.binance import BinanceOHLCVBrz


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    create_namespace_if_not_exists(BINANCE_NAMESPACE)
    slv_tbl_model = BinanceOHLCVBrz()
    slv_tbl_model.create_table_if_not_exists()
