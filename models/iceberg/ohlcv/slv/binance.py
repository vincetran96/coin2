import pyiceberg.types as types
from pyiceberg.schema import Schema

from models.consts import CHG_TS_COL
from models.iceberg.base_model import BaseModel


NAMESPACE = "binance"


class BinanceOHLCVSlv(BaseModel):
    """
    Model representing the Binance OHLCV Silver table.
    """
    def __init__(self) -> None:
        super().__init__(namespace=NAMESPACE, table_name="ohlcv_slv")

        self.tbl_schema = Schema(
            types.NestedField(field_id=1, name="exchange", field_type=types.StringType(), required=True),
            types.NestedField(field_id=2, name="symbol", field_type=types.StringType(), required=True),
            types.NestedField(field_id=3, name="event_tstamp", field_type=types.TimestampType(), required=True, doc="Timestamp of the event, in UTC"),
            types.NestedField(field_id=4, name="open", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=5, name="high", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=6, name="low", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=7, name="close", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=8, name="volume", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=9, name="src_change_tstamp", field_type=types.TimestamptzType(), required=True, doc="Timestamp of when the source record was changed, in UTC"),

            # Audit columns
            types.NestedField(field_id=10, name=CHG_TS_COL, field_type=types.TimestamptzType(), required=True),

            identifier_field_ids=[1, 2, 3]
        )

        # We set partitioning by source change timestamp because
        # this table is mainly used as a staging one before loading into Gold/other warehouses
        self.set_partition_spec(
            ("src_change_tstamp", "day", "src_change_date"),
            ("symbol", "bucket[32]", "symbol_bucket_32"),
        )
