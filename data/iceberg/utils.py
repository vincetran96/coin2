"""Utilities as related to Iceberg
"""
from typing import Any, Dict, List

import pyarrow as pa


def to_arrow_table(
    data: List[Dict[str, Any]],
    fields: List[str]
) -> pa.Table:
    """
    Convert list of dicts to PyArrow Table with field selection
    
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
    return pa.Table.from_pylist(filtered_data)
