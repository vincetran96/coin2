"""Utils for ETL related to Daft
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Iterator

import daft
import daft.functions as F
from daft import col, lit
from daft.window import Window

from models.consts import CHG_TS_COL


def deduplicate_data(
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


def add_audit_columns(input_df: daft.DataFrame) -> daft.DataFrame:
    """Add audit columns to the Daft DataFrame

    The following columns are added:
        - _change_tstamp: timestamp of the change
    """
    return (
        input_df.select(
            "*",
            lit(datetime.now(timezone.utc)).alias(CHG_TS_COL),
        )
    )


# Function related to batching DataFrame with a timestamp column

@dataclass(frozen=True, kw_only=True)
class TimeBatch:
    start: datetime
    end: datetime
    df: daft.DataFrame


def get_min_max_ts(df: daft.DataFrame, ts_col: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Compute min/max of ts_col by executing a small aggregation

    Returns:
        Tuple: Min/max timestamps
    """
    if ts_col not in df.column_names:
        raise ValueError(f"Column {ts_col} not found in DataFrame")

    stats = (
        df.agg(
            col(ts_col).min().alias("min_ts"),
            col(ts_col).max().alias("max_ts"),
        )
        .to_arrow()
    )
    if stats.num_rows == 0:
        return None, None

    min_ts = stats["min_ts"][0].as_py()
    max_ts = stats["max_ts"][0].as_py()
    return min_ts, max_ts


def iter_batches_by_ts(
    input_df: daft.DataFrame,
    ts_col: str,
    step: timedelta,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterator[TimeBatch]:
    """Yield batches of input DataFrame where ts_col is in [batch_start, batch_end)

    Notes:
    - Start/end default to the min/max in delta_df
    - This does NOT materialize the full data; each yielded DataFrame stays lazy
    """
    min_ts, max_ts = get_min_max_ts(input_df, ts_col)
    if min_ts is None or max_ts is None:
        return

    lower = start or min_ts
    upper = end or max_ts

    # Make stop inclusive-safe by extending one step if needed
    # (since we use [cur, nxt) and want to include df_max)
    if upper == lower:
        upper = lower + step

    while lower <= upper:
        nxt = lower + step
        batch = input_df.filter((col(ts_col) >= lit(lower)) & (col(ts_col) < lit(nxt)))

        yield TimeBatch(start=lower, end=nxt, df=batch)
        lower = nxt

# Function related to batching DataFrame with a timestamp column