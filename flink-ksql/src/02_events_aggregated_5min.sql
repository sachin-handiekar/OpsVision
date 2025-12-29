-- ============================================================
-- 5-Minute Windowed Event Aggregations
-- ============================================================
--
-- PURPOSE:
-- This is the core aggregation layer that transforms raw streaming events
-- into meaningful 5-minute summaries. It replaces traditional batch
-- processing with continuous real-time aggregation.
--
-- WHY 5-MINUTE WINDOWS?
-- - Balances granularity with noise reduction
-- - Aligns with common monitoring intervals (Prometheus, Datadog)
-- - Provides actionable insights without alert fatigue
-- - Efficient for downstream processing and storage
--
-- AGGREGATIONS PERFORMED:
--   1. event_count: Total events in the window
--   2. unique_types: Count of distinct event types (diversity metric)
--   3. critical_count: Events with severity = 'critical'
--   4. error_count: Events with severity = 'error'
--   5. warning_count: Events with severity = 'warning'
--   6. info_count: Events with severity = 'info'
--
-- TUMBLING WINDOW:
-- Uses TUMBLE() function to create non-overlapping 5-minute windows.
-- Each event belongs to exactly one window based on its event time.
--
-- UPSERT MODE:
-- The 'upsert' changelog mode allows in-place updates as events arrive,
-- ensuring the latest aggregation is always available.
-- ============================================================

-- Table Definition
CREATE TABLE events_aggregated_5min (
    `window_start` TIMESTAMP(3),
    `window_end` TIMESTAMP(3),
    `source` STRING,
    `event_count` BIGINT,
    `unique_types` BIGINT,
    `critical_count` BIGINT,
    `error_count` BIGINT,
    `warning_count` BIGINT,
    `info_count` BIGINT,
    PRIMARY KEY (`window_start`, `source`) NOT ENFORCED
) DISTRIBUTED BY HASH(`source`) INTO 3 BUCKETS
WITH (
    'changelog.mode' = 'upsert'
);

-- ============================================================
-- CONTINUOUS AGGREGATION INSERT
-- This runs continuously, processing events as they arrive!
-- ============================================================

INSERT INTO events_aggregated_5min
SELECT 
    TUMBLE_START(`time`, INTERVAL '5' MINUTES) as `window_start`,
    TUMBLE_END(`time`, INTERVAL '5' MINUTES) as `window_end`,
    `source`,
    COUNT(*) as `event_count`,
    COUNT(DISTINCT `type`) as `unique_types`,
    COUNT(*) FILTER (WHERE `severity` = 'critical') as `critical_count`,
    COUNT(*) FILTER (WHERE `severity` = 'error') as `error_count`,
    COUNT(*) FILTER (WHERE `severity` = 'warning') as `warning_count`,
    COUNT(*) FILTER (WHERE `severity` = 'info') as `info_count`
FROM cloudevents
GROUP BY 
    TUMBLE(`time`, INTERVAL '5' MINUTES),
    `source`;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- View latest aggregated windows
SELECT * FROM events_aggregated_5min
ORDER BY `window_start` DESC, `event_count` DESC
LIMIT 10;

-- View aggregation for a specific source
SELECT * FROM events_aggregated_5min
WHERE `source` = 'github'
ORDER BY `window_start` DESC
LIMIT 5;
