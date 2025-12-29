# OpsVision - EventStream Intelligence

<div align="center">

![OpsVision Logo](https://img.shields.io/badge/OpsVision-EventStream%20Intelligence-blue?style=for-the-badge&logo=apache-kafka)

**Real-time DevOps event monitoring with AI-powered insights**

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-06B6D4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)
[![Confluent](https://img.shields.io/badge/Confluent-Kafka-FF6B35?style=flat-square&logo=apache-kafka)](https://www.confluent.io/)
[![Vertex AI](https://img.shields.io/badge/Google-Gemini-4285F4?style=flat-square&logo=google)](https://cloud.google.com/vertex-ai)

[Demo](#demo) • [Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [API](#api)

</div>

---

## 🎯 Overview

OpsVision is an intelligent event streaming dashboard that aggregates DevOps events from multiple sources (GitHub, Datadog, Kubernetes, Jenkins, PagerDuty), processes them through Confluent Kafka, and provides AI-powered insights using Google Gemini.

### The Problem
DevOps teams are overwhelmed by alerts and events from multiple monitoring tools, making it difficult to identify critical issues quickly.

### Our Solution
OpsVision unifies all event streams into a single dashboard with:
- **Real-time event aggregation** via WebSocket
- **AI-powered analysis** that identifies patterns and anomalies
- **Scenario simulation** for demos and testing
- **Heath status tracking** with intelligent severity classification

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔴 **Live Event Stream** | Real-time WebSocket connection displaying events as they occur |
| 🤖 **AI Intelligence** | Google Gemini analyzes event patterns and provides actionable insights |
| 📊 **Multi-Source Integration** | GitHub, Datadog, Kubernetes, Jenkins, PagerDuty webhooks |
| 🎭 **Scenario Simulation** | Pre-built scenarios: Normal Operations, Deployment, Incident, Traffic Spike |
| 📈 **Statistics Dashboard** | Track total events, critical alerts, errors, and warnings |
| ⚡ **Custom Event Sender** | Send custom events directly to Kafka for testing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Event Sources                            │
├─────────┬─────────┬─────────────┬──────────┬──────────────────┤
│ GitHub  │ Datadog │ Kubernetes  │ Jenkins  │    PagerDuty     │
└────┬────┴────┬────┴──────┬──────┴────┬─────┴────────┬─────────┘
     │         │           │           │              │
     └─────────┴───────────┴───────────┴──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Confluent Kafka      │
              │   (Event Streaming)    │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   FastAPI Backend      │
              │   + WebSocket Server   │
              └───────────┬────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌────────────┐   ┌──────────┐
    │  React   │   │  Vertex AI │   │  Flink   │
    │ Frontend │   │  (Gemini)  │   │ (Stream) │
    └──────────┘   └────────────┘   └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- FastAPI backend running on port 8000 (see [backend repo](#))
- Confluent Cloud account (for Kafka)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/opsvision.git
cd opsvision

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your backend URL

# Start development server
npm run dev
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | FastAPI backend URL | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulate` | Send a custom event to Kafka |
| `POST` | `/api/scenario/{id}` | Run a pre-built scenario |
| `WS` | `/ws` | WebSocket connection for real-time events |

### WebSocket Events

```javascript
// Event received from stream
{ type: 'event_sent', event: { ... } }

// AI analysis summary
{ type: 'ai_alert', summary: { health_status, ai_insight, ... } }

// Scenario lifecycle
{ type: 'scenario_started', scenario: 'incident' }
{ type: 'scenario_completed', scenario: 'incident' }
```

---

## 🛠️ Tech Stack

**Frontend**
- React 19 with hooks
- Vite 7 for blazing-fast builds
- TailwindCSS 3 for styling
- Lucide React for icons

**Backend** (separate repository)
- FastAPI + WebSocket
- Confluent Kafka (Cloud)
- Apache Flink for stream processing
- Google Vertex AI (Gemini)

---

## 📁 Project Structure

```
opsvision/
├── src/
│   ├── components/
│   │   ├── Header/
│   │   ├── StatsGrid/
│   │   ├── ScenarioPanel/
│   │   ├── EventForm/
│   │   ├── EventStream/
│   │   └── AIInsights/
│   ├── hooks/
│   │   └── useWebSocket.js
│   ├── constants/
│   │   └── sources.js
│   ├── App.jsx
│   └── main.jsx
├── public/
├── .env.example
└── package.json
```

---

## 🎬 Demo

> 🎥 **Video demo coming soon!**

### Running Scenarios

1. **Normal Operations** - Steady stream of info-level events
2. **Deployment** - CI/CD pipeline events (build, deploy, verify)
3. **Production Incident** - Critical alerts, pod crashes, PagerDuty triggers
4. **Traffic Spike** - High-volume events simulating load increase

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🏆 Hackathon

Built for [Hackathon Name] - [Date]

**Team:** [Your Name]

---

<div align="center">
Made with ❤️ using Confluent Kafka & Google Gemini
</div>
