import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const HistoryPage = ({ onSelectHistory }) => {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await api.get('history/');
                setHistory(res.data);
            } catch (err) {
                console.error("Failed to fetch history");
            } finally {
                setIsLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const handleSelect = (item) => {
        onSelectHistory(item);
        navigate('/'); // Redirect to dashboard to view data
    };

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Inventory Logs</h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Access and review previous equipment data uploads.</p>
            </div>

            <div className="bg-white dark:bg-slate-850 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm border-collapse">
                        <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase font-bold text-slate-500 dark:text-slate-400">
                            <tr>
                                <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">Upload ID</th>
                                <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">Date & Time</th>
                                <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">File Name</th>
                                <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {isLoading ? (
                                <tr>
                                    <td colSpan="4" className="px-6 py-8 text-center text-slate-500">Loading history...</td>
                                </tr>
                            ) : history.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="px-6 py-8 text-center text-slate-500">No logs found.</td>
                                </tr>
                            ) : (
                                history.map((item) => (
                                    <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group">
                                        <td className="px-6 py-4 font-mono font-medium text-slate-900 dark:text-white">#{item.user_upload_index || item.id}</td>
                                        <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{new Date(item.uploaded_at).toLocaleString()}</td>
                                        <td className="px-6 py-4 text-slate-600 dark:text-slate-300 flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-400 text-[18px]">description</span>
                                            {item.filename || 'equipment_data.csv'}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleSelect(item)}
                                                className="text-primary hover:text-blue-600 font-medium text-sm px-3 py-1.5 bg-primary/10 hover:bg-primary/20 rounded-lg transition-colors"
                                            >
                                                View Data
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default HistoryPage;
