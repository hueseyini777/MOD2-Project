"""Extract stage: download raw Green Taxi Parquet files into the local staging directory.

This is the "E" in ETL. Its only job is to get bytes from the public source onto local
disk, unchanged. It does not look at the data's contents at all.
"""

from collections.abc import Iterable
from pathlib import Path

import requests

from .config import DOWNLOAD_TIMEOUT_SECONDS, RAW_DIR, dataset_filename, dataset_url


def download_month(month: str, raw_dir: Path = RAW_DIR, *, force: bool = False) -> Path:
    """Download one month of trip data to `raw_dir`, unless it is already staged."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    destination = raw_dir / dataset_filename(month)

    if destination.exists() and not force:
        return destination

    with requests.get(dataset_url(month), stream=True, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        response.raise_for_status()
        with destination.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                output_file.write(chunk)

    return destination


def download_months(months: Iterable[str], raw_dir: Path = RAW_DIR, *, force: bool = False) -> list[Path]:
    """Download every requested month, returning the local path for each."""
    return [download_month(month, raw_dir, force=force) for month in months]
