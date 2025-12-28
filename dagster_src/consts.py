"""Dagster constants shared across assets/jobs/schedules."""

# Keep this as a single source of truth for the Binance OHLCV Raw→Bronze micro-batch runtime.
BINANCE_OHLCV_BRZ_MAX_RUNTIME: int = 15 * 60
