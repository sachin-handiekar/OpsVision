import { Activity, AlertTriangle } from 'lucide-react';

const StatsGrid = ({ stats }) => {
    return (
        <div className="grid grid-cols-4 gap-4">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                    <Activity className="w-5 h-5 text-blue-400" />
                    <span className="text-2xl font-bold">{stats.total}</span>
                </div>
                <p className="text-sm text-slate-400">Total Events</p>
            </div>
            <div className="bg-red-500/10 backdrop-blur border border-red-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <span className="text-2xl font-bold text-red-400">{stats.critical}</span>
                </div>
                <p className="text-sm text-slate-400">Critical</p>
            </div>
            <div className="bg-orange-500/10 backdrop-blur border border-orange-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                    <AlertTriangle className="w-5 h-5 text-orange-400" />
                    <span className="text-2xl font-bold text-orange-400">{stats.errors}</span>
                </div>
                <p className="text-sm text-slate-400">Errors</p>
            </div>
            <div className="bg-yellow-500/10 backdrop-blur border border-yellow-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-400" />
                    <span className="text-2xl font-bold text-yellow-400">{stats.warnings}</span>
                </div>
                <p className="text-sm text-slate-400">Warnings</p>
            </div>
        </div>
    );
};

export default StatsGrid;
