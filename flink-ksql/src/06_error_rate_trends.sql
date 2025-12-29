-- ============================================================
-- Error Rate Trends Analysis
-- ============================================================
--
-- PURPOSE:
-- Compares error rates between current and previous time windows
-- to identify trends: spikes, improvements, or stable patterns.
--
-- WHY TREND ANALYSIS?
-- - Raw error counts don't tell the whole story
-- - A spike from 1% to 10% is more concerning than steady 5%
-- - Trend detection enables proactive alerting
-- - Helps identify if remediation is working
--
-- TREND CATEGORIES:
--   - NEW_ERRORS: No previous errors, now seeing them (concerning)
--   - SPIKE: Error rate doubled or more (immediate attention)
--   - INCREASING: Error rate up by 20%+ (watch closely)
--   - DECREASING: Error rate down by 20%+ (improving)
--   - IMPROVING: Error rate halved or more (great progress)
--   - STABLE: Error rate within 20% of previous (normal)
--
-- LIMITATIONS:
-- ⚠️ NOTE: LAG() window function is NOT SUPPORTED in 
-- Confluent Cloud Flink streaming mode.
--
-- The INSERT statement is commented out. To use this pattern:
-- 1. Use batch mode processing, or
-- 2. Implement comparison logic in application layer, or
-- 3. Use materialized views with self-join on offset windows
-- ============================================================

CREATE TABLE error_rate_trends (
    `window_start` TIMESTAMP(3),
    `source` STRING,
    `current_error_rate` DOUBLE,
    `previous_error_rate` DOUBLE,
    `trend` STRING,
    `percent_change` DOUBLE,
    PRIMARY KEY (`window_start`, `source`) NOT ENFORCED
) DISTRIBUTED BY (`window_start`, `source`);

-- ============================================================
-- TREND CALCULATION (DISABLED - LAG() NOT SUPPORTED)
-- ============================================================

-- DISABLED: LAG() not supported in Confluent Cloud Flink streaming
-- 
-- The logic shown below demonstrates the intended pattern.
-- Consider alternative approaches for production use.

/*
INSERT INTO error_rate_trends
SELECT 
    `window_start`,
    `source`,
    `current_error_rate`,
    `previous_error_rate`,
    CASE
        WHEN `previous_error_rate` = 0 AND `current_error_rate` > 0 THEN 'NEW_ERRORS'
        WHEN `current_error_rate` > `previous_error_rate` * 2 THEN 'SPIKE'
        WHEN `current_error_rate` < `previous_error_rate` * 0.5 THEN 'IMPROVING'
        WHEN `current_error_rate` > `previous_error_rate` * 1.2 THEN 'INCREASING'
        WHEN `current_error_rate` < `previous_error_rate` * 0.8 THEN 'DECREASING'
        ELSE 'STABLE'
    END as `trend`,
    CASE 
        WHEN `previous_error_rate` = 0 THEN 0
        ELSE ((`current_error_rate` - `previous_error_rate`) / `previous_error_rate` * 100.0)
    END as `percent_change`
FROM (
    SELECT 
        `window_start`,
        `source`,
        CASE 
            WHEN `event_count` > 0 
            THEN CAST((`critical_count` + `error_count`) AS DOUBLE) / CAST(`event_count` AS DOUBLE)
            ELSE 0.0 
        END as `current_error_rate`,
        LAG(
            CASE 
                WHEN `event_count` > 0 
                THEN CAST((`critical_count` + `error_count`) AS DOUBLE) / CAST(`event_count` AS DOUBLE)
                ELSE 0.0 
            END, 
            1
        ) OVER (PARTITION BY `source` ORDER BY `window_start`) as `previous_error_rate`
    FROM events_aggregated_5min
)
WHERE `previous_error_rate` IS NOT NULL;
*/

-- ============================================================
-- QUERY EXAMPLES (for when data is populated)
-- ============================================================

-- View concerning trends (spikes and new errors)
SELECT * FROM error_rate_trends
WHERE `trend` IN ('SPIKE', 'NEW_ERRORS', 'INCREASING')
ORDER BY `window_start` DESC, `percent_change` DESC
LIMIT 20;

-- View sources with current spikes
SELECT 
    `source`,
    `current_error_rate`,
    `previous_error_rate`,
    `percent_change`,
    `trend`
FROM error_rate_trends
WHERE `window_start` = (
    SELECT MAX(`window_start`) FROM error_rate_trends
)
AND `trend` IN ('SPIKE', 'INCREASING')
ORDER BY `percent_change` DESC;

-- ============================================================
-- ALTERNATIVE APPROACH: Self-Join Pattern
-- ============================================================
-- 
-- If you need trend analysis in streaming mode, consider a
-- self-join pattern that compares current window with previous:
--
-- SELECT 
--     curr.`window_start`,
--     curr.`source`,
--     curr.error_rate as `current_error_rate`,
--     prev.error_rate as `previous_error_rate`
-- FROM events_aggregated_5min curr
-- JOIN events_aggregated_5min prev
--     ON curr.`source` = prev.`source`
--     AND curr.`window_start` = prev.`window_start` + INTERVAL '5' MINUTES
--
-- Note: This approach has higher resource requirements.
-- ============================================================
