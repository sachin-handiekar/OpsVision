import { useState, useEffect, useRef } from 'react';
import { WS_URL } from '../constants';

/**
 * Custom hook for WebSocket connection management
 * Handles connection, reconnection, and message processing
 */
export const useWebSocket = () => {
    const [events, setEvents] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState({ total: 0, critical: 0, errors: 0, warnings: 0 });
    const [isConnected, setIsConnected] = useState(false);
    const [activeScenario, setActiveScenario] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    useEffect(() => {
        const connectWebSocket = () => {
            // Clear any existing reconnect timeout
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }

            try {
                const ws = new WebSocket(WS_URL);

                ws.onopen = () => {
                    setIsConnected(true);
                    console.log('WebSocket connected to:', WS_URL);
                };

                ws.onclose = (event) => {
                    setIsConnected(false);
                    console.log('WebSocket disconnected:', event.code, event.reason);

                    // Reconnect after 3 seconds
                    reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    setIsConnected(false);
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);

                        if (data.type === 'event_sent') {
                            setEvents(prev => [data.event, ...prev].slice(0, 50));
                            setStats(prev => ({
                                total: prev.total + 1,
                                critical: prev.critical + (data.event.severity === 'critical' ? 1 : 0),
                                errors: prev.errors + (data.event.severity === 'error' ? 1 : 0),
                                warnings: prev.warnings + (data.event.severity === 'warning' ? 1 : 0)
                            }));
                        } else if (data.type === 'ai_alert') {
                            setAlerts(prev => [data.summary, ...prev].slice(0, 10));
                        } else if (data.type === 'scenario_started') {
                            setActiveScenario(data.scenario);
                        } else if (data.type === 'scenario_completed') {
                            setActiveScenario(null);
                        }
                    } catch (parseError) {
                        console.error('Error parsing WebSocket message:', parseError);
                    }
                };

                wsRef.current = ws;
            } catch (error) {
                console.error('Error creating WebSocket:', error);
                reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
            }
        };

        connectWebSocket();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    return {
        events,
        alerts,
        stats,
        isConnected,
        activeScenario,
        setActiveScenario,
    };
};

export default useWebSocket;

