# 🔍 OpsVision

> **AI-Powered Real-Time Event Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Confluent](https://img.shields.io/badge/Confluent-Kafka-FF6B35?logo=apache-kafka)](https://www.confluent.io/)
[![Flink](https://img.shields.io/badge/Apache%20Flink-SQL-E6526F?logo=apache-flink)](https://flink.apache.org)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OpsVision transforms raw operational events from multiple sources (GitHub, Kubernetes, Datadog, Jenkins, PagerDuty) into actionable intelligence using **Apache Kafka** for real-time streaming, **Apache Flink SQL** for stream processing, and **Google Gemini AI** for intelligent insights.

**🏆 Built for [AI Partner Catalyst: Accelerate Innovation](https://ai-partner-catalyst.devpost.com/) Hackathon**

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
  - [4. Flink SQL Setup](#4-flink-sql-setup)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Demo Scenarios](#-demo-scenarios)
- [Testing](#-testing)
- [Tech Stack](#-tech-stack)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Real-Time Streaming** | CloudEvents ingestion via Confluent Kafka with Avro serialization |
| 🤖 **AI-Powered Insights** | Google Gemini generates actionable recommendations from event patterns |
| 📊 **Live Dashboard** | React-based real-time dashboard with WebSocket updates |
| 🔗 **Event Correlation** | Flink SQL aggregates and correlates events across 5-minute windows |
| 📈 **System Health Monitoring** | Automatic health status classification (CRITICAL/DEGRADED/WARNING/HEALTHY) |
| 🎭 **Scenario Simulation** | Built-in scenarios for demos: Normal Ops, Deployment, Incident, Traffic Spike |
| 🔌 **Multi-Source Integration** | GitHub, Datadog, Kubernetes, Jenkins, PagerDuty webhook adapters |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EVENT SOURCES                                │
├──────────┬──────────┬───────────┬──────────┬──────────────────────┤
│  GitHub  │ Datadog  │ Kubernetes│ Jenkins  │     PagerDuty        │
└────┬─────┴────┬─────┴─────┬─────┴────┬─────┴──────────┬───────────┘
     │          │           │          │                │
     └──────────┴───────────┴──────────┴────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Event Collector)                     │
│                 Transforms webhooks → CloudEvents format              │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │ Avro
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 Confluent Cloud Kafka                                 │
│                 (cloudevents-stream topic)                            │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 Apache Flink SQL Pipeline                             │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │
│  │ Source Table   │→ │ 5-min Aggregation│→ │ Health + Correlation │   │
│  └────────────────┘  └─────────────────┘  └─────────────────────┘   │
│                                                      │               │
│                              ┌───────────────────────┘               │
│                              ▼                                        │
│                     ┌─────────────────┐                              │
│                     │ gemini_summary   │                              │
│                     │ (AI-ready output)│                              │
│                     └────────┬────────┘                              │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
     │ Google      │   │ FastAPI      │   │ React        │
     │ Gemini AI   │→  │ WebSocket    │→  │ Dashboard    │
     └─────────────┘   └──────────────┘   └──────────────┘
```

---

## 📁 Project Structure

```
OpsVision/
├── python-backend/          # FastAPI backend server
│   ├── app/
│   │   ├── config.py        # Configuration & environment
│   │   ├── models.py        # Pydantic models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Kafka, AI, WebSocket services
│   │   └── schemas/         # Avro schemas
│   ├── main.py              # Entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
│
├── react-frontend/          # React dashboard
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── hooks/           # Custom React hooks
│   │   └── App.jsx          # Main application
│   ├── package.json         # Node dependencies
│   └── .env.example         # Environment template
│
├── flink-ksql/              # Confluent Flink SQL scripts
│   └── src/
│       ├── 01_source_table_cloudevents.sql
│       ├── 02_events_aggregated_5min.sql
│       ├── 03_system_health_5min.sql
│       ├── 04_top_error_sources.sql
│       ├── 05_correlated_incidents.sql
│       ├── 08_gemini_summary.sql
│       └── ...
│
├── README.md                # This file
└── LICENSE                  # MIT License
```

---

## 📋 Prerequisites

- **Python 3.11+** - [Download](https://python.org)
- **Node.js 20+** - [Download](https://nodejs.org)
- **Confluent Cloud Account** - [Sign Up](https://confluent.io)
  - Kafka cluster
  - Flink compute pool (2+ CFUs recommended)
  - Schema Registry
- **Google Gemini API Key** - [Get API Key](https://ai.google.dev)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/sachin-handiekar/OpsVision.git
cd OpsVision
```

### 2. Backend Setup

```bash
cd python-backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Environment Configuration below)
```

### 3. Frontend Setup

```bash
cd react-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if using different backend URL
```

### 4. Flink SQL Setup

Execute the SQL files in order in the **Confluent Cloud Flink SQL Editor**:

1. **Create Source Table**: `01_source_table_cloudevents.sql`
2. **Create Aggregation Table**: `02_events_aggregated_5min.sql`
3. **Create Derived Tables** (can run in parallel):
   - `03_system_health_5min.sql`
   - `04_top_error_sources.sql`
   - `05_correlated_incidents.sql`
4. **Create AI Summary Table**: `08_gemini_summary.sql`

> **Note**: Each INSERT statement runs as a continuous streaming job in Confluent Cloud.

---

## ⚙️ Environment Configuration

### Backend (`python-backend/.env`)

```env
# Kafka Configuration (Confluent Cloud)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.region.gcp.confluent.cloud:9092
KAFKA_CLIENT_ID=opsvision-event-collector
KAFKA_EVENTS_TOPIC=cloudevents-stream
GEMINI_SUMMARY_TOPIC=gemini_summary

# Kafka Authentication
KAFKA_API_KEY=your-kafka-api-key
KAFKA_API_SECRET=your-kafka-api-secret

# Schema Registry
SCHEMA_REGISTRY_URL=https://your-sr.region.gcp.confluent.cloud
SCHEMA_REGISTRY_API_KEY=your-sr-api-key
SCHEMA_REGISTRY_API_SECRET=your-sr-api-secret

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

### Frontend (`react-frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 🏃 Running the Application

### Start Backend Server

```bash
cd python-backend
python main.py
```

Server starts at `http://localhost:8000`

### Start Frontend Development Server

```bash
cd react-frontend
npm run dev
```

Dashboard available at `http://localhost:5173`

### Verify Everything is Connected

1. Open the React dashboard in your browser
2. WebSocket connection indicator should show "Connected"
3. Use scenario simulation to test event flow

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info and health check |
| `GET` | `/api/stats` | Current event statistics |
| `GET` | `/api/templates` | Available event templates |
| `GET` | `/api/summaries` | Fetch AI summaries from Kafka |
| `POST` | `/api/simulate` | Send custom event to Kafka |
| `POST` | `/api/scenario/{name}` | Run predefined scenario |
| `WS` | `/ws` | Real-time WebSocket connection |

### Example: Simulate an Event

```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"event_type": "error", "source": "api-gateway", "count": 5}'
```

---

## 🎭 Demo Scenarios

Trigger pre-built scenarios via API or the dashboard:

| Scenario | Description | Events |
|----------|-------------|--------|
| `normal` | Steady stream of info-level events | ~20 events |
| `deployment` | CI/CD pipeline flow (build→deploy→verify) | ~15 events |
| `incident` | Production incident with critical alerts | ~25 events |
| `traffic_spike` | High-volume traffic increase simulation | ~30 events |

**Run via API:**
```bash
curl -X POST http://localhost:8000/api/scenario/incident
```

**Run via Dashboard:**
Click scenario buttons in the Scenario Panel section.

---

## 🧪 Testing

### Backend Tests

```bash
cd python-backend

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

### Frontend Build

```bash
cd react-frontend

# Lint code
npm run lint

# Build for production
npm run build
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI, Uvicorn
- **Streaming**: Apache Kafka (Confluent Cloud)
- **Serialization**: Avro + Schema Registry
- **AI**: Google Gemini 2.0 Flash
- **Real-time**: WebSockets

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite 7
- **Styling**: TailwindCSS 3
- **Icons**: Lucide React

### Stream Processing
- **Engine**: Apache Flink (Confluent Cloud)
- **Language**: Flink SQL
- **Event Format**: CloudEvents 1.0

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>⭐ Star this repo if you find it useful!</b>
  <br><br>
  Made with ❤️ using Confluent Kafka & Google Gemini
</p>
