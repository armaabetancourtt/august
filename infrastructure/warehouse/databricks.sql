-- Run from an authenticated Databricks SQL Warehouse (Unity Catalog enabled).
CREATE SCHEMA IF NOT EXISTS main.raw;
CREATE SCHEMA IF NOT EXISTS main.analytics;
CREATE TABLE IF NOT EXISTS main.raw.property_events (
 event_id STRING NOT NULL, property_id STRING NOT NULL,
 occurred_at TIMESTAMP NOT NULL, amount DECIMAL(18,2), event_type STRING
) USING DELTA;
