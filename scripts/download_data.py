"""Download the raw Green Taxi Parquet files, without running the rest of the pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_pipeline.extract import download_months
from data_pipeline.config import MONTHS

if __name__ == "__main__":
    paths = download_months(MONTHS)
    for path in paths:
        print(f"staged: {path}")
