WITH ordered AS (
    SELECT
        date,
        series_id,
        value,
        AVG(value) OVER (
            PARTITION BY series_id
            ORDER BY date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3_period_avg,
        LAG(value, 1) OVER (
            PARTITION BY series_id
            ORDER BY date
        ) AS previous_value
    FROM macro_observations
)
SELECT
    *,
    value - previous_value AS period_change,
    CASE
        WHEN previous_value = 0 OR previous_value IS NULL THEN NULL
        ELSE (value / previous_value) - 1
    END AS period_change_pct
FROM ordered
ORDER BY series_id, date;
