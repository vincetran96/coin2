"""Code containing logic to execute SQL queries on ClickHouse
"""
from typing import Any, List
from data.clickhouse.connections import ClickHouseClient


class ClickHouseBaseExecutor(ClickHouseClient):
    """
    Base query executor on ClickHouse that can be used as a context manager
    """
    def __init__(self):
        super().__init__()

    def execute(self, query: str, **kwargs) -> List[Any]:
        """Execute a SQL query on ClickHouse

        Args:
            query (str): The SQL query to execute
            **kwargs: Additional keyword arguments to pass to the `clickhouse_driver.Client`'s execute method
        """
        if self._con is None:
            raise ValueError("ClickHouse client is not connected")
        result = []
        sub_queries = query.split(";")
        for sub_query in sub_queries:
            sub_query = sub_query.strip()
            if sub_query:
                result.append(self._con.execute(sub_query, **kwargs))
        return result
