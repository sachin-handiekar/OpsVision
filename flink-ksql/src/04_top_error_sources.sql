-- ============================================================
-- Top Error Sources Leaderboard
-- ============================================================
--
-- PURPOSE:
-- Tracks which event sources are generating the most errors and
-- critical events. This creates a "leaderboard" of problematic
-- sources that need attention.
--
-- WHY A LEADERBOARD?
-- - Quickly identify the most problematic systems
-- - Prioritize incident response based on error volume
-- - Historical tracking of error-prone sources
-- - Resource allocation for reliability improvements
--
-- METRICS TRACKED:
--   - error_count: Number of error-severity events
--   - critical_count: Number of critical-severity events
--   - total_errors: Combined critical + error count
--
-- FILTERING:
-- Only sources with at least one error or critical event are stored.
-- This keeps the table focused and efficient.
--
-- RANKING:
-- Note: Flink streaming doesn't support ROW_NUMBER on non-time attributes.
-- Ranking (top 5, top 10) is done at query time using ORDER BY + LIMIT.
--
-- USE CASES:
-- - Incident response prioritization
-- - Weekly reliability reviews
-- - SRE team resource allocation
-- - Identifying flaky services
-- ============================================================

CREATE TABLE top_error_sources_5min (
    `window_start` TIMESTAMP(3),
    `source` STRING,
    `error_count` BIGINT,
    `critical_count` BIGINT,
    `total_errors` BIGINT,
    PRIMARY KEY (`window_start`, `source`) NOT ENFORCED
) DISTRIBUTED BY (`window_start`, `source`);

-- ============================================================
-- CONTINUOUS INSERT
-- Stores error sources without ranking (ranking done at query time)
-- ============================================================

INSERT INTO top_error_sources_5min
SELECT 
    `window_start`,
    `source`,
    `error_count`,
    `critical_count`,
    `error_count` + `critical_count` as `total_errors`
FROM events_aggregated_5min
WHERE `error_count` + `critical_count` > 0;

-- ============================================================
-- QUERY EXAMPLES
-- ============================================================

-- View top 5 error sources for the most recent window
SELECT 
    `window_start`,
    `source`,
    `error_count`,
    `critical_count`,
    `total_errors`
FROM top_error_sources_5min
ORDER BY `window_start` DESC, `total_errors` DESC
LIMIT 5;

-- View top 20 error sources across all windows
SELECT 
    `window_start`,
    `source`,
    `error_count`,
    `critical_count`,
    `total_errors`
FROM top_error_sources_5min
ORDER BY `window_start` DESC, `total_errors` DESC
LIMIT 20;

-- Find sources with critical events (highest priority)
SELECT 
    `window_start`,
    `source`,
    `critical_count`,
    `total_errors`
FROM top_error_sources_5min
WHERE `critical_count` > 0
ORDER BY `window_start` DESC, `critical_count` DESC
LIMIT 10;
