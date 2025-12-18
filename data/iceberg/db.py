"""For operating with database in Iceberg
"""
import logging

from common.catalog import get_catalog


def drop_table(namespace: str, tbl_name: str) -> None:
    """Drop a table
    """
    catalog = get_catalog()
    tbl_identifier = f"{namespace}.{tbl_name}"
    try:
        catalog.drop_table(tbl_identifier)
        logging.info(f"Dropped table: {tbl_identifier}")
    except Exception as exc:
        logging.warning(f"Failed to drop table {tbl_identifier}: {exc}")


def preview_table(namespace: str, tbl_name: str) -> None:
    """Preview a table
    """
    catalog = get_catalog()
    tbl_identifier = f"{namespace}.{tbl_name}"
    try:
        table = catalog.load_table(tbl_identifier)
        logging.info(f"Table exists: {tbl_identifier}")
        logging.info(f"Schema: {table.schema()}")
        
        # Get row count
        snapshot = table.current_snapshot()
        total_rows = int(snapshot.summary.get("total-records", 0)) if snapshot else 0
        logging.info(f"Total rows: {total_rows}")

        # Sample preview (bounded scan)
        preview = table.scan(limit=5).to_pandas()
        logging.info("\nSample rows (up to 5):")
        logging.info(preview)
    except Exception as exc:
        logging.warning(f"Failed to preview table {tbl_identifier}: {exc}")
