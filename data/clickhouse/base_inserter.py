"""Code containing logic to insert data to ClickHouse
"""
from typing import Dict, List

from common.configs import Config, OsVariable
from data.connections import clickhouse_connection


class BaseInserter:
    """Base inserter to ClickHouse that can be used as a context manager
    """
    def __init__(self):
        self._con = None

    def connect(self):
        """Connect to ClickHouse db and assign a connection to its attr
        """
        self._con = clickhouse_connection(
            host=Config.os_get(key=OsVariable.CLICKHOUSE_HOST.value),
            port=Config.os_get(key=OsVariable.CLICKHOUSE_NATIVE_PORT.value),
            username=Config.os_get(key=OsVariable.APP_INSERTER_USER.value),
            password=Config.os_get(key=OsVariable.APP_INSERTER_PASSWORD.value)
        )

    def disconnect(self):
        """Disconnect from ClickHouse db
        """
        self._con.disconnect()

    def insert(self, table_name: str, data: List[Dict], table_fields: List[str]):
        """Insert data into ClickHouse table

        Args:
            table_name (str): The name of the ClickHouse table to insert data into
            data (List[Dict]): The data to be inserted into ClickHouse
            table_fields (List[str]): The fields of the ClickHouse table to insert data into
        """
        self._con.execute(
            f"INSERT INTO {table_name} ({', '.join(table_fields)}) VALUES ",
            data,
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.disconnect()
