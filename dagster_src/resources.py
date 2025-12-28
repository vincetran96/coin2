"""Dagster resources
"""
from dagster import ConfigurableResource

from common.catalog import get_catalog
from data.clickhouse.base_executor import ClickHouseBaseExecutor
from data.clickhouse.base_inserter import ClickHouseBaseInserter


class IcebergResource(ConfigurableResource):
    def get_catalog(self):
        return get_catalog()


class ClickHouseResource(ConfigurableResource):
    def get_executor(self):
        return ClickHouseBaseExecutor()

    def get_inserter(self):
        return ClickHouseBaseInserter()
