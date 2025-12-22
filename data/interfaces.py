"""Abstract interface acting as a layer on top of 
specific implementations of database operators (e.g., inserters)
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal

# from data.clickhouse.base_inserter import BaseInserter as CHBaseInserter
# from data.iceberg.base_inserter import BaseInserter as IBBaseInserter


AVAILABLE_INSERTER_TYPES = [
    "clickhouse",
    "iceberg"
]


class DataInserter(ABC):
    """Abstract base class for inserting data
    """
    def __init__(
        self,
        mode: Literal["append", "overwrite"] = "append"
    ):
        self.mode = mode

    @abstractmethod
    def _insert(self, tbl_name: str, data: List[Dict], field_names: List[str], **kwargs):
        """
        Private method to be implemented

        Args:
            **kwargs: Implementation-specific parameters
        """
        pass

    def insert(self, tbl_name: str, data: List[Dict], field_names: List[str], **kwargs):
        """Public interface to insert data
        """
        self._insert(tbl_name=tbl_name, data=data, field_names=field_names, **kwargs)
        logging.info(f"Inserted {len(data)} records into table {tbl_name}!")
