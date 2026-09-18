import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_pipeline.transform import compute_daily_revenue


def test_compute_daily_revenue_groups_by_date_and_sums_amount():
    trips = pd.DataFrame(
        {
            "lpep_pickup_datetime": pd.to_datetime(
                [
                    "2025-01-01 08:00:00",
                    "2025-01-01 20:00:00",
                    "2025-01-02 09:30:00",
                ]
            ),
            "total_amount": [10.0, 15.5, 7.25],
        }
    )

    daily = compute_daily_revenue(trips)

    assert list(daily["pickup_date"].astype(str)) == ["2025-01-01", "2025-01-02"]
    assert daily["total_revenue"].tolist() == [25.5, 7.25]
    assert daily["trip_count"].tolist() == [2, 1]


def test_compute_daily_revenue_rounds_to_cents():
    trips = pd.DataFrame(
        {
            "lpep_pickup_datetime": pd.to_datetime(["2025-01-01", "2025-01-01"]),
            "total_amount": [0.111, 0.112],
        }
    )

    daily = compute_daily_revenue(trips)

    assert daily["total_revenue"].tolist() == [0.22]
