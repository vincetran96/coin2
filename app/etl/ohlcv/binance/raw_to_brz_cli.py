"""Script to transform and move data from Bronze to Silver for OHLCV from Binance source
"""
import json
import logging
from typing import Dict

import daft
import daft.functions as F
from daft import col, DataType

from app.configs import INSERTER_KAFKA_GROUP_ID
from app.kafka import KafkaAccDbInserter
from common.consts import KAFKA_CONSUME_BATCHSIZE, LOG_FORMAT
from common.catalog import get_catalog, create_namespace_if_not_exists
from data.iceberg.base_inserter import IcebergBaseInserter
from data.iceberg.consts import BINANCE_NAMESPACE
from models.iceberg.ohlcv.brz.binance import BinanceOHLCVBrz


def process_msg(msg: str) -> Dict:
    """Process a message from Binance topic
    """
    msg_j = json.loads(msg)
    return {
        "exchange": msg_j["exchange"],
        "symbol": msg_j["symbol"],
        "timestamp": int(msg_j["timestamp"]),
        "open_": float(msg_j["open_"]),
        "high_": float(msg_j["high_"]),
        "low_": float(msg_j["low_"]),
        "close_": float(msg_j["close_"]),
        "volume_": float(msg_j["volume_"]),
    }


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    create_namespace_if_not_exists(BINANCE_NAMESPACE)
    brz_tbl_model = BinanceOHLCVBrz()
    brz_tbl_model.create_table_if_not_exists()

    inserter = KafkaAccDbInserter(
        topic="ws-binance",
        batchsize=KAFKA_CONSUME_BATCHSIZE,
        wait_timeout=60,
        group_id=INSERTER_KAFKA_GROUP_ID,
        target_tbl=brz_tbl_model.tbl_identifier,
        db_inserter=IcebergBaseInserter(mode="append"),
        extract_fields=["exchange", "symbol", "timestamp", "open_"],
        msg_processor=json.loads
    )

    inserter.run_consume()
