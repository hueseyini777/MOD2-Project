"""Wires the three stages together in ETL order: extract, then transform, then load."""

from pathlib import Path

from .config import MONTHS
from .extract import download_months
from .load import write_daily_revenue
from .transform import compute_daily_revenue, read_staged_trips


def run(months: tuple[str, ...] = MONTHS, *, force_download: bool = False) -> dict[str, Path]:
    raw_files = download_months(months, force=force_download)
    trips = read_staged_trips(raw_files)
    daily_revenue = compute_daily_revenue(trips)
    return write_daily_revenue(daily_revenue)
