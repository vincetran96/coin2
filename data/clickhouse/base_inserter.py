"""Code containing logic to insert data to ClickHouse
"""
from typing import Dict, List

from clickhouse_driver import Client

from common.configs import Config, OsVariable
from data.clickhouse.connections import ClickHouseClient, clickhouse_connection
from data.interfaces import DataInserter


class ClickHouseBaseInserter(ClickHouseClient, DataInserter):
    """
    Base inserter to ClickHouse that can be used as a context manager
    """
    def __init__(self):
        ClickHouseClient.__init__(self)
        DataInserter.__init__(self)

    def _insert(self, tbl_name: str, data: List[Dict], field_names: List[str], **kwargs) -> None:
        """Private method
        
        Insert data into ClickHouse table

        Note that the practice of inserting native Python types (List[Dict]) is not very efficient.

        Args:
            tbl_name (str): The name of the ClickHouse table to insert data into
            data (List[Dict]): The data to be inserted into ClickHouse
            field_names (List[str]): The fields of the ClickHouse table to insert data into
        """
        if self._con is None:
            raise ValueError("ClickHouse client is not connected")
        self._con.execute(
            f"INSERT INTO {tbl_name} ({', '.join(field_names)}) VALUES ",
            data,
        )
