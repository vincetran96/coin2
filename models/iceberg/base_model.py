"""Base model to be used for different exchanges' tables
"""
import logging

from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder

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

        self.catalog = get_catalog()
        self.tbl_object: Table | None = None

    @property
    def tbl_identifier(self) -> str:
        return f"{self.namespace}.{self.tbl_name}"

    def create_table_if_not_exists(self) -> None:
        """Create the table if it doesn't exist
        """
        try:
            self.tbl_object = self.catalog.create_table_if_not_exists(
                identifier=self.tbl_identifier,
                schema=self.tbl_schema,
            )
            logging.info(f"Created table: {self.tbl_identifier}")
        except Exception as exc:
            logging.error(f"Failed to create table {self.tbl_identifier}: {exc}")
            raise
