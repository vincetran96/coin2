"""Script to transform and move data from Bronze to Silver for OHLCV from Binance source
"""
import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

import daft
import pyarrow as pa
import pyarrow.compute as pc
from daft import DataType, col, lit
from pyiceberg.catalog import Catalog
from pyiceberg.table import Table as PyIcebergTable

from app.etl.utils.daft import add_audit_columns, get_last_src_change_tstamp
from common.consts import LOG_FORMAT
from common.catalog import create_namespace_if_not_exists, get_catalog
from data.iceberg.base_inserter import IcebergBaseInserter
from data.iceberg.consts import BINANCE_NAMESPACE, ETL_NAMESPACE
from models.consts import CHG_TS_COL
from models.iceberg.etl.etl_state_current import ETLStateCurrent
from models.iceberg.ohlcv.brz.binance import BinanceOHLCVBrz
from models.iceberg.ohlcv.slv.binance import BinanceOHLCVSlv


# Job information
JOB_NAME = "binance_ohlcv_brz_to_slv"
SOURCE = "iceberg"
SOURCE_IDENTIFIER = "binance.ohlcv_brz"
DEST_IDENTIFIER = "binance.ohlcv_slv"

TS_BATCH_STEP = timedelta(minutes=30)
DF_BATCHSIZE = 1_000_000


def _select_and_cast(input_df: daft.DataFrame) -> daft.DataFrame:
    """Select and cast columns from the input DataFrame

    We take the change tstamp column as-is from the source table.

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
            col(CHG_TS_COL).alias("src_change_tstamp"),
        )
    )


def run_brz_to_slv(catalog: Catalog) -> None:
    """Main function to run the ETL process

    We use Iceberg `etl.etl_state_current` as the watermark store.
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, stream=sys.stdout)

    create_namespace_if_not_exists(ETL_NAMESPACE)
    create_namespace_if_not_exists(BINANCE_NAMESPACE)

    etl_state_tbl_model = ETLStateCurrent(catalog=catalog)
    brz_tbl_model = BinanceOHLCVBrz(catalog=catalog)
    slv_tbl_model = BinanceOHLCVSlv(catalog=catalog)
    etl_state_tbl_model.create_table_if_not_exists()
    brz_tbl_model.load_table()
    slv_tbl_model.create_table_if_not_exists()

    etl_state_tbl_object: PyIcebergTable = etl_state_tbl_model.tbl_object
    brz_tbl_object: PyIcebergTable = brz_tbl_model.tbl_object
    slv_tbl_object: PyIcebergTable = slv_tbl_model.tbl_object

    brz_df = daft.read_iceberg(brz_tbl_object)
    etl_state_df = daft.read_iceberg(etl_state_tbl_object)
    last_src_ts = get_last_src_change_tstamp(etl_state_df, job_name=JOB_NAME)

    delta_df = brz_df
    if last_src_ts is None:
        logging.info("No existing ETL state found; will backfill from all available Bronze data.")
    else:
        logging.info(f"Last watermark from ETL state: {last_src_ts}")
        delta_df = brz_df.filter(col(CHG_TS_COL) > lit(last_src_ts))
    
    logging.info("Processing new records from Bronze...")
    delta_df = delta_df.into_batches(DF_BATCHSIZE)

    # Compute max source watermark from the delta, to store into ETL state at end
    max_src_change_tstamp: Optional[datetime] = None
    for part in delta_df.select(CHG_TS_COL).iter_partitions():
        pa_tbl = part.to_arrow()
        if pa_tbl.num_rows == 0:
            continue

        chunk_max = pc.max(pa_tbl[CHG_TS_COL]).as_py()  # type: ignore[attr-defined]
        if isinstance(chunk_max, datetime):
            if max_src_change_tstamp is None or chunk_max > max_src_change_tstamp:
                max_src_change_tstamp = chunk_max

    if max_src_change_tstamp is None:
        logging.info("No new rows found in Bronze delta; exiting.")
        return

    # Perform transformations
    delta_df = (
        delta_df
        .transform(_select_and_cast)
        .transform(add_audit_columns)
    )

    delta_df.write_iceberg(slv_tbl_object, mode="append")

    # Write ETL state
    state_row = {
        "job_name": JOB_NAME,
        "source": SOURCE,
        "source_identifier": SOURCE_IDENTIFIER,
        "dest_identifier": DEST_IDENTIFIER,
        "last_src_change_tstamp": max_src_change_tstamp
    }
    with IcebergBaseInserter(catalog=catalog, mode="upsert") as inserter:
        inserter.insert(
            tbl_name=etl_state_tbl_model.tbl_identifier,
            data=[state_row],
            field_names=list(state_row.keys()),
        )
    logging.info(f"Updated ETL state watermark to: {max_src_change_tstamp}")


if __name__ == "__main__":
    run_brz_to_slv(catalog=get_catalog())
