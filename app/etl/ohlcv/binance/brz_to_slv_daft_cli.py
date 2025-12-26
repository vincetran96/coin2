"""Script to transform and move data from Bronze to Silver for OHLCV from Binance source
"""
import logging
import sys
from datetime import datetime, timedelta, timezone

import daft
import pyarrow as pa
from daft import DataType, col, lit
from pyiceberg.table import Table as PyIcebergTable

from app.etl.utils.daft import iter_batches_by_ts, add_audit_columns
from common.consts import LOG_FORMAT
from common.catalog import create_namespace_if_not_exists
from data.iceberg.consts import BINANCE_NAMESPACE
from models.consts import CHG_TS_COL
from models.iceberg.ohlcv.brz.binance import BinanceOHLCVBrz
from models.iceberg.ohlcv.slv.binance import BinanceOHLCVSlv


TS_BATCH_STEP = timedelta(minutes=30)


def _get_delta_from_brz(
    brz_df: daft.DataFrame,
    slv_df: daft.DataFrame,
) -> daft.DataFrame:
    """Select delta from Bronze to Silver based on change timestamp
    
    Gets the maximum change timestamp from Silver and filters Bronze records
    where change_tstamp >= max_change_tstamp (incremental processing).

    Note that if we use `>=`, there will always be at least one record in the delta DataFrame.
    
    Args:
        brz_df: Daft DataFrame from Bronze table
        slv_df: 
        
    Returns:
        daft.DataFrame: Filtered DataFrame with only new records
    """
    # By default, return all records from Bronze
    delta_df = brz_df

    # Aggregate max and convert to PyArrow to get the value
    max_change_tstamp_df = slv_df.agg(col(CHG_TS_COL).max().alias("max_ts"))
    max_change_tstamp_pa = max_change_tstamp_df.to_arrow()
    
    if (max_change_tstamp_pa.num_rows > 0 and
        max_change_tstamp_pa["max_ts"][0].as_py() is not None):
        max_change_tstamp = max_change_tstamp_pa["max_ts"][0].as_py()
        delta_df = brz_df.filter(col(CHG_TS_COL) >= max_change_tstamp)
        logging.info(f"Max change_tstamp in Silver: {max_change_tstamp}")
    else:
        logging.info("Silver table exists but is empty")
    
    return delta_df


def _select_and_cast(input_df: daft.DataFrame) -> daft.DataFrame:
    """Select and cast columns from the input DataFrame

    Returns:
        daft.DataFrame:
    """
    return (
        input_df.select(
            "exchange",
            "symbol",
            col("timestamp").cast(DataType.timestamp(timeunit="ms", timezone="UTC")).alias("event_tstamp"),
            col("open_").cast(DataType.float64()).alias("open"),
            col("high_").cast(DataType.float64()).alias("high"),
            col("low_").cast(DataType.float64()).alias("low"),
            col("close_").cast(DataType.float64()).alias("close"),
            col("volume_").cast(DataType.float64()).alias("volume"),
        )
    )


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    create_namespace_if_not_exists(BINANCE_NAMESPACE)
    brz_tbl_model = BinanceOHLCVBrz()
    slv_tbl_model = BinanceOHLCVSlv()
    brz_tbl_model.load_table()
    slv_tbl_model.create_table_if_not_exists()
    
    brz_tbl_object: PyIcebergTable = brz_tbl_model.tbl_object
    slv_tbl_object: PyIcebergTable = slv_tbl_model.tbl_object
    brz_df = daft.read_iceberg(brz_tbl_object)
    slv_df = daft.read_iceberg(slv_tbl_object)
    slv_tbl_schema = slv_tbl_object.schema()
    slv_tbl_pa_schema = slv_tbl_schema.as_arrow()
    slv_tbl_columns = [col.name for col in slv_tbl_schema.columns]
    logging.info(f"Column names in Bronze: {brz_df.column_names}")

    # Get delta from Bronze based on change timestamp
    delta_df = _get_delta_from_brz(brz_df, slv_df)
    
    logging.info("Processing new records from Bronze...")
    for ts_batch in iter_batches_by_ts(input_df=delta_df, ts_col=CHG_TS_COL, step=TS_BATCH_STEP):
        # Perform transformations
        batch_df = (
            ts_batch.df
            .transform(_select_and_cast)
            .transform(add_audit_columns)
        )

        batch_df.write_iceberg(slv_tbl_object, mode="append")
