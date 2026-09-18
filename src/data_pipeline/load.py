"""Load stage: write the transformed result to its final destination.

This is the "L" in ETL. By the time data reaches this stage it is already the
finished daily-revenue table — this stage's only job is to persist it. Today
that destination is the local filesystem. If you later swap in a database
(e.g. writing with SQLAlchemy to Postgres), only this file needs to change;
extract.py and transform.py stay exactly as they are.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import PROCESSED_DIR


def write_daily_revenue(daily_revenue: pd.DataFrame, processed_dir: Path = PROCESSED_DIR) -> dict[str, Path]:
    """Write the daily revenue table as CSV and Parquet, plus a small run metadata file."""
    processed_dir.mkdir(parents=True, exist_ok=True)

    csv_path = processed_dir / "daily_revenue.csv"
    parquet_path = processed_dir / "daily_revenue.parquet"
    metadata_path = processed_dir / "pipeline_metadata.json"

    daily_revenue.to_csv(csv_path, index=False)
    daily_revenue.to_parquet(parquet_path, index=False)

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(daily_revenue),
        "date_range": [
            str(daily_revenue["pickup_date"].min()),
            str(daily_revenue["pickup_date"].max()),
        ],
        "total_revenue": float(daily_revenue["total_revenue"].sum()),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))

    return {"csv": csv_path, "parquet": parquet_path, "metadata": metadata_path}
