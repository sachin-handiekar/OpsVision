-- ============================================================
-- Gemini AI Summary Table
-- ============================================================
--
-- PURPOSE:
-- Creates a comprehensive, AI-ready summary of system health for each
-- time window. This table is designed to be consumed by Google Gemini
-- (or other LLMs) for natural language incident summaries.
--
-- WHY AI INTEGRATION?
-- - Transforms complex metrics into human-readable insights
-- - Enables natural language queries about system health
-- - Automates incident report generation
-- - Provides context-aware recommendations
--
-- DESIGN PRINCIPLES:
-- 1. ONE ROW PER WINDOW: Each row contains everything needed to
--    understand system state at that point in time
-- 2. DENORMALIZED: Includes data from multiple tables for efficiency
-- 3. AI-FRIENDLY: Uses descriptive field names and consistent types
--
-- FIELDS:
--   Core Metrics:
--   - total_events: Total event count
--   - total_sources: Active source count
--   - critical/error/warning_count: Severity breakdown
--   
--   Health Indicators:
--   - health_status: CRITICAL/DEGRADED/WARNING/HEALTHY
--   - error_rate_percent: Overall error percentage
--   
--   Context:
--   - top_error_source: Most problematic source
--   - top_error_count: Error count from that source
--   - correlation_count: Number of correlated incidents
--   - anomaly_count: Number of detected anomalies
--   - error_trend: SPIKE/IMPROVING/STABLE/etc.
--
-- CONSUMPTION:
-- This table is read by a Python/FastAPI service that sends the data
-- to Gemini for natural language processing.
-- ============================================================

CREATE TABLE gemini_summary (
    `window_start` TIMESTAMP(3),
    `window_end` TIMESTAMP(3),
    `total_events` BIGINT,
    `total_sources` BIGINT,
    `critical_count` BIGINT,
    `error_count` BIGINT,
    `warning_count` BIGINT,
    `health_status` STRING,
    `error_rate_percent` DOUBLE,
    `top_error_source` STRING,
    `top_error_count` BIGINT,
    `correlation_count` BIGINT,
    `anomaly_count` BIGINT,
    `error_trend` STRING,
    PRIMARY KEY (`window_start`) NOT ENFORCED
) DISTRIBUTED BY HASH(`window_start`) INTO 1 BUCKETS
WITH (
    'changelog.mode' = 'upsert'
);

-- ============================================================
-- COMPREHENSIVE SUMMARY GENERATION
-- Joins multiple tables to create AI-ready summaries
-- ============================================================

-- Note: error_rate_trends and error_anomalies INSERTs are disabled
-- so correlation_count, anomaly_count, and error_trend use defaults

INSERT INTO gemini_summary
SELECT 
    -- Time window
    sh.`window_start`,
    sh.`window_end`,
    
    -- Core metrics from system health
    sh.`total_events`,
    sh.`total_sources`,
    sh.`total_critical`,
    sh.`total_errors`,
    sh.`total_warnings`,
    sh.`health_status`,
    sh.`error_rate_percent`,
    
    -- Top error source context
    COALESCE(tes.`source`, 'none') as `top_error_source`,
    COALESCE(tes.`total_errors`, CAST(0 AS BIGINT)) as `top_error_count`,
    
    -- Correlated incidents context
    COALESCE(ci.`incident_count`, CAST(0 AS BIGINT)) as `correlation_count`,
    
    -- Anomaly context (disabled - using defaults)
    CAST(0 AS BIGINT) as `anomaly_count`,
    'STABLE' as `error_trend`
    
FROM system_health_5min sh

-- Join with top error sources to get worst performer
LEFT JOIN (
    SELECT `window_start`, `source`, `total_errors`
    FROM top_error_sources_5min
) tes ON sh.`window_start` = tes.`window_start`

-- Join with correlated incidents for incident count
LEFT JOIN (
    SELECT `window_start`, COUNT(*) as `incident_count`
    FROM correlated_incidents
    GROUP BY `window_start`
) ci ON sh.`window_start` = ci.`window_start`;

-- ============================================================
-- QUERY EXAMPLES
-- ============================================================

-- View latest summaries (what AI receives)
SELECT * FROM gemini_summary
ORDER BY `window_start` DESC
LIMIT 10;

-- Get the most recent summary for AI processing
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

-- Find windows that warrant AI-generated alerts
SELECT *
FROM gemini_summary
WHERE `health_status` IN ('CRITICAL', 'DEGRADED')
   OR `correlation_count` > 5
   OR `anomaly_count` > 0
ORDER BY `window_start` DESC
LIMIT 20;

-- ============================================================
-- SAMPLE AI PROMPT TEMPLATE
-- ============================================================
--
-- The following is an example prompt that can be used with Gemini:
--
-- """
-- Analyze the following system health summary and provide:
-- 1. A brief status overview in plain English
-- 2. Key concerns that need immediate attention
-- 3. Recommended actions for the operations team
--
-- System Health Data:
-- - Time Window: {window_start} to {window_end}
-- - Health Status: {health_status}
-- - Total Events: {total_events}
-- - Error Rate: {error_rate_percent}%
-- - Critical Events: {critical_count}
-- - Errors: {error_count}
-- - Top Error Source: {top_error_source} ({top_error_count} errors)
-- - Correlated Incidents: {correlation_count}
-- - Anomalies Detected: {anomaly_count}
-- - Error Trend: {error_trend}
--
-- Provide a concise, actionable summary for the NOC team.
-- """
-- ============================================================
