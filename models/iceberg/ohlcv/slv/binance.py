import pyiceberg.types as types
from pyiceberg.schema import Schema

from models.base_model import BaseModel


NAMESPACE = "binance"


class BinanceOHLCVSlv(BaseModel):
    def __init__(self) -> None:
        super().__init__(namespace=NAMESPACE, table_name="ohlcv_slv")

        self.tbl_schema = Schema(
            types.NestedField(field_id=1, name="exchange", field_type=types.StringType(), required=True),
            types.NestedField(field_id=2, name="symbol", field_type=types.StringType(), required=True),
            types.NestedField(field_id=3, name="timestamp", field_type=types.TimestampType(), required=True),
            types.NestedField(field_id=4, name="open", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=5, name="high", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=6, name="low", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=7, name="close", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=8, name="volume", field_type=types.DoubleType(), required=False),
        )
