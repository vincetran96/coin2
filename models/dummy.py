from pyiceberg.schema import Schema
import pyiceberg.types as types

from models.base_model import BaseModel


class DummyTable(BaseModel):
    def __init__(self) -> None:
        super().__init__(namespace="binance", table_name="dummy")

        self.tbl_schema = Schema(
            types.NestedField(1, name="exchange", field_type=types.StringType(), required=True),
            types.NestedField(2, name="timestamp", field_type=types.TimestampType(), required=True)
        )
