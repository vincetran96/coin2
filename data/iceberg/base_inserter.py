"""Code containing logic to insert data to Iceberg
"""
import logging
from typing import Any, Dict, List, Literal

from common.catalog import get_catalog, create_namespace_if_not_exists
from models.base_model import BaseModel


class BaseInserter:
    """Base inserter to Iceberg that can be used as a context manager
    """
    def __init__(self, mode: Literal["append", "overwrite"] = "append"):
        self.mode = mode

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

    def insert(self, tbl_model: BaseModel, data: Any):
        """Insert data into Iceberg table

        Args:
            tbl_model (BaseModel): Model representing the target table
            data (Any):
        """
        tbl_object = self._catalog.load_table(tbl_model.tbl_identifier)
        
        match self.mode:
            case "append":
                tbl_object.append(df=data)
            case "overwrite":
                tbl_object.overwrite(df=data)
            case _:
                logging.info("No valid mode provided")

    def __enter__(self):
        # self.connect()
        return self

    def __exit__(self, *_):
        pass
