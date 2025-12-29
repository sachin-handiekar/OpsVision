import { Zap } from 'lucide-react';

const Header = ({ isConnected }) => {
    return (
        <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <Zap className="w-8 h-8" />
                </div>
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        EventStream Intelligence
                    </h1>
                    <p className="text-slate-400">Live Demo - Confluent + Vertex AI</p>
                </div>
            </div>
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${isConnected ? 'bg-green-500/20 border border-green-500/30' : 'bg-red-500/20 border border-red-500/30'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span className={`text-sm font-medium ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                </span>
            </div>
        </div>
    );
};

export default Header;
