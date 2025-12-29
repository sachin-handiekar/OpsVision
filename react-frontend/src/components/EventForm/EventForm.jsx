import { useState } from 'react';
import { Send } from 'lucide-react';
import { sources, eventTypes, API_URL } from '../../constants';

const EventForm = () => {
    const [selectedSource, setSelectedSource] = useState('github');
    const [customEvent, setCustomEvent] = useState({
        subject: '',
        severity: 'info',
        category: 'other'
    });
    const [isSending, setIsSending] = useState(false);

    const sendEvent = async () => {
        if (!customEvent.subject) return;

        setIsSending(true);

        try {
            const response = await fetch(`${API_URL}/api/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: selectedSource,
                    event_type: eventTypes[selectedSource][0],
                    severity: customEvent.severity,
                    subject: customEvent.subject,
                    category: customEvent.category
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            setCustomEvent({ subject: '', severity: 'info', category: 'other' });
        } catch (error) {
            console.error('Error sending event:', error);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Send className="w-5 h-5 text-blue-400" />
                Send Custom Event
            </h2>

            {/* Source Selection */}
            <div className="mb-4">
                <label className="text-sm text-slate-400 mb-2 block">Event Source</label>
                <div className="grid grid-cols-5 gap-2">
                    {sources.map(source => (
                        <button
                            key={source.id}
                            onClick={() => setSelectedSource(source.id)}
                            className={`p-3 rounded-lg transition-all ${selectedSource === source.id
                                ? `bg-gradient-to-br ${source.color} text-white shadow-lg scale-105`
                                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                                }`}
                        >
                            <div className="text-2xl mb-1">{source.icon}</div>
                            <div className="text-xs font-medium">{source.name}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Event Details */}
            <div className="space-y-3">
                <div>
                    <label className="text-sm text-slate-400 mb-2 block">Subject / Message</label>
                    <input
                        type="text"
                        value={customEvent.subject}
                        onChange={(e) => setCustomEvent({ ...customEvent, subject: e.target.value })}
                        placeholder="e.g., Deployed to production"
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                    />
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="text-sm text-slate-400 mb-2 block">Severity</label>
                        <select
                            value={customEvent.severity}
                            onChange={(e) => setCustomEvent({ ...customEvent, severity: e.target.value })}
                            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="info">Info</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-sm text-slate-400 mb-2 block">Category</label>
                        <select
                            value={customEvent.category}
                            onChange={(e) => setCustomEvent({ ...customEvent, category: e.target.value })}
                            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="cicd">CI/CD</option>
                            <option value="infrastructure">Infrastructure</option>
                            <option value="alert">Alert</option>
                            <option value="incident">Incident</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>

                <button
                    onClick={sendEvent}
                    disabled={!customEvent.subject || isSending}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-all transform hover:scale-105 active:scale-95"
                >
                    {isSending ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Sending...
                        </>
                    ) : (
                        <>
                            <Send className="w-5 h-5" />
                            Send Event to Kafka
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default EventForm;
