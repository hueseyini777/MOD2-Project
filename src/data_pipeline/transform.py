"""Transform stage: turn staged raw trips into a daily revenue summary.

This is the "T" in ETL. It runs entirely in memory (via pandas) and never touches
the network or a database — it only knows how to turn one shape of DataFrame into
another. Keeping it a pure function makes it easy to unit test without any files
or downloads at all (see tests/test_transform.py).
"""

from pathlib import Path

import pandas as pd

PICKUP_COLUMN = "lpep_pickup_datetime"
AMOUNT_COLUMN = "total_amount"


def read_staged_trips(raw_files: list[Path]) -> pd.DataFrame:
    """Read and concatenate the staged Parquet files into a single DataFrame."""
    frames = [
        pd.read_parquet(path, columns=[PICKUP_COLUMN, AMOUNT_COLUMN])
        for path in raw_files
    ]
    return pd.concat(frames, ignore_index=True)


def compute_daily_revenue(trips: pd.DataFrame) -> pd.DataFrame:
    """Aggregate trips into total revenue and trip count per pickup date.

    No rows are filtered before summing. A small fraction of trips have a
    negative or zero total_amount (refunds, adjustments, comped rides); these
    are intentionally included as-is so total_revenue reflects net revenue
    actually recognized that day, not gross fares. Filtering them out would
    silently overstate revenue by hiding refunds.
    """
    pickup_date = pd.to_datetime(trips[PICKUP_COLUMN]).dt.date

    daily = (
        trips.assign(pickup_date=pickup_date)
        .groupby("pickup_date")
        .agg(total_revenue=(AMOUNT_COLUMN, "sum"), trip_count=(AMOUNT_COLUMN, "size"))
        .reset_index()
        .sort_values("pickup_date")
        .reset_index(drop=True)
    )
    daily["total_revenue"] = daily["total_revenue"].round(2)
    return daily
