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
