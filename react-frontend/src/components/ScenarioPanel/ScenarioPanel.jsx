import { useState } from 'react';
import { Play } from 'lucide-react';
import { scenarios, API_URL } from '../../constants';

const ScenarioPanel = ({ activeScenario }) => {
    const [isLoading, setIsLoading] = useState({});

    const runScenario = async (scenarioId) => {
        setIsLoading(prev => ({ ...prev, [scenarioId]: true }));

        try {
            const response = await fetch(`${API_URL}/api/scenario/${scenarioId}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error running scenario:', error);
            // Reset loading state on error
            setIsLoading(prev => ({ ...prev, [scenarioId]: false }));
        }
    };

    return (
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Play className="w-5 h-5 text-purple-400" />
                Quick Scenarios
            </h2>
            <div className="grid grid-cols-2 gap-3">
                {scenarios.map(scenario => (
                    <button
                        key={scenario.id}
                        onClick={() => runScenario(scenario.id)}
                        disabled={activeScenario === scenario.id || isLoading[scenario.id]}
                        className={`${scenario.color} hover:opacity-90 disabled:opacity-50 text-white rounded-lg p-4 flex items-center gap-3 transition-all transform hover:scale-105 active:scale-95`}
                    >
                        <span className="text-2xl">{scenario.icon}</span>
                        <span className="font-semibold">{scenario.name}</span>
                        {(activeScenario === scenario.id || isLoading[scenario.id]) && (
                            <div className="ml-auto">
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default ScenarioPanel;
