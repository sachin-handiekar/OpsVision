-- ============================================================
-- System Health Overview (5-Minute Windows)
-- ============================================================
--
-- PURPOSE:
-- Provides a single row per time window summarizing the overall health
-- of the entire system across ALL sources. This is the "executive summary"
-- view that powers dashboard health indicators.
--
-- KEY METRICS:
--   - total_events: Sum of all events across all sources
--   - total_sources: Count of unique event sources active in this window
--   - total_critical: Sum of critical events (highest priority)
--   - total_errors: Sum of error events
--   - total_warnings: Sum of warning events
--   - error_rate_percent: (critical + errors) / total * 100
--   - health_status: Categorical health indicator
--
-- HEALTH STATUS LOGIC:
--   1. CRITICAL: Any critical events detected (immediate attention needed)
--   2. DEGRADED: Error rate > 10% (system performance affected)
--   3. WARNING: Some errors but not critical levels
--   4. HEALTHY: No significant issues
--
-- DATA FLOW:
-- events_aggregated_5min (per-source) --> system_health_5min (global)
--
-- USE CASES:
-- - NOC (Network Operations Center) dashboards
-- - Executive health summaries
-- - SLA monitoring
-- - Alerting systems
-- ============================================================

CREATE TABLE system_health_5min (
    `window_start` TIMESTAMP(3),
    `window_end` TIMESTAMP(3),
    `total_events` BIGINT,
    `total_sources` BIGINT,
    `total_critical` BIGINT,
    `total_errors` BIGINT,
    `total_warnings` BIGINT,
    `error_rate_percent` DOUBLE,
    `health_status` STRING,
    PRIMARY KEY (`window_start`) NOT ENFORCED
) DISTRIBUTED BY HASH(`window_start`) INTO 1 BUCKETS
WITH (
    'changelog.mode' = 'upsert'
);

-- ============================================================
-- CONTINUOUS HEALTH CALCULATION
-- Aggregates from per-source summaries to system-wide view
-- ============================================================

INSERT INTO system_health_5min
SELECT 
    `window_start`,
    `window_end`,
    SUM(`event_count`) as `total_events`,
    COUNT(DISTINCT `source`) as `total_sources`,
    SUM(`critical_count`) as `total_critical`,
    SUM(`error_count`) as `total_errors`,
    SUM(`warning_count`) as `total_warnings`,
    -- Calculate error rate as percentage
    CASE 
        WHEN SUM(`event_count`) > 0 
        THEN CAST((SUM(`critical_count`) + SUM(`error_count`)) AS DOUBLE) 
             / CAST(SUM(`event_count`) AS DOUBLE) * 100.0
        ELSE 0.0 
    END as `error_rate_percent`,
    -- Determine health status based on severity thresholds
    CASE
        WHEN SUM(`critical_count`) > 0 THEN 'CRITICAL'
        WHEN CAST((SUM(`critical_count`) + SUM(`error_count`)) AS DOUBLE) 
             / CAST(SUM(`event_count`) AS DOUBLE) > 0.1 THEN 'DEGRADED'
        WHEN SUM(`error_count`) > 0 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as `health_status`
FROM events_aggregated_5min
GROUP BY `window_start`, `window_end`;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- View current system health (latest windows)
SELECT * FROM system_health_5min
ORDER BY `window_start` DESC
LIMIT 10;

-- Find periods with degraded health
SELECT 
    `window_start`,
    `health_status`,
    `error_rate_percent`,
    `total_critical`,
    `total_errors`
FROM system_health_5min
WHERE `health_status` IN ('CRITICAL', 'DEGRADED')
ORDER BY `window_start` DESC
LIMIT 20;
