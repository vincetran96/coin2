"""Common configs
"""
import os


class OsVariable:  # pylint: disable=too-few-public-methods
    REDIS_HOST = "REDIS_HOST"
    REDIS_PASSWORD = "REDIS_PASSWORD"
    REDIS_USER = "REDIS_USER"
    REDIS_PORT = "REDIS_PORT"

    KAFKA_HOST = "KAFKA_HOST"
    KAFKA_PORT = "KAFKA_PORT"
    KAFKA_BOOTSTRAP_SERVER = "KAFKA_BOOTSTRAP_SERVER"

    CLICKHOUSE_HOST = "CLICKHOUSE_HOST"
    CLICKHOUSE_NATIVE_PORT = "CLICKHOUSE_NATIVE_PORT"

    APP_INSERTER_USER = "APP_INSERTER_USERNAME"
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
