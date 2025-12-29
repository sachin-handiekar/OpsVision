-- ============================================================
-- CloudEvents Source Table Definition
-- ============================================================
-- 
-- PURPOSE:
-- This SQL defines the source table that ingests CloudEvents from a Kafka topic.
-- CloudEvents is a specification for describing event data in a common way,
-- making it easy to process events from different sources consistently.
--
-- ARCHITECTURE:
-- Kafka Topic (cloudevents) --> Flink Source Table --> Downstream Processing
--
-- FIELDS:
--   - id: Unique identifier for each event
--   - specversion: CloudEvents specification version (e.g., "1.0")
--   - type: Event type (e.g., "deployment.started", "alert.triggered")
--   - source: Origin of the event (e.g., "github", "kubernetes", "datadog")
--   - time: When the event occurred (used for time-based windowing)
--   - datacontenttype: MIME type of the data field (e.g., "application/json")
--   - subject: Subject of the event (e.g., resource name, service name)
--   - severity: Event severity level (critical, error, warning, info)
--   - category: Event category for classification
--   - correlation_id: ID to trace related events across systems
--   - data: Event payload as JSON string
--
-- WATERMARK:
-- The watermark handles out-of-order events with 10-second tolerance.
-- Events arriving up to 10 seconds late will still be included in their
-- correct time windows.
--
-- DISTRIBUTION:
-- DISTRIBUTED BY HASH(`id`) ensures even data distribution across partitions
-- for optimal parallel processing.
-- ============================================================

CREATE TABLE cloudevents (
    `id` STRING,
    `specversion` STRING,
    `type` STRING,
    `source` STRING,
    `time` TIMESTAMP(3),
    `datacontenttype` STRING,
    `subject` STRING,
    `severity` STRING,
    `category` STRING,
    `correlation_id` STRING,
    `data` STRING,
    -- Event time watermark (handles out-of-order events)
    WATERMARK FOR `time` AS `time` - INTERVAL '10' SECOND
) DISTRIBUTED BY HASH(`id`) INTO 3 BUCKETS
WITH (
    'changelog.mode' = 'append'
);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Verify data is flowing into the source table
SELECT * FROM cloudevents LIMIT 5;

-- Count events per source (real-time streaming query)
SELECT 
    `source`,
    COUNT(*) as event_count
FROM cloudevents
GROUP BY `source`;
