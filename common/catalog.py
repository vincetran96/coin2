"""Functions for Iceberg catalog
"""
import logging
from pyiceberg.catalog import Catalog, load_catalog

from common.configs import Config, OsVariable


def get_catalog() -> Catalog:
    """Load and return Iceberg catalog with configuration from environment variables
    
    Returns:
        Catalog: Configured Iceberg catalog instance
    """
    minio_user = Config.os_get(OsVariable.MINIO_ROOT_USER.value) or "admin"
    minio_password = Config.os_get(OsVariable.MINIO_ROOT_PASSWORD.value) or "password"
    
    return load_catalog(
        "rest",
        uri=Config.os_get(OsVariable.CATALOG_ENDPOINT.value),
        **{
            "s3.endpoint": Config.os_get(OsVariable.MINIO_ENDPOINT.value),
            "s3.access-key-id": minio_user,
            "s3.secret-access-key": minio_password,
            "s3.path-style-access": "true"
        }
    )


def create_namespace_if_not_exists(namespace: str) -> None:
    """Create the namespace if it doesn't exist

    Args:
        namespace (str): 
    """
    catalog = get_catalog()
    try:
        catalog.create_namespace(namespace)
        logging.info(f"Created namespace: {namespace}")
    except Exception as exc:
        logging.debug(f"Namespace {namespace} already exists or creation failed: {exc}")
        pass
