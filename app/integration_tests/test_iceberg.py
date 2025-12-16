"""Quick check if data is flowing to Iceberg
"""
from pyiceberg.catalog import load_catalog

from common.catalog import get_catalog
from common.configs import Config, OsVariable


catalog = get_catalog()
TABLE_IDENTIFIER = "binance.ohlcv_brz"

try:
    table = catalog.load_table(TABLE_IDENTIFIER)
    
    print(f"Table exists: {TABLE_IDENTIFIER}")
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
