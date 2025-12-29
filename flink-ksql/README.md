# 🚀 EventStream Intelligence

> **Real-time event processing and system health monitoring powered by Confluent Cloud Flink SQL and Google Gemini AI**

[![Confluent Cloud](https://img.shields.io/badge/Confluent%20Cloud-Flink%20SQL-blue?style=for-the-badge&logo=apache-kafka)](https://confluent.io)
[![Apache Flink](https://img.shields.io/badge/Apache%20Flink-1.18+-E6526F?style=for-the-badge&logo=apache-flink)](https://flink.apache.org)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Powered-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![CloudEvents](https://img.shields.io/badge/CloudEvents-1.0-orange?style=for-the-badge)](https://cloudevents.io)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [SQL Components](#sql-components)
- [Setup Guide](#setup-guide)
- [Usage](#usage)
- [Demo](#demo)
- [Technical Details](#technical-details)
- [Limitations & Workarounds](#limitations--workarounds)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**EventStream Intelligence** is a real-time event processing pipeline that transforms raw operational events into actionable intelligence. Built entirely on **Confluent Cloud Flink SQL**, it processes CloudEvents from multiple sources (GitHub, Kubernetes, Datadog, PagerDuty, Jenkins) and provides:

- 📊 **5-minute aggregated health summaries**
- 🚨 **Real-time error detection and leaderboards**
- 🔗 **Cross-system incident correlation**
- 📈 **Statistical anomaly detection**
- 🤖 **AI-ready summaries for Google Gemini integration**

### Why Flink SQL?

Traditional event processing requires writing complex application code. With Flink SQL, we achieve:

| Traditional Approach | Flink SQL Approach |
|---------------------|-------------------|
| Custom aggregation code | Declarative SQL windowing |
| Manual state management | Automatic state handling |
| Complex deployment | Fully managed by Confluent |
| Scalability concerns | Auto-scaling compute pools |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           EVENT SOURCES                                       │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────────────┤
│  GitHub  │  K8s     │ Datadog  │ PagerDuty│ Jenkins  │  Custom Webhooks     │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴──────────┬───────────┘
     │          │          │          │          │                │
     ▼          ▼          ▼          ▼          ▼                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FastAPI Event Collector (CloudEvents)                      │
│                    Transforms webhooks → CloudEvents format                   │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Kafka Topic: cloudevents                              │
│                         (Confluent Cloud)                                     │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     FLINK SQL PROCESSING PIPELINE                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  01_source_table    →  CloudEvents ingestion with watermarks            │ │
│  └──────────────────────────────────────┬──────────────────────────────────┘ │
│                                         │                                     │
│  ┌──────────────────────────────────────▼──────────────────────────────────┐ │
│  │  02_events_aggregated  →  5-min tumbling windows per source             │ │
│  └──────────────────────────────────────┬──────────────────────────────────┘ │
│                    ┌────────────────────┼────────────────────┐               │
│                    ▼                    ▼                    ▼               │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐    │
│  │ 03_system_health    │ │ 04_top_error_sources│ │ 05_correlated_      │    │
│  │ (Global view)       │ │ (Error leaderboard) │ │    incidents        │    │
│  └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘    │
│             │                       │                       │               │
│             └───────────────────────┼───────────────────────┘               │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  08_gemini_summary  →  AI-ready consolidated view (ONE ROW PER WINDOW)  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Python Consumer + Google Gemini                            │
│                    Natural Language Incident Summaries                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🔄 Real-Time Event Processing
- **5-minute tumbling windows** for consistent time-based aggregation
- **Watermark handling** for out-of-order events (10-second tolerance)
- **Per-source metrics** including event counts and severity breakdown

### 📊 System Health Monitoring
- **Global health status**: CRITICAL → DEGRADED → WARNING → HEALTHY
- **Error rate calculation** as percentage of total events
- **Multi-source aggregation** for holistic system view

### 📈 Error Leaderboard
- **Top error sources** ranked by total error count
- **Critical event tracking** for immediate attention
- **Historical error patterns** across time windows

### 🔗 Incident Correlation
- **Cross-system incident detection** using correlation IDs
- **Duration tracking** for ongoing incidents
- **Multi-source impact analysis** 

### 🤖 AI-Ready Output
- **Denormalized summary table** optimized for LLM consumption
- **Google Gemini integration** for natural language insights
- **Automated incident reports** with actionable recommendations

---

## 📁 SQL Components

| File | Purpose | Key Features |
|------|---------|--------------|
| `01_source_table_cloudevents.sql` | Ingest CloudEvents from Kafka | Watermarks, event-time processing |
| `02_events_aggregated_5min.sql` | 5-minute window aggregations | TUMBLE windows, per-source metrics |
| `02a_events_aggregated_alternative.sql` | Alternative aggregation | Manual time bucketing for low-volume |
| `03_system_health_5min.sql` | Global health status | Error rate %, health classification |
| `04_top_error_sources.sql` | Error leaderboard | Ranked by total errors |
| `05_correlated_incidents.sql` | Incident correlation | Cross-system event grouping |
| `06_error_rate_trends.sql` | Trend analysis | SPIKE/IMPROVING/STABLE detection |
| `07_error_anomalies.sql` | Anomaly detection | Z-score analysis |
| `08_gemini_summary.sql` | AI-ready output | Consolidated metrics for Gemini |
| `09_utility_queries.sql` | Debug & demo queries | Verification and monitoring |
| `10_cleanup.sql` | Reset scripts | Safe table deletion |

---

## 🚀 Setup Guide

### Prerequisites

- **Confluent Cloud Account** with:
  - Kafka cluster (same region as Flink)
  - Flink compute pool (recommended: 2+ CFUs)
  - Schema Registry (optional, for Avro)

### Step 1: Create Kafka Topic

```bash
confluent kafka topic create cloudevents --partitions 3
```

### Step 2: Deploy Flink Tables

Execute SQL files in order in Confluent Cloud Flink SQL editor:

```sql
-- 1. Source table
-- Execute: 01_source_table_cloudevents.sql

-- 2. Aggregation layer
-- Execute: 02_events_aggregated_5min.sql
-- (Or 02a for low-volume scenarios)

-- 3. Derived tables (can run in parallel)
-- Execute: 03_system_health_5min.sql
-- Execute: 04_top_error_sources.sql
-- Execute: 05_correlated_incidents.sql

-- 4. AI summary
-- Execute: 08_gemini_summary.sql
```

### Step 3: Start INSERT Statements

Each INSERT runs as a **continuous streaming job** in Confluent Cloud:

1. Navigate to Flink → Statements
2. Run each INSERT statement
3. Monitor in the Statements dashboard

### Step 4: Verify Data Flow

```sql
-- Check events are flowing
SELECT COUNT(*) as events_last_5min
FROM cloudevents
WHERE `time` > CURRENT_TIMESTAMP - INTERVAL '5' MINUTES;

-- Check all table row counts
SELECT 'cloudevents' as table_name, COUNT(*) as row_count FROM cloudevents
UNION ALL
SELECT 'events_aggregated_5min', COUNT(*) FROM events_aggregated_5min
UNION ALL
SELECT 'gemini_summary', COUNT(*) FROM gemini_summary;
```

---

## 💡 Usage

### Querying System Health

```sql
-- Current health status
SELECT * FROM system_health_5min
ORDER BY `window_start` DESC
LIMIT 1;

-- Windows with critical status
SELECT *
FROM system_health_5min
WHERE `health_status` = 'CRITICAL'
ORDER BY `window_start` DESC
LIMIT 10;
```

### Finding Error Sources

```sql
-- Top 5 error sources in last hour
SELECT 
    `source`,
    SUM(`total_errors`) as total_errors
FROM top_error_sources_5min
WHERE `window_start` > CURRENT_TIMESTAMP - INTERVAL '1' HOURS
GROUP BY `source`
ORDER BY total_errors DESC
LIMIT 5;
```

### Incident Correlation

```sql
-- Cross-system incidents
SELECT 
    `correlation_id`,
    `event_count`,
    `source_count`,
    `duration_seconds`
FROM correlated_incidents
WHERE `source_count` >= 2
ORDER BY `event_count` DESC
LIMIT 10;
```

### AI Summary for Gemini

```sql
-- Get latest summary for AI processing
SELECT 
    `window_start`,
    `health_status`,
    `total_events`,
    `error_rate_percent`,
    `top_error_source`,
    `correlation_count`
FROM gemini_summary
ORDER BY `window_start` DESC
LIMIT 1;
```

---

## 🎬 Demo

### Sample AI Prompt Template

```
Analyze the following system health summary:

- Time Window: {window_start} to {window_end}
- Health Status: {health_status}
- Total Events: {total_events}
- Error Rate: {error_rate_percent}%
- Critical Events: {critical_count}
- Top Error Source: {top_error_source} ({top_error_count} errors)
- Correlated Incidents: {correlation_count}

Provide:
1. A brief status overview in plain English
2. Key concerns that need immediate attention
3. Recommended actions for the operations team
```

### Sample Gemini Response

> 🟡 **System Status: WARNING**
>
> The system is experiencing elevated error rates (8.5%) with 142 events 
> processed in the last 5-minute window. The primary concern is the 
> **kubernetes** source contributing 23 of the 34 total errors.
>
> **Recommended Actions:**
> 1. Investigate Kubernetes pod health and recent deployments
> 2. Check for resource exhaustion or OOM kills
> 3. Review the 2 correlated incidents for root cause

---

## 🔧 Technical Details

### CloudEvents Schema

```json
{
  "id": "event-123",
  "specversion": "1.0",
  "type": "deployment.failed",
  "source": "kubernetes",
  "time": "2024-01-15T10:30:00Z",
  "severity": "error",
  "category": "deployment",
  "correlation_id": "deploy-456",
  "subject": "pod/my-service-abc123",
  "data": "{\"reason\": \"ImagePullBackOff\"}"
}
```

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| `critical` | System-breaking issues | Immediate response |
| `error` | Failures requiring attention | Investigate soon |
| `warning` | Potential problems | Monitor closely |
| `info` | Informational events | No action needed |

### Health Status Logic

```sql
CASE
    WHEN SUM(`critical_count`) > 0 THEN 'CRITICAL'
    WHEN error_rate > 0.1 THEN 'DEGRADED'  -- >10% errors
    WHEN SUM(`error_count`) > 0 THEN 'WARNING'
    ELSE 'HEALTHY'
END
```

---

## ⚠️ Limitations & Workarounds

### Confluent Cloud Flink Streaming Limitations

| Feature | Status | Workaround |
|---------|--------|------------|
| `LAG()` window function | ❌ Not supported | Self-join with offset windows |
| `AVG/STDDEV OVER` | ❌ Not supported | Application-layer calculation |
| `ROW_NUMBER()` on non-time | ❌ Not supported | ORDER BY + LIMIT at query time |
| Watermark advancement | Requires ~250 events | Use manual time bucketing |

### When to Use Alternative Aggregation

Use `02a_events_aggregated_alternative.sql` when:
- Event volume is low (<250 events/5min/partition)
- You need immediate results for demos
- Development/testing scenarios

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Confluent Cloud** for managed Flink infrastructure
- **Apache Flink** for the stream processing engine
- **CloudEvents** for the event format specification
- **Google Gemini** for AI-powered insights

---

<p align="center">
  <b>Built with ❤️ for real-time observability</b>
</p>
