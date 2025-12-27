"""Common configs
"""
import os
from enum import Enum


class OsVariable(Enum):
    REDIS_HOST = "REDIS_HOST"
    REDIS_PASSWORD = "REDIS_PASSWORD"
    REDIS_USER = "REDIS_USER"
    REDIS_PORT = "REDIS_PORT"

    KAFKA_HOST = "KAFKA_HOST"
    KAFKA_PORT = "KAFKA_PORT"
    KAFKA_BOOTSTRAP_SERVER = "KAFKA_BOOTSTRAP_SERVER"

    MINIO_ENDPOINT = "MINIO_ENDPOINT"
    MINIO_ROOT_USER = "MINIO_ROOT_USER"
    MINIO_ROOT_PASSWORD = "MINIO_ROOT_PASSWORD"

    CATALOG_ENDPOINT = "CATALOG_ENDPOINT"

    CLICKHOUSE_HOST = "CLICKHOUSE_HOST"
    CLICKHOUSE_NATIVE_PORT = "CLICKHOUSE_NATIVE_PORT"
    CLICKHOUSE_HTTP_PORT = "CLICKHOUSE_HTTP_PORT"

    APP_INSERTER_USER = "APP_INSERTER_USER"
    APP_INSERTER_PASSWORD = "APP_INSERTER_PASSWORD"


class Config:
    """Config"""
    @staticmethod
    def os_get(key):
        """Get OS environment variable

        Args:
            key (str): Environment variable name

        Returns:
            Variable value
        """
        return os.getenv(key)
