"""Quick check if data is flowing to Iceberg
"""
import logging

from data.iceberg.db import preview_table

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    preview_table(namespace="binance", tbl_name="ohlcv_brz")
