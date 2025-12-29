// Event sources configuration
export const sources = [
    { id: 'github', name: 'GitHub', icon: '🔧', color: 'from-gray-600 to-gray-800' },
    { id: 'datadog', name: 'Datadog', icon: '📊', color: 'from-purple-600 to-purple-800' },
    { id: 'kubernetes', name: 'Kubernetes', icon: '☸️', color: 'from-blue-600 to-blue-800' },
    { id: 'jenkins', name: 'Jenkins', icon: '🔨', color: 'from-red-600 to-red-800' },
    { id: 'pagerduty', name: 'PagerDuty', icon: '🚨', color: 'from-green-600 to-green-800' },
];

// Scenario configurations
export const scenarios = [
    { id: 'normal_operations', name: 'Normal Operations', icon: '✅', color: 'bg-green-500' },
    { id: 'deployment', name: 'Deployment', icon: '🚀', color: 'bg-blue-500' },
    { id: 'incident', name: 'Production Incident', icon: '🔥', color: 'bg-red-500' },
    { id: 'traffic_spike', name: 'Traffic Spike', icon: '📈', color: 'bg-yellow-500' },
];

// Event types by source
export const eventTypes = {
    github: ['com.github.push', 'com.github.pull_request.opened', 'com.github.pull_request.merged'],
    datadog: ['com.datadog.alert.warning', 'com.datadog.alert.error', 'com.datadog.alert.critical'],
    kubernetes: ['io.k8s.pod.started', 'io.k8s.pod.crash', 'io.k8s.deployment.scaled'],
    jenkins: ['com.jenkins.build.success', 'com.jenkins.build.failure', 'com.jenkins.deployment.started'],
    pagerduty: ['com.pagerduty.incident.triggered', 'com.pagerduty.incident.resolved'],
};

// API configuration with environment variable support
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Severity color mapping
export const severityColors = {
    critical: 'bg-red-500',
    error: 'bg-orange-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
};

// Health status color mapping
export const healthColors = {
    HEALTHY: 'text-green-500',
    WARNING: 'text-yellow-500',
    DEGRADED: 'text-orange-500',
    CRITICAL: 'text-red-500',
};

// Helper functions
export const getSeverityColor = (severity) => severityColors[severity] || 'bg-gray-500';
export const getHealthColor = (status) => healthColors[status] || 'text-gray-500';
