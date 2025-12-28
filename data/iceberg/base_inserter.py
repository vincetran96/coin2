"""Code containing logic to insert data to Iceberg
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

import pyarrow as pa

from common.catalog import get_catalog
from data.iceberg.utils import to_arrow_table, add_audit_columns
from data.interfaces import DataInserter


class IcebergBaseInserter(DataInserter):
    """
    Base inserter to Iceberg that can be used as a context manager
    """
    def __init__(self, mode: Literal["append", "overwrite"] = "append") -> None:
        super().__init__(mode=mode)

        # Private
        self._con = None
        self._catalog = get_catalog()

    # def connect(self):
    #     """Connect to Iceberg db and assign a connection to its attr
    #     """

    # def disconnect(self):
    #     """Disconnect from Iceberg db
    #     """
    #     self._con.disconnect()

    def _insert(self, tbl_name: str, data: List[Dict], field_names: List[str], **kwargs) -> None:
        """Private method

        Insert data into Iceberg table

        Before inserting, we add audit columns to the data.

        Args:
            tbl_name (str): Identifier of the target table
            data (List[Dict]):
            field_names (List[str]):
        """
        tbl_object = self._catalog.load_table(tbl_name)
        tbl_schema = tbl_object.schema()
        tbl_pa_schema = tbl_schema.as_arrow()
        tbl_columns = [col.name for col in tbl_schema.columns]

        data_pa_tbl = to_arrow_table(data=data, fields=field_names)
        data_pa_tbl = add_audit_columns(data_pa_tbl)

        # We attempt to convert the data into target's schema
        data_pa_tbl = data_pa_tbl.cast(
            pa.schema(
                [tbl_pa_schema.field(f) for f in tbl_columns if f in data_pa_tbl.column_names]
            )
        )

        match self.mode:
            case "append":
                tbl_object.append(df=data_pa_tbl)
            case "overwrite":
                tbl_object.overwrite(df=data_pa_tbl)
            case _:
                logging.info("No valid mode provided")

    def __enter__(self):
        # self.connect()
        return self

    def __exit__(self, *_):
        pass
