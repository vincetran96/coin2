"""Dagster assets for Binance OHLCV
"""
from dagster import asset, AssetExecutionContext, Config

from app.etl.ohlcv.binance.raw_to_brz_cli import run_raw_to_brz
from app.etl.ohlcv.binance.brz_to_slv_daft_cli import run_brz_to_slv
from app.etl.ohlcv.binance.slv_to_clickhouse_cli import run_slv_to_clickhouse
from dagster_src.consts import BINANCE_OHLCV_BRZ_MAX_RUNTIME
from dagster_src.resources import IcebergResource, ClickHouseResource


class BinanceOHLCVBrzConfig(Config):
    max_runtime: int = BINANCE_OHLCV_BRZ_MAX_RUNTIME


@asset(group_name="ohlcv")
def binance_ohlcv_brz(
    context: AssetExecutionContext,
    iceberg: IcebergResource,
    config: BinanceOHLCVBrzConfig
) -> None:
    """Asset representing the Binance OHLCV Bronze table
    """
    context.log.info("Processing Raw to Bronze...")
    
    catalog = iceberg.get_catalog()
    
    run_raw_to_brz(catalog=catalog, max_runtime=config.max_runtime)
    
    context.log.info("Bronze transformation complete!")


@asset(group_name="ohlcv", deps=[binance_ohlcv_brz])
def binance_ohlcv_slv(
    context: AssetExecutionContext,
    iceberg: IcebergResource
) -> None:
    """Asset representing the Binance OHLCV Silver table
    """
    context.log.info("Processing Bronze to Silver...")
    
    catalog = iceberg.get_catalog()
    
    run_brz_to_slv(catalog=catalog)
    
    context.log.info("Silver transformation complete!")


@asset(group_name="ohlcv", deps=[binance_ohlcv_slv])
def binance_ohlcv_clickhouse(
    context: AssetExecutionContext,
    iceberg: IcebergResource,
    clickhouse: ClickHouseResource
) -> None:
    """Asset representing the Binance OHLCV ClickHouse table
    """
    context.log.info("Processing Silver to ClickHouse...")

    catalog = iceberg.get_catalog()
    ch_executor = clickhouse.get_executor()
    
    with ch_executor as executor:
        run_slv_to_clickhouse(catalog=catalog, ch_executor=executor)
    
    context.log.info("ClickHouse transformation complete!")
