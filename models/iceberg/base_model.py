"""Base model to be used for different exchanges' tables
"""
import logging

from pyiceberg.partitioning import PARTITION_FIELD_ID_START, PartitionField, PartitionSpec, UNPARTITIONED_PARTITION_SPEC
from pyiceberg.schema import Schema
from pyiceberg.table import Table
from pyiceberg.table.sorting import SortOrder, UNSORTED_SORT_ORDER
from pyiceberg.transforms import parse_transform

from common.catalog import get_catalog


class BaseModel:
    def __init__(
        self,
        namespace: str,
        table_name: str
    ) -> None:
        """
        Args:
            namespace (str): 
            table_name (str): 
        """
        self.namespace = namespace
        self.tbl_name = table_name

        # Schema to be implemented in subclass
        self.tbl_schema: Schema | None = None
        
        # Optional: set in subclass to partition the table
        self.partition_spec: PartitionSpec = UNPARTITIONED_PARTITION_SPEC

        # Optional: set in subclass to define write sort order
        self.sort_order: SortOrder = UNSORTED_SORT_ORDER

        self.catalog = get_catalog()
        self.tbl_object: Table | None = None

    @property
    def tbl_identifier(self) -> str:
        return f"{self.namespace}.{self.tbl_name}"

    def load_table(self) -> None:
        """Load the table from the catalog
        """
        self.tbl_object = self.catalog.load_table(self.tbl_identifier)

    def create_table_if_not_exists(self) -> None:
        """Create the table if it doesn't exist
        """
        try:
            if self.tbl_schema is None:
                raise ValueError(f"tbl_schema is not set for model {type(self).__name__}")

            self.tbl_object = self.catalog.create_table_if_not_exists(
                identifier=self.tbl_identifier,
                schema=self.tbl_schema,
                partition_spec=self.partition_spec,
                sort_order=self.sort_order,
            )
            logging.info(f"Created table: {self.tbl_identifier}")
        except Exception as exc:
            logging.error(f"Failed to create table {self.tbl_identifier}: {exc}")
            raise

    def set_partition_spec(self, *parts: tuple[str, str] | tuple[str, str, str]) -> None:
        """Helper to define Iceberg partitioning by column name

        Examples:
            model.set_partition_spec(
                ("symbol", "identity"),
                ("event_tstamp", "day"),
            )

        Args:
            - parts:
                Tuples of `(column_name, transform)` or `(column_name, transform, partition_field_name)`.
                Transform strings following Iceberg syntax, e.g. "identity", "month", "day", "hour", "bucket[16]", "truncate[8]".
        """
        if self.tbl_schema is None:
            raise ValueError("tbl_schema must be set before defining partition_spec")

        fields: list[PartitionField] = []
        next_field_id = PARTITION_FIELD_ID_START

        for i, part in enumerate(parts):
            if len(part) == 2:
                col_name, transform_str = part
                if transform_str == "identity":
                    part_name = col_name
                else:
                    # e.g. "event_tstamp_day", "symbol_bucket_16"
                    safe_transform = (
                        transform_str.replace("[", "_")
                        .replace("]", "")
                        .replace(",", "_")
                        .replace(" ", "")
                    )
                    part_name = f"{col_name}_{safe_transform}"
            else:
                col_name, transform_str, part_name = part

            source_id = self.tbl_schema.find_field(col_name).field_id
            fields.append(
                PartitionField(
                    source_id=source_id,
                    field_id=next_field_id + i,
                    transform=parse_transform(transform_str),
                    name=part_name,
                )
            )

        self.partition_spec = PartitionSpec(*fields)
