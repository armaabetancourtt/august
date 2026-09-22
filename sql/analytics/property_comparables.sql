WITH neighborhood_stats AS (
    SELECT
        city,
        neighborhood,
        COUNT(*) AS comparable_count,
        MEDIAN(price_mxn / NULLIF(area_m2, 0)) AS median_price_m2,
        QUANTILE_CONT(price_mxn / NULLIF(area_m2, 0), 0.25) AS p25_price_m2,
        QUANTILE_CONT(price_mxn / NULLIF(area_m2, 0), 0.75) AS p75_price_m2
    FROM properties
    GROUP BY city, neighborhood
)
SELECT *
FROM neighborhood_stats
ORDER BY comparable_count DESC;
