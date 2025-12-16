"""Quick check if data is flowing to Iceberg
"""
from pyiceberg.catalog import load_catalog

from common.configs import Config, OsVariable


catalog = load_catalog(
    "rest",
    uri=Config.os_get(OsVariable.CATALOG_ENDPOINT.value),
    **{
        "s3.endpoint": Config.os_get(OsVariable.MINIO_ENDPOINT.value),
        "s3.access-key-id": "admin",
        "s3.secret-access-key": "password",
        "s3.path-style-access": "true"
    }
)

try:
    table = catalog.load_table("binance.ohlcv_brz")
    
    print("Table exists: binance.ohlcv_brz")
    print(f"Schema: {table.schema()}")
    
    # Get row count
    snapshot = table.current_snapshot()
    total_rows = int(snapshot.summary.get("total-records", 0)) if snapshot else 0
    print(f"Total rows: {total_rows}")

    # Sample preview (bounded scan)
    preview = table.scan(limit=5).to_pandas()
    print("\nSample rows (up to 5):")
    print(preview)
    
except Exception as e:
    print(f"Error: {e}")
