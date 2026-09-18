"""Shared configuration for the pipeline: which months, which URLs, which paths."""

from pathlib import Path

# NYC TLC only publishes complete months, so we pin the three months the brief asks for.
MONTHS = ("2025-01", "2025-02", "2025-03")

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
FILENAME_TEMPLATE = "green_tripdata_{month}.parquet"
DOWNLOAD_TIMEOUT_SECONDS = 60

# Resolve paths relative to this file, so the pipeline works from any working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def dataset_filename(month: str) -> str:
    """Local filename for one month of Green Taxi data."""
    return FILENAME_TEMPLATE.format(month=month)


def dataset_url(month: str) -> str:
    """Public download URL for one month of Green Taxi data."""
    return f"{BASE_URL}/{dataset_filename(month)}"
