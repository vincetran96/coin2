"""For establishing connections to data sinks/sources/etc.
"""
import logging

from clickhouse_driver import Client

from common.configs import Config, OsVariable


def clickhouse_connection(
    host: str,
    port: int,
    username: str,
    password: str
) -> Client:
    """
    Create a connection to ClickHouse
    
    Returns:
        Client: ClickHouse client object
    """
    return Client(
        host=host,
        port=port,
        user=username,
        password=password
    )


class ClickHouseClient():
    """
    Base ClickHouse client that can be used as a context manager
    """
    def __init__(self):
        # Private
        self._con: Client | None = None

    def connect(self):
        """Connect to ClickHouse db and assign a connection to its attr
        """
        logging.info("Connecting to ClickHouse...")
        self._con = clickhouse_connection(
            host=Config.os_get(key=OsVariable.CLICKHOUSE_HOST.value),
            port=Config.os_get(key=OsVariable.CLICKHOUSE_NATIVE_PORT.value),
            username=Config.os_get(key=OsVariable.APP_INSERTER_USER.value),
            password=Config.os_get(key=OsVariable.APP_INSERTER_PASSWORD.value)
        )

    def disconnect(self):
        """Disconnect from ClickHouse db
        """
        if self._con is None:
            return
        self._con.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.disconnect()
