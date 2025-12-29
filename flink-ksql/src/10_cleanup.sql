-- ============================================================
-- Cleanup and Reset Scripts
-- ============================================================
--
-- PURPOSE:
-- Contains DROP statements to remove all tables and start fresh.
-- Use when you need to reset the system completely.
--
-- ⚠️ IMPORTANT WARNINGS:
-- 1. STOP all running INSERT statements FIRST in Confluent Cloud UI!
--    Running INSERTs will fail if tables are dropped.
-- 
-- 2. Tables MUST be dropped in REVERSE dependency order:
--    - Drop tables that depend on other tables first
--    - Then drop the tables they depend on
--
-- 3. All data will be PERMANENTLY DELETED!
--    Back up any data you need before running these commands.
--
-- 4. Associated Kafka topics may also be affected depending on
--    your Confluent Cloud settings.
-- ============================================================


-- ============================================================
-- STEP 1: Stop All Running Statements
-- ============================================================
--
-- Before dropping tables:
-- 1. Go to Confluent Cloud Console
-- 2. Navigate to Flink > Statements
-- 3. Stop all running INSERT statements
-- 4. Wait for them to fully stop
-- ============================================================


-- ============================================================
-- STEP 2: Drop Tables in Reverse Dependency Order
-- ============================================================

-- Level 4: Final output tables (depend on multiple sources)
DROP TABLE IF EXISTS gemini_summary;

-- Level 3: Analysis tables (depend on aggregated data)
DROP TABLE IF EXISTS error_anomalies;
DROP TABLE IF EXISTS error_rate_trends;

-- Level 2: Intermediate aggregation tables
DROP TABLE IF EXISTS correlated_incidents;
DROP TABLE IF EXISTS top_error_sources_5min;
DROP TABLE IF EXISTS system_health_5min;
DROP TABLE IF EXISTS events_aggregated_5min;

-- Level 1: Source table
DROP TABLE IF EXISTS cloudevents;


-- ============================================================
-- VERIFICATION: Confirm All Tables Dropped
-- ============================================================

-- List all tables (should be empty after cleanup)
SHOW TABLES;


-- ============================================================
-- OPTIONAL: Recreate Tables
-- ============================================================
--
-- After cleanup, run the SQL files in order:
-- 1. 01_source_table_cloudevents.sql
-- 2. 02_events_aggregated_5min.sql (or 02a for alternative)
-- 3. 03_system_health_5min.sql
-- 4. 04_top_error_sources.sql
-- 5. 05_correlated_incidents.sql
-- 6. 06_error_rate_trends.sql
-- 7. 07_error_anomalies.sql
-- 8. 08_gemini_summary.sql
-- ============================================================


-- ============================================================
-- NOTES FOR CONFLUENT CLOUD
-- ============================================================
--
-- 1. Tables automatically map to Kafka topics with the same name
-- 2. Dropping a table does NOT automatically delete the Kafka topic
-- 3. To fully clean up, you may need to delete topics separately
-- 4. Use Confluent Cloud UI to manage running statements
-- 5. Tables persist even if Flink compute pool is paused
-- 6. Monitor costs in Confluent Cloud billing dashboard
--
-- KAFKA TOPIC CLEANUP (if needed):
-- confluent kafka topic delete cloudevents
-- confluent kafka topic delete events_aggregated_5min
-- confluent kafka topic delete system_health_5min
-- confluent kafka topic delete top_error_sources_5min
-- confluent kafka topic delete correlated_incidents
-- confluent kafka topic delete error_rate_trends
-- confluent kafka topic delete error_anomalies
-- confluent kafka topic delete gemini_summary
-- ============================================================
