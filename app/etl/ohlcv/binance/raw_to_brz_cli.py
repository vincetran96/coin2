"""Script to transform and move data from Bronze to Silver for OHLCV from Binance source
"""
import json
import logging
import sys
from typing import Optional

from pyiceberg.catalog import Catalog

from app.configs import INSERTER_KAFKA_GROUP_ID
from app.kafka import KafkaAccDbInserter
from common.consts import KAFKA_CONSUME_BATCHSIZE, LOG_FORMAT
from common.catalog import create_namespace_if_not_exists, get_catalog
from data.iceberg.base_inserter import IcebergBaseInserter
from data.iceberg.consts import BINANCE_NAMESPACE
from models.iceberg.ohlcv.brz.binance import BinanceOHLCVBrz


def run_raw_to_brz(catalog: Catalog, *, max_runtime: Optional[float] = None) -> None:
    """Main function to run the ETL process

    Args:
        max_runtime (Optional[float]): Maximum runtime in seconds for the Kafka consumer loop
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, stream=sys.stdout)

    create_namespace_if_not_exists(BINANCE_NAMESPACE)
    brz_tbl_model = BinanceOHLCVBrz(catalog=catalog)
    brz_tbl_model.create_table_if_not_exists()

    inserter = KafkaAccDbInserter(
        topic="ws-binance",
        batchsize=KAFKA_CONSUME_BATCHSIZE,
        wait_timeout=60,
        group_id=INSERTER_KAFKA_GROUP_ID,
        target_tbl=brz_tbl_model.tbl_identifier,
        db_inserter=IcebergBaseInserter(mode="append"),
        extract_fields=["exchange", "symbol", "timestamp", "open_", "high_", "low_", "close_", "volume_"],
        msg_processor=json.loads
    )

    inserter.run_consume(max_runtime=max_runtime)


if __name__ == "__main__":
    run_raw_to_brz(catalog=get_catalog(), max_runtime=15 * 60)
