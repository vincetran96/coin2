"""Dummy script to create the dummy table
"""
import logging

from common.consts import LOG_FORMAT
from common.catalog import get_catalog, create_namespace_if_not_exists
from models.dummy import DummyTable


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    tbl_model = DummyTable()
    tbl_model.create_table_if_not_exists()
