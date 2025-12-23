"""Utils for ETL related to Daft
"""
from typing import List

import daft
import daft.functions as F
from daft import col, lit
from daft.window import Window


def _deduplicate_data(
    input_df: daft.DataFrame,
    partition_by: List[str],
    order_by: List[str],
    desc: List[bool]
) -> daft.DataFrame:
    """Deduplicate data from the input DataFrame
    
    For each combination of (exchange, symbol, timestamp), keeps only the row with
    the latest change_tstamp.
    Similar to SQL's: `ROW_NUMBER() OVER (PARTITION BY exchange, symbol, timestamp ORDER BY change_tstamp DESC)`

    Args:
        input_df (daft.DataFrame): Input DataFrame
        partition_by (List[str]): Columns to partition by
        order_by (List[str]): Columns to order by
        desc (List[bool]): Descending flags for each column in order_by

    Returns:
        daft.DataFrame: Deduplicated DataFrame with one row per (exchange, symbol, timestamp)
    """
    if len(desc) != len(order_by):
        raise ValueError("Length of descending flags must match number of order by columns")

    window_spec = (
        Window()
        .partition_by(*partition_by)
        .order_by(*[col(c) for c in order_by], desc=desc)
    )

    input_df = input_df.with_column("_row_num", F.row_number().over(window_spec))

    return (
        input_df
        .where(col("_row_num") == lit(1))
        .exclude("_row_num")
    )
