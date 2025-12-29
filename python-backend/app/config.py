# app/config.py
"""
Configuration and event templates for EventStream Intelligence
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Kafka Configuration
KAFKA_CONFIG: Dict[str, Any] = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
}

# Add SASL authentication if credentials are provided
if os.getenv('KAFKA_API_KEY') and os.getenv('KAFKA_API_SECRET'):
    KAFKA_CONFIG.update({
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('KAFKA_API_KEY'),
        'sasl.password': os.getenv('KAFKA_API_SECRET'),
    })

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Schema Registry Configuration (for Avro deserialization)
SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL')
SCHEMA_REGISTRY_CONFIG: Dict[str, Any] = {}
if SCHEMA_REGISTRY_URL:
    SCHEMA_REGISTRY_CONFIG = {
        'url': SCHEMA_REGISTRY_URL,
    }
    if os.getenv('SCHEMA_REGISTRY_API_KEY') and os.getenv('SCHEMA_REGISTRY_API_SECRET'):
        SCHEMA_REGISTRY_CONFIG['basic.auth.user.info'] = (
            f"{os.getenv('SCHEMA_REGISTRY_API_KEY')}:{os.getenv('SCHEMA_REGISTRY_API_SECRET')}"
        )

# Kafka Topics (can be overridden in .env)
CLOUDEVENTS_TOPIC = os.getenv('KAFKA_EVENTS_TOPIC', 'cloudevents-stream')
GEMINI_SUMMARY_TOPIC = os.getenv('GEMINI_SUMMARY_TOPIC', 'gemini-summary')

# Event Templates
EVENT_TEMPLATES = {
    "github": [
        {"type": "com.github.push", "severity": "info", "category": "cicd", "subject": "Push to main branch"},
        {"type": "com.github.pull_request.opened", "severity": "info", "category": "cicd", "subject": "New PR opened"},
        {"type": "com.github.pull_request.merged", "severity": "info", "category": "cicd", "subject": "PR merged"},
    ],
    "datadog": [
        {"type": "com.datadog.alert.warning", "severity": "warning", "category": "alert", "subject": "High latency detected"},
        {"type": "com.datadog.alert.error", "severity": "error", "category": "alert", "subject": "Service unavailable"},
        {"type": "com.datadog.alert.critical", "severity": "critical", "category": "alert", "subject": "Database connection failed"},
    ],
    "kubernetes": [
        {"type": "io.k8s.pod.started", "severity": "info", "category": "infrastructure", "subject": "Pod started successfully"},
        {"type": "io.k8s.pod.crash", "severity": "critical", "category": "infrastructure", "subject": "Pod crashed (OOMKilled)"},
        {"type": "io.k8s.deployment.scaled", "severity": "info", "category": "infrastructure", "subject": "Deployment scaled up"},
    ],
    "jenkins": [
        {"type": "com.jenkins.build.success", "severity": "info", "category": "cicd", "subject": "Build #142 succeeded"},
        {"type": "com.jenkins.build.failure", "severity": "error", "category": "cicd", "subject": "Build #143 failed"},
        {"type": "com.jenkins.deployment.started", "severity": "info", "category": "cicd", "subject": "Deployment to production"},
    ],
    "pagerduty": [
        {"type": "com.pagerduty.incident.triggered", "severity": "critical", "category": "incident", "subject": "P1 Incident - Service Down"},
        {"type": "com.pagerduty.incident.acknowledged", "severity": "warning", "category": "incident", "subject": "Incident acknowledged by team"},
        {"type": "com.pagerduty.incident.resolved", "severity": "info", "category": "incident", "subject": "Incident resolved"},
    ],
}

# Predefined Scenarios
SCENARIOS = {
    "normal_operations": {
        "name": "Normal Operations",
        "description": "Typical daily operations with mostly info events",
        "distribution": {"info": 80, "warning": 15, "error": 4, "critical": 1}
    },
    "deployment": {
        "name": "Deployment in Progress",
        "description": "Simulates a production deployment with related events",
        "events": [
            {"source": "github", "type": "com.github.push", "severity": "info", "subject": "Deploy commit abc123"},
            {"source": "jenkins", "type": "com.jenkins.build.success", "severity": "info", "subject": "Build #200 succeeded"},
            {"source": "kubernetes", "type": "io.k8s.deployment.scaled", "severity": "info", "subject": "Scaled to 10 replicas"},
            {"source": "datadog", "type": "com.datadog.alert.warning", "severity": "warning", "subject": "Brief latency spike"},
        ]
    },
    "incident": {
        "name": "Production Incident",
        "description": "Simulates a cascading failure scenario",
        "events": [
            {"source": "kubernetes", "type": "io.k8s.pod.crash", "severity": "critical", "subject": "payment-service crashed (OOM)", "correlation_id": "incident-001"},
            {"source": "datadog", "type": "com.datadog.alert.critical", "severity": "critical", "subject": "High error rate: payment-service", "correlation_id": "incident-001"},
            {"source": "pagerduty", "type": "com.pagerduty.incident.triggered", "severity": "critical", "subject": "P1: Payment service down", "correlation_id": "incident-001"},
            {"source": "github", "type": "com.github.pull_request.opened", "severity": "info", "subject": "Hotfix: Increase memory limits", "correlation_id": "incident-001"},
            {"source": "jenkins", "type": "com.jenkins.deployment.started", "severity": "info", "subject": "Deploying hotfix", "correlation_id": "incident-001"},
            {"source": "pagerduty", "type": "com.pagerduty.incident.resolved", "severity": "info", "subject": "Incident resolved", "correlation_id": "incident-001"},
        ]
    },
    "traffic_spike": {
        "name": "Traffic Spike",
        "description": "Sudden increase in traffic causing performance issues",
        "events": [
            {"source": "datadog", "type": "com.datadog.alert.warning", "severity": "warning", "subject": "Traffic increased 300%"},
            {"source": "kubernetes", "type": "io.k8s.deployment.scaled", "severity": "info", "subject": "Auto-scaled to 20 replicas"},
            {"source": "datadog", "type": "com.datadog.alert.warning", "severity": "warning", "subject": "High CPU usage"},
        ]
    }
}
