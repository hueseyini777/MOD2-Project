"""Run the ELT variant: download, load raw rows into SQLite, transform with SQL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_pipeline.elt.pipeline import run

if __name__ == "__main__":
    daily_revenue = run()
    print(f"wrote {len(daily_revenue)} rows to data/elt/daily_revenue_elt.csv")
    print(daily_revenue.head())
