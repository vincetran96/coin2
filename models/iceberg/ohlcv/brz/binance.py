import pyiceberg.types as types
from pyiceberg.schema import Schema

from models.iceberg.base_model import BaseModel


NAMESPACE = "binance"


# TODO: Parsing using Kafka Connect may force us to not use `required`
class BinanceOHLCVBrz(BaseModel):
    """
    Model representing the Binance OHLCV Bronze table.
    """
    def __init__(self) -> None:
        super().__init__(namespace=NAMESPACE, table_name="ohlcv_brz")

        self.tbl_schema = Schema(
            types.NestedField(field_id=1, name="exchange", field_type=types.StringType(), required=False),
            types.NestedField(field_id=2, name="symbol", field_type=types.StringType(), required=False),
            types.NestedField(field_id=3, name="timestamp", field_type=types.LongType(), required=False),
            types.NestedField(field_id=4, name="open_", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=5, name="high_", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=6, name="low_", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=7, name="close_", field_type=types.DoubleType(), required=False),
            types.NestedField(field_id=8, name="volume_", field_type=types.DoubleType(), required=False),
        )
