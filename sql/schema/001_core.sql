CREATE TABLE IF NOT EXISTS macro_observations (
    date DATE,
    series_id VARCHAR,
    value DOUBLE,
    source VARCHAR,
    data_classification VARCHAR
);

CREATE TABLE IF NOT EXISTS properties (
    property_id VARCHAR,
    city VARCHAR,
    neighborhood VARCHAR,
    area_m2 DOUBLE,
    bedrooms INTEGER,
    bathrooms DOUBLE,
    price_mxn DOUBLE,
    data_classification VARCHAR
);

CREATE TABLE IF NOT EXISTS model_runs (
    run_id VARCHAR,
    model_name VARCHAR,
    model_version VARCHAR,
    dataset_version VARCHAR,
    split_strategy VARCHAR,
    metric_name VARCHAR,
    metric_value DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
