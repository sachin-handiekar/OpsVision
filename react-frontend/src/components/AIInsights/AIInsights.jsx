import { Zap, TrendingUp, Clock } from 'lucide-react';
import { getHealthColor } from '../../constants';

const AIInsights = ({ alerts }) => {
    return (
        <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 backdrop-blur border border-purple-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-bold">AI Intelligence</h2>
                    <p className="text-sm text-purple-300">Powered by Gemini</p>
                </div>
            </div>

            <div className="space-y-4">
                {alerts.length === 0 ? (
                    <div className="text-center text-slate-400 py-12">
                        <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p className="text-sm">Waiting for AI analysis...</p>
                        <p className="text-xs mt-2">Summaries generated every 5 minutes</p>
                    </div>
                ) : (
                    alerts.map((alert, idx) => (
                        <div key={idx} className="bg-slate-800/50 border border-slate-600 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                                <span className={`text-lg font-bold ${getHealthColor(alert.health_status)}`}>
                                    {alert.health_status}
                                </span>
                                <Clock className="w-4 h-4 text-slate-400" />
                            </div>

                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Events:</span>
                                    <span className="font-semibold">{alert.total_events?.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Critical:</span>
                                    <span className="font-semibold text-red-400">{alert.critical_count || 0}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Errors:</span>
                                    <span className="font-semibold text-orange-400">{alert.error_count || 0}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Error Rate:</span>
                                    <span className="font-semibold">{alert.error_rate_percent?.toFixed(2)}%</span>
                                </div>
                            </div>

                            {alert.ai_insight && (
                                <div className="mt-4 pt-4 border-t border-slate-600">
                                    <p className="text-sm font-semibold text-purple-300 mb-2">🤖 AI Insight:</p>
                                    <p className="text-sm text-slate-300 leading-relaxed">
                                        {alert.ai_insight.insight}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AIInsights;
