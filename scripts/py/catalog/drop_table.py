"""This file is to be used in CLI

Drop table from Iceberg catalog
"""
import argparse
import logging

from common.consts import LOG_FORMAT
from data.iceberg.db import drop_table


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Drop table from Iceberg catalog")
    p.add_argument("--namespace", type=str, required=True, help="Iceberg namespace")
    p.add_argument("--table", type=str, required=True, help="Table name")
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    args = _parse_args()
    namespace = args.namespace
    table = args.table

    drop_table(namespace=namespace, tbl_name=table)
