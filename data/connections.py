"""For establishing connections to data sinks/sources/etc.
"""
from clickhouse_driver import Client


def clickhouse_connection(
    host: str,
    port: int,
    username: str,
    password: str,
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
        password=password,
    )
