-- ============================================================
-- Utility Queries for Demo and Debugging
-- ============================================================
--
-- PURPOSE:
-- A collection of useful queries for:
-- - Live demos and presentations
-- - Debugging and troubleshooting
-- - Validating data flow
-- - Monitoring system status
--
-- These are SELECT-only queries (no table modifications).
-- Run them interactively in Confluent Cloud Flink SQL editor.
-- ============================================================


-- ============================================================
-- SECTION 1: Real-Time Event Monitoring
-- ============================================================

-- 1.1 Show current event stream (last minute)
-- Use this to verify events are flowing
SELECT * FROM cloudevents
WHERE `time` > CURRENT_TIMESTAMP - INTERVAL '1' MINUTES
ORDER BY `time` DESC
LIMIT 20;

-- 1.2 Event count by source (last hour)
-- Overview of which sources are most active
SELECT 
    `source`,
    COUNT(*) as `event_count`,
    COUNT(*) FILTER (WHERE `severity` = 'critical') as `critical_count`,
    COUNT(*) FILTER (WHERE `severity` = 'error') as `error_count`
FROM cloudevents
WHERE `time` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
GROUP BY `source`
ORDER BY `event_count` DESC;

-- 1.3 Recent critical events (requires immediate attention)
SELECT 
    `time`,
    `source`,
    `type`,
    `subject`,
    `correlation_id`
FROM cloudevents
WHERE `severity` = 'critical'
  AND `time` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
ORDER BY `time` DESC
LIMIT 20;


-- ============================================================
-- SECTION 2: Aggregation Verification
-- ============================================================

-- 2.1 Latest aggregated window summary (all sources)
SELECT * FROM events_aggregated_5min
WHERE `window_start` = (
    SELECT MAX(`window_start`) FROM events_aggregated_5min
);

-- 2.2 Current system health (single row)
SELECT * FROM system_health_5min
WHERE `window_start` = (
    SELECT MAX(`window_start`) FROM system_health_5min
);

-- 2.3 Aggregation history (last 6 hours)
SELECT 
    `window_start`,
    SUM(`event_count`) as total_events,
    COUNT(DISTINCT `source`) as source_count
FROM events_aggregated_5min
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '6' HOURS
GROUP BY `window_start`
ORDER BY `window_start` DESC;


-- ============================================================
-- SECTION 3: Incident and Correlation Queries
-- ============================================================

-- 3.1 Active correlation incidents (last hour)
SELECT 
    `correlation_id`,
    `event_count`,
    `source_count`,
    `duration_seconds`,
    `has_critical`
FROM correlated_incidents
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
ORDER BY `event_count` DESC;

-- 3.2 Cross-system incidents (affecting multiple sources)
SELECT 
    `correlation_id`,
    `event_count`,
    `source_count`,
    `duration_seconds`,
    `has_critical`
FROM correlated_incidents
WHERE `source_count` >= 2
ORDER BY `window_start` DESC, `source_count` DESC
LIMIT 10;


-- ============================================================
-- SECTION 4: Error Analysis
-- ============================================================

-- 4.1 Sources with error spikes (if error_rate_trends is populated)
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

-- 4.2 Error distribution by source (last hour)
SELECT 
    `source`,
    SUM(`error_count`) as total_errors,
    SUM(`critical_count`) as total_critical,
    SUM(`warning_count`) as total_warnings,
    SUM(`event_count`) as total_events,
    ROUND(
        CAST(SUM(`error_count`) + SUM(`critical_count`) AS DOUBLE) 
        / CAST(SUM(`event_count`) AS DOUBLE) * 100, 
        2
    ) as error_rate_pct
FROM events_aggregated_5min
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
GROUP BY `source`
ORDER BY total_errors DESC;


-- ============================================================
-- SECTION 5: AI Summary Queries
-- ============================================================

-- 5.1 Latest Gemini summary (what AI is analyzing)
SELECT 
    `window_start`,
    `health_status`,
    `total_events`,
    `error_rate_percent`,
    `top_error_source`,
    `correlation_count`,
    `anomaly_count`,
    `error_trend`
FROM gemini_summary
ORDER BY `window_start` DESC
LIMIT 1;

-- 5.2 Windows requiring AI alerts
SELECT 
    `window_start`,
    `health_status`,
    `total_events`,
    `critical_count`,
    `error_rate_percent`,
    `top_error_source`
FROM gemini_summary
WHERE `health_status` IN ('CRITICAL', 'DEGRADED')
ORDER BY `window_start` DESC
LIMIT 10;


-- ============================================================
-- SECTION 6: System Monitoring
-- ============================================================

-- 6.1 Check if data is flowing (should be > 0 for healthy system)
SELECT COUNT(*) as events_last_5min
FROM cloudevents
WHERE `time` > CURRENT_TIMESTAMP - INTERVAL '5' MINUTES;

-- 6.2 All table row counts (system overview)
SELECT 'cloudevents' as table_name, COUNT(*) as row_count FROM cloudevents
UNION ALL
SELECT 'events_aggregated_5min', COUNT(*) FROM events_aggregated_5min
UNION ALL
SELECT 'system_health_5min', COUNT(*) FROM system_health_5min
UNION ALL
SELECT 'top_error_sources_5min', COUNT(*) FROM top_error_sources_5min
UNION ALL
SELECT 'correlated_incidents', COUNT(*) FROM correlated_incidents
UNION ALL
SELECT 'error_rate_trends', COUNT(*) FROM error_rate_trends
UNION ALL
SELECT 'error_anomalies', COUNT(*) FROM error_anomalies
UNION ALL
SELECT 'gemini_summary', COUNT(*) FROM gemini_summary;

-- 6.3 Health status distribution over time
SELECT 
    `health_status`,
    COUNT(*) as window_count
FROM system_health_5min
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '24' HOURS
GROUP BY `health_status`
ORDER BY window_count DESC;

-- 6.4 Event volume over time (hourly)
SELECT 
    DATE_FORMAT(`window_start`, 'yyyy-MM-dd HH:00') as hour,
    SUM(`event_count`) as total_events,
    SUM(`critical_count`) as critical_events,
    SUM(`error_count`) as error_events
FROM events_aggregated_5min
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '24' HOURS
GROUP BY DATE_FORMAT(`window_start`, 'yyyy-MM-dd HH:00')
ORDER BY hour DESC;
