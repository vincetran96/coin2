"""Code containing logic to insert data to Iceberg
"""
import logging
from typing import Any, Dict, List, Literal

from common.catalog import get_catalog
from data.iceberg.utils import to_arrow_table
from data.interfaces import DataInserter


class IcebergBaseInserter(DataInserter):
    """Base inserter to Iceberg that can be used as a context manager
    """
    def __init__(self, mode: Literal["append", "overwrite"] = "append"):
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

    def _insert(self, tbl_name: str, data: List[Dict], field_names: List[str], **kwargs):
        """Private method

        Insert data into Iceberg table

        Args:
            tbl_name (str):
            data (List[Dict]):
            field_names (List[str]):
        """
        tbl_object = self._catalog.load_table(tbl_name)
        data_py_tbl = to_arrow_table(data=data, fields=field_names)
        
        match self.mode:
            case "append":
                tbl_object.append(df=data_py_tbl)
            case "overwrite":
                tbl_object.overwrite(df=data_py_tbl)
            case _:
                logging.info("No valid mode provided")

    def __enter__(self):
        # self.connect()
        return self

    def __exit__(self, *_):
        pass
