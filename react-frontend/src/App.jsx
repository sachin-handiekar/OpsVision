import { Header, StatsGrid, ScenarioPanel, EventForm, EventStream, AIInsights } from './components';
import useWebSocket from './hooks/useWebSocket';

const EventStreamDemo = () => {
    const { events, alerts, stats, isConnected, activeScenario } = useWebSocket();

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
            {/* Header */}
            <div className="mb-8">
                <Header isConnected={isConnected} />
                <StatsGrid stats={stats} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Event Simulator */}
                <div className="lg:col-span-2 space-y-6">
                    <ScenarioPanel activeScenario={activeScenario} />
                    <EventForm />
                    <EventStream events={events} />
                </div>

                {/* AI Alerts */}
                <AIInsights alerts={alerts} />
            </div>
        </div>
    );
};

export default EventStreamDemo;