"""Utilities as related to Iceberg
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import pyarrow as pa

from common.catalog import get_catalog
from models.consts import CHG_TS_COL


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


def to_arrow_table(
    data: List[Dict[str, Any]],
    fields: List[str],
    schema: pa.Schema | None = None
) -> pa.Table:
    """Convert list of dicts to PyArrow Table with field selection
    
    Args:
        data: List of dictionaries
        fields: List of field names to include
    
    Returns:
        PyArrow Table with specified fields
    """
    if not data:
        schema = pa.schema([(field, pa.null()) for field in fields])
        return pa.Table.from_pylist([], schema=schema)
    filtered_data = [
        {field: row.get(field) for field in fields}
        for row in data
    ]
    if schema:
        return pa.Table.from_pylist(filtered_data, schema=schema)
    return pa.Table.from_pylist(filtered_data)


def add_audit_columns(pa_tbl: pa.Table) -> pa.Table:
    """Add audit columns to the PyArrow table

    The following columns are added:
        - _change_tstamp: timestamp of the change
    """
    # _change_tstamp
    current_time = datetime.now(timezone.utc)
    timestamp_array = pa.array([current_time] * pa_tbl.num_rows, type=pa.timestamp('us', tz='UTC'))

    return pa_tbl.append_column(CHG_TS_COL, timestamp_array)
