-- ELT transform stage: the "T" runs here, in SQL, inside the warehouse.
-- This is the SQL equivalent of compute_daily_revenue() in the ETL pipeline's
-- transform.py — same grouping, same measures, same "no rows filtered" policy
-- for negative/zero total_amount (refunds/comps stay in the sum).

DROP TABLE IF EXISTS fct_daily_revenue;

CREATE TABLE fct_daily_revenue AS
SELECT
    DATE(lpep_pickup_datetime) AS pickup_date,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    COUNT(*) AS trip_count
FROM raw_green_tripdata
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY pickup_date;
