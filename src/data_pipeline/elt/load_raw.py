"""ELT load stage: write raw trip rows into a local warehouse, unchanged.

This is the "L" in ELT, and it runs right after Extract — before any
transformation happens. Contrast this with the ETL load stage
(src/data_pipeline/load.py), which writes an already-aggregated result.
Here, every column from the staged Parquet files goes into the warehouse
as-is; the transform only happens afterwards, in SQL, against this table.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from ..config import PROJECT_ROOT

WAREHOUSE_PATH = PROJECT_ROOT / "data" / "elt" / "warehouse.db"
RAW_TABLE = "raw_green_tripdata"


def load_raw_trips(raw_files: list[Path], warehouse_path: Path = WAREHOUSE_PATH) -> Path:
    """Load the staged Parquet files into a SQLite table, unchanged."""
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(warehouse_path) as connection:
        for index, path in enumerate(raw_files):
            trips = pd.read_parquet(path)  # every column, no filtering — this is "raw"
            trips.to_sql(
                RAW_TABLE,
                connection,
                if_exists="replace" if index == 0 else "append",
                index=False,
            )

    return warehouse_path
