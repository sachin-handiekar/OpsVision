import { Activity, Server } from 'lucide-react';
import { getSeverityColor } from '../../constants';

const EventStream = ({ events }) => {
    return (
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                Live Event Stream
            </h2>
            <div className="space-y-2 max-h-80 overflow-y-auto">
                {events.length === 0 ? (
                    <div className="text-center text-slate-400 py-8">
                        <Server className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No events yet. Send an event or run a scenario!</p>
                    </div>
                ) : (
                    events.map((event, idx) => (
                        <div key={`${event.id || idx}-${event.time}`} className="bg-slate-700/50 border border-slate-600 rounded-lg p-3 hover:border-slate-500 transition-all">
                            <div className="flex items-start justify-between mb-1">
                                <div className="flex items-center gap-2">
                                    <span className={`w-2 h-2 rounded-full ${getSeverityColor(event.severity)}`}></span>
                                    <span className="font-semibold text-sm">{event.type}</span>
                                </div>
                                <span className="text-xs text-slate-400">
                                    {new Date(event.time).toLocaleTimeString()}
                                </span>
                            </div>
                            <p className="text-sm text-slate-300">{event.subject}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                                <span>Source: {event.source?.split('/')[2] || 'unknown'}</span>
                                <span>•</span>
                                <span className="capitalize">{event.severity}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default EventStream;
