-- ============================================================
-- Alternative 5-Minute Aggregation (Manual Time Bucketing)
-- ============================================================
--
-- PURPOSE:
-- This is an alternative aggregation approach that uses manual time
-- bucketing instead of watermark-based TUMBLE windows. This is useful
-- when you need to bypass Confluent Cloud's watermark requirements.
--
-- WHY USE THIS APPROACH?
-- - Confluent Cloud Flink requires ~250 events per partition before
--   watermarks advance (for efficient processing)
-- - For low-volume topics, this manual approach provides immediate results
-- - Uses $rowtime (Kafka ingestion time) instead of event time
--
-- HOW IT WORKS:
-- 1. Extracts hour and minute from $rowtime
-- 2. Floors minutes to nearest 5-minute boundary
-- 3. Creates window_start and window_end timestamps
-- 4. Groups by these calculated time buckets
--
-- ADDITIONAL FIELDS:
-- - event_types: Comma-separated list of unique event types in window
-- - sample_subjects: Comma-separated list of event subjects (for debugging)
--
-- TRADE-OFFS:
-- + Works with low event volumes
-- + Provides immediate output
-- - Uses ingestion time, not true event time
-- - Less accurate for late-arriving events
-- ============================================================

INSERT INTO events_aggregated_5min
SELECT
    -- 5-minute bucket start (truncate minutes to nearest 5)
    TIMESTAMPADD(
        MINUTE,
        (EXTRACT(HOUR FROM `$rowtime`) * 60 + FLOOR(EXTRACT(MINUTE FROM `$rowtime`) / 5) * 5),
        CAST(DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd') AS DATE)
    ) AS window_start,
    source,
    TIMESTAMPADD(
        MINUTE,
        (EXTRACT(HOUR FROM `$rowtime`) * 60 + FLOOR(EXTRACT(MINUTE FROM `$rowtime`) / 5) * 5) + 5,
        CAST(DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd') AS DATE)
    ) AS window_end,
    COUNT(*) AS event_count,
    COUNT(DISTINCT type) AS unique_types,
    CAST(SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) AS BIGINT) AS critical_count,
    CAST(SUM(CASE WHEN severity = 'error' THEN 1 ELSE 0 END) AS BIGINT) AS error_count,
    CAST(SUM(CASE WHEN severity = 'warning' THEN 1 ELSE 0 END) AS BIGINT) AS warning_count,
    CAST(SUM(CASE WHEN severity = 'info' THEN 1 ELSE 0 END) AS BIGINT) AS info_count,
    LISTAGG(DISTINCT type, ',') AS event_types,
    LISTAGG(subject, ',') AS sample_subjects
FROM `cloudevents-stream`
GROUP BY 
    TIMESTAMPADD(
        MINUTE,
        (EXTRACT(HOUR FROM `$rowtime`) * 60 + FLOOR(EXTRACT(MINUTE FROM `$rowtime`) / 5) * 5),
        CAST(DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd') AS DATE)
    ),
    TIMESTAMPADD(
        MINUTE,
        (EXTRACT(HOUR FROM `$rowtime`) * 60 + FLOOR(EXTRACT(MINUTE FROM `$rowtime`) / 5) * 5) + 5,
        CAST(DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd') AS DATE)
    ),
    source;

-- ============================================================
-- WHEN TO USE WHICH APPROACH
-- ============================================================
-- 
-- Use 02_events_aggregated_5min.sql (watermark-based) when:
--   - You have high event volumes (>250 events/5min/partition)
--   - Event time accuracy is critical
--   - You need proper late event handling
--
-- Use this file (manual bucketing) when:
--   - You have low event volumes
--   - You need immediate feedback during demos
--   - Development/testing scenarios
-- ============================================================
