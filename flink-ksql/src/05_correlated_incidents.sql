-- ============================================================
-- Correlated Events Detection
-- ============================================================
--
-- PURPOSE:
-- Detects events that share the same correlation_id, indicating they
-- are part of the same incident, transaction, or workflow. This is
-- critical for understanding cascading failures and root cause analysis.
--
-- WHAT IS CORRELATION ID?
-- A correlation_id is a unique identifier that traces related events
-- across different systems. For example:
--   - A deployment starts in GitHub (correlation_id: deploy-123)
--   - Kubernetes pod restarts (correlation_id: deploy-123)
--   - Monitoring alert fires (correlation_id: deploy-123)
-- All these events share the same correlation_id, allowing us to
-- trace the incident back to its root cause.
--
-- DETECTION LOGIC:
-- - Groups events by correlation_id within time windows
-- - Requires at least 3 events to be considered an "incident"
-- - Calculates duration and checks for critical events
--
-- METRICS:
--   - event_count: Total events in the correlated group
--   - source_count: Number of distinct sources (cross-system impact)
--   - first_event_time: When the incident started
--   - last_event_time: Most recent event
--   - duration_seconds: How long the incident has been ongoing
--   - has_critical: Whether any critical events occurred
--
-- USE CASES:
-- - Root cause analysis
-- - Cascading failure detection
-- - Deployment impact assessment
-- - Cross-service incident tracking
-- ============================================================

CREATE TABLE correlated_incidents (
    `window_start` TIMESTAMP(3),
    `correlation_id` STRING,
    `event_count` BIGINT,
    `source_count` BIGINT,
    `first_event_time` TIMESTAMP(3),
    `last_event_time` TIMESTAMP(3),
    `duration_seconds` BIGINT,
    `has_critical` BOOLEAN,
    PRIMARY KEY (`window_start`, `correlation_id`) NOT ENFORCED
) DISTRIBUTED BY (`window_start`, `correlation_id`);

-- ============================================================
-- CONTINUOUS INCIDENT DETECTION
-- Groups correlated events and identifies incidents
-- ============================================================

INSERT INTO correlated_incidents
SELECT 
    -- Create 1-minute time buckets for grouping
    TO_TIMESTAMP(
        DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd HH:mm:00'), 
        'yyyy-MM-dd HH:mm:ss'
    ) AS window_start,
    `correlation_id`,
    COUNT(*) as event_count,
    COUNT(DISTINCT `source`) as source_count,
    MIN(`$rowtime`) as first_event_time,
    MAX(`$rowtime`) as last_event_time,
    TIMESTAMPDIFF(SECOND, MIN(`$rowtime`), MAX(`$rowtime`)) as duration_seconds,
    MAX(CASE WHEN `severity` = 'critical' THEN TRUE ELSE FALSE END) as has_critical
FROM `cloudevents-stream`
WHERE `correlation_id` IS NOT NULL
GROUP BY 
    DATE_FORMAT(`$rowtime`, 'yyyy-MM-dd HH:mm:00'),
    `correlation_id`
HAVING COUNT(*) >= 3;  -- Threshold: at least 3 events to be an incident

-- ============================================================
-- QUERY EXAMPLES
-- ============================================================

-- View all correlated incidents (most events first)
SELECT * FROM correlated_incidents
ORDER BY `event_count` DESC, `window_start` DESC
LIMIT 10;

-- Find incidents spanning multiple sources (cross-system issues)
SELECT 
    `correlation_id`,
    `event_count`,
    `source_count`,
    `duration_seconds`,
    `has_critical`
FROM correlated_incidents
WHERE `source_count` >= 2
ORDER BY `source_count` DESC, `event_count` DESC
LIMIT 10;

-- Find critical incidents in the last hour
SELECT 
    `correlation_id`,
    `event_count`,
    `source_count`,
    `duration_seconds`
FROM correlated_incidents
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
  AND `has_critical` = TRUE
ORDER BY `event_count` DESC;

-- Find long-running incidents (potential ongoing issues)
SELECT 
    `correlation_id`,
    `event_count`,
    `duration_seconds`,
    `first_event_time`,
    `last_event_time`
FROM correlated_incidents
WHERE `duration_seconds` > 60  -- Incidents lasting more than 1 minute
ORDER BY `duration_seconds` DESC
LIMIT 10;
