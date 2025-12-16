"""Script to transform and move data from Bronze to Silver for OHLCV from Binance source
"""
import logging

import daft
import daft.functions as F
from daft import col, DataType

from common.consts import LOG_FORMAT
from common.catalog import get_catalog, create_namespace_if_not_exists
from models.iceberg.ohlcv.slv.binance import NAMESPACE, BinanceOHLCVSlv


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    create_namespace_if_not_exists(NAMESPACE)
    slv_tbl_model = BinanceOHLCVSlv()
    slv_tbl_model.create_table_if_not_exists()

    # Bronze
    # TODO: Implement Bronze table model if needed
    catalog = get_catalog()
    brz_tbl_object = catalog.load_table(f"{NAMESPACE}.ohlcv_brz")
    brz_df = daft.read_iceberg(brz_tbl_object)
    logging.info(brz_df.column_names)

    # Transform and insert into Silver
    slv_df = (
        brz_df.select(
            "exchange", "symbol",
            col("timestamp").cast(DataType.timestamp(timeunit="ms")).alias("timestamp"),
            col("open_").cast(DataType.float64()).alias("open"),
            col("high_").cast(DataType.float64()).alias("high"),
            col("low_").cast(DataType.float64()).alias("low"),
            col("close_").cast(DataType.float64()).alias("close"),
            col("volume_").cast(DataType.float64()).alias("volume")
        )
    )

    slv_df.write_iceberg(slv_tbl_model.tbl_object, mode="append")
