"""Wires the ELT stages together in ELT order: extract, load (raw), transform (SQL)."""

import sqlite3
from pathlib import Path

import pandas as pd

from ..config import MONTHS, PROJECT_ROOT
from ..extract import download_months
from .load_raw import load_raw_trips

SQL_PATH = Path(__file__).resolve().parent / "sql" / "daily_revenue.sql"
OUTPUT_CSV = PROJECT_ROOT / "data" / "elt" / "daily_revenue_elt.csv"


def run(months: tuple[str, ...] = MONTHS, *, force_download: bool = False) -> pd.DataFrame:
    raw_files = download_months(months, force=force_download)  # E — shared with the ETL pipeline
    warehouse_path = load_raw_trips(raw_files)  # L — raw rows, unchanged

    transform_sql = SQL_PATH.read_text()
    with sqlite3.connect(warehouse_path) as connection:
        connection.executescript(transform_sql)  # T — runs inside the warehouse, not in Python
        daily_revenue = pd.read_sql("SELECT * FROM fct_daily_revenue", connection)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    daily_revenue.to_csv(OUTPUT_CSV, index=False)
    return daily_revenue
