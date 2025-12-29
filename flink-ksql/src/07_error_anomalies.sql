-- ============================================================
-- Real-Time Anomaly Detection
-- ============================================================
--
-- PURPOSE:
-- Detects statistical anomalies in error rates using z-score analysis.
-- This identifies when error rates deviate significantly from their
-- historical baseline, catching issues that simple thresholds miss.
--
-- WHY STATISTICAL ANOMALY DETECTION?
-- - Fixed thresholds don't work for all services
--   (a 1% error rate might be normal for one service, critical for another)
-- - Z-scores normalize behavior relative to each source's baseline
-- - Detects unusual patterns even when absolute numbers seem fine
-- - Reduces false positives from services with inherent variability
--
-- Z-SCORE EXPLAINED:
-- Z-score = (current_value - average) / standard_deviation
--   - Z > 3: Very unusual (99.7th percentile) - CRITICAL
--   - Z > 2: Unusual (95th percentile) - WARNING
--   - Z < 2: Normal variation
--
-- BASELINE CALCULATION:
-- Uses the previous 12 windows (60 minutes) as the baseline period.
-- This provides enough history to establish patterns while remaining
-- responsive to recent changes.
--
-- ANOMALY LEVELS:
--   - CRITICAL: Z-score > 3 (very significant deviation)
--   - WARNING: Z-score > 2 (notable deviation)
--   - NORMAL: Within expected variation
--   - STABLE: Standard deviation is 0 (constant error rate)
--
-- LIMITATIONS:
-- ⚠️ NOTE: AVG/STDDEV OVER windows are NOT SUPPORTED in 
-- Confluent Cloud Flink streaming mode.
--
-- The INSERT statement is commented out. For production:
-- - Use batch processing
-- - Implement in application layer
-- - Consider using Confluent ksqlDB for this pattern
-- ============================================================

CREATE TABLE error_anomalies (
    `window_start` TIMESTAMP(3),
    `source` STRING,
    `error_rate` DOUBLE,
    `avg_baseline` DOUBLE,
    `std_deviation` DOUBLE,
    `z_score` DOUBLE,
    `anomaly_level` STRING,
    PRIMARY KEY (`window_start`, `source`) NOT ENFORCED
) DISTRIBUTED BY (`window_start`, `source`);

-- ============================================================
-- ANOMALY DETECTION (DISABLED - OVER WINDOWS NOT SUPPORTED)
-- ============================================================

-- DISABLED: AVG/STDDEV OVER ROWS BETWEEN not supported in 
-- Confluent Cloud Flink streaming mode.
--
-- The logic below shows the intended pattern.

/*
INSERT INTO error_anomalies
SELECT 
    `window_start`,
    `source`,
    `error_rate`,
    `avg_baseline`,
    `std_deviation`,
    -- Calculate z-score
    CASE 
        WHEN `std_deviation` > 0 
        THEN (`error_rate` - `avg_baseline`) / `std_deviation`
        ELSE 0 
    END as `z_score`,
    -- Classify anomaly level based on z-score
    CASE
        WHEN `std_deviation` = 0 THEN 'STABLE'
        WHEN ABS((`error_rate` - `avg_baseline`) / `std_deviation`) > 3 THEN 'CRITICAL'
        WHEN ABS((`error_rate` - `avg_baseline`) / `std_deviation`) > 2 THEN 'WARNING'
        ELSE 'NORMAL'
    END as `anomaly_level`
FROM (
    SELECT 
        `window_start`,
        `source`,
        -- Current error rate
        CASE 
            WHEN `event_count` > 0 
            THEN CAST((`critical_count` + `error_count`) AS DOUBLE) / CAST(`event_count` AS DOUBLE)
            ELSE 0.0 
        END as `error_rate`,
        -- Rolling average (12 previous windows = 60 minutes)
        AVG(
            CASE 
                WHEN `event_count` > 0 
                THEN CAST((`critical_count` + `error_count`) AS DOUBLE) / CAST(`event_count` AS DOUBLE)
                ELSE 0.0 
            END
        ) OVER (
            PARTITION BY `source` 
            ORDER BY `window_start` 
            ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
        ) as `avg_baseline`,
        -- Rolling standard deviation
        STDDEV(
            CASE 
                WHEN `event_count` > 0 
                THEN CAST((`critical_count` + `error_count`) AS DOUBLE) / CAST(`event_count` AS DOUBLE)
                ELSE 0.0 
            END
        ) OVER (
            PARTITION BY `source` 
            ORDER BY `window_start` 
            ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
        ) as `std_deviation`
    FROM events_aggregated_5min
);
*/

-- ============================================================
-- QUERY EXAMPLES (for when data is populated)
-- ============================================================

-- View active anomalies
SELECT * FROM error_anomalies
WHERE `anomaly_level` IN ('CRITICAL', 'WARNING')
ORDER BY `window_start` DESC, ABS(`z_score`) DESC
LIMIT 20;

-- Find sources with critical anomalies
SELECT 
    `source`,
    `error_rate`,
    `avg_baseline`,
    `z_score`
FROM error_anomalies
WHERE `anomaly_level` = 'CRITICAL'
ORDER BY `window_start` DESC, ABS(`z_score`) DESC
LIMIT 10;

-- ============================================================
-- ALTERNATIVE: Application-Layer Anomaly Detection
-- ============================================================
--
-- Consider implementing z-score calculation in Python:
--
-- import numpy as np
-- 
-- def detect_anomaly(current_rate, historical_rates):
--     mean = np.mean(historical_rates)
--     std = np.std(historical_rates)
--     if std == 0:
--         return 'STABLE', 0
--     z_score = (current_rate - mean) / std
--     if abs(z_score) > 3:
--         return 'CRITICAL', z_score
--     elif abs(z_score) > 2:
--         return 'WARNING', z_score
--     return 'NORMAL', z_score
--
-- This approach is more flexible and works with streaming data.
-- ============================================================
