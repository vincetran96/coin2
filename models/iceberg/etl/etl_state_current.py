import pyiceberg.types as types
from pyiceberg.catalog import Catalog
from pyiceberg.schema import Schema

from models.consts import CHG_TS_COL
from models.iceberg.base_model import BaseModel


NAMESPACE = "etl"


class ETLStateCurrent(BaseModel):
    """
    Model representing the ETL state current table.
    """
    def __init__(self, catalog: Catalog) -> None:
        super().__init__(namespace=NAMESPACE, table_name="etl_state_current", catalog=catalog)

        self.tbl_schema = Schema(
            types.NestedField(field_id=1, name="job_name", field_type=types.StringType(), required=True),
            types.NestedField(field_id=2, name="source", field_type=types.StringType(), required=True),
            types.NestedField(field_id=3, name="source_identifier", field_type=types.StringType(), required=True),
            types.NestedField(field_id=4, name="dest_identifier", field_type=types.StringType(), required=True),
            types.NestedField(field_id=5, name="last_src_change_tstamp", field_type=types.TimestamptzType(), required=True),
            
            # Audit columns
            types.NestedField(field_id=6, name=CHG_TS_COL, field_type=types.TimestamptzType(), required=True),

            identifier_field_ids=[1]
        )
