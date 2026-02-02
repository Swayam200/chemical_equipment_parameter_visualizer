import React, { useState, useMemo, useRef } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import FileUpload from '../components/FileUpload';
import api from '../api';
import { chartColors } from '../chartConfig';
import { useSearch } from '../context/SearchContext';

import { highlightText } from '../utils/textUtils';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const MainPage = ({ data, onUploadSuccess, theme = 'dark' }) => { // Default to dark if undefined
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [showDiagnostics, setShowDiagnostics] = useState(false);
    const { searchQuery } = useSearch();
    const anomaliesRef = useRef(null);

    const scrollToAnomalies = () => {
        anomaliesRef.current?.scrollIntoView({ behavior: 'smooth' });
    };



    // Safety check for empty data
    const summary = data?.summary || {
        total_count: 0,
        avg_flowrate: 0,
        avg_pressure: 0,
        avg_temperature: 0,
        type_distribution: {},
        outliers: []
    };

    const colors = chartColors[theme] || chartColors.dark;

    // --- Chart Data ---
    const typeChartData = useMemo(() => {
        const labels = Object.keys(summary.type_distribution);
        const values = Object.values(summary.type_distribution);
        return {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    colors.primary,
                    '#6366f1', // Indigo (mixers)
                    '#94a3b8', // Gray (storage)
                    colors.tertiary,
                    colors.quinary,
                    colors.senary,
                ],
                borderWidth: 0,
            }],
        };
    }, [summary, colors]);

    const statsChartData = useMemo(() => {
        return {
            labels: ['Avg Flowrate', 'Avg Pressure', 'Avg Temp'],
            datasets: [{
                label: 'Global Averages',
                data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature],
                backgroundColor: [colors.primary, colors.secondary, colors.tertiary],
                borderRadius: 4,
                barThickness: 40,
            }],
        };
    }, [summary, colors]);

    // --- Actions ---
    const handleExport = async () => {
        if (!data?.id) return;
        try {
            const response = await api.get(`/report/${data.id}/`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${data.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            console.error("Export failed", error);
        }
    };

    return (
        <>
            {/* Page Heading & Actions */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">{highlightText("System Overview", searchQuery)}</h2>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Real-time chemical equipment parameter monitoring and diagnostics.</p>
                </div>
                <div className="flex flex-wrap gap-2">

                    <button
                        onClick={() => setShowUploadModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                    >
                        <span className="material-symbols-outlined text-[20px]">upload_file</span>
                        Upload Logs
                    </button>
                    <button
                        onClick={handleExport}
                        className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-blue-600 text-white rounded-lg text-sm font-semibold shadow-sm shadow-blue-500/30 transition-colors"
                    >
                        <span className="material-symbols-outlined text-[20px]">download</span>
                        Export Data
                    </button>
                </div>
            </div>

            {/* Empty State vs Content */}
            {summary.total_count === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh] text-center p-8 bg-white dark:bg-slate-850 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm border-dashed">
                    <div className="bg-primary/10 p-6 rounded-full text-primary mb-6">
                        <span className="material-symbols-outlined text-6xl">cloud_off</span>
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">No Equipment Data Available</h2>
                    <p className="text-slate-500 dark:text-slate-400 max-w-md mb-8">
                        Upload a CSV log file to view analytics, or check the inventory history for past records.
                    </p>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setShowUploadModal(true)}
                            className="px-6 py-3 bg-primary hover:bg-blue-600 text-white rounded-lg font-semibold shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2"
                        >
                            <span className="material-symbols-outlined">upload_file</span>
                            Upload New Log
                        </button>
                        <a
                            href="/history"
                            className="px-6 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-lg font-semibold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all flex items-center gap-2"
                        >
                            <span className="material-symbols-outlined">history</span>
                            View History
                        </a>
                    </div>
                </div>
            ) : (
                <>
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="glass-card bg-white dark:bg-slate-850 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                                    <span className="material-symbols-outlined">precision_manufacturing</span>
                                </div>
                                <span className="flex items-center text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full">
                                    <span className="material-symbols-outlined text-[14px] mr-1">trending_up</span> +2 New
                                </span>
                            </div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{highlightText("Total Equipment", searchQuery)}</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{summary.total_count} Units</p>
                        </div>

                        <div className="glass-card bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-2 bg-cyan-50 dark:bg-cyan-900/20 rounded-lg text-cyan-600 dark:text-cyan-400">
                                    <span className="material-symbols-outlined">water_drop</span>
                                </div>
                                <span className="flex items-center text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-full">
                                    <span className="material-symbols-outlined text-[14px] mr-1">trending_flat</span> Stable
                                </span>
                            </div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{highlightText("Avg. Flowrate", searchQuery)}</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{summary.avg_flowrate.toFixed(1)} L/min</p>
                        </div>

                        <div className="glass-card bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-purple-600 dark:text-purple-400">
                                    <span className="material-symbols-outlined">compress</span>
                                </div>
                                <span className="flex items-center text-xs font-medium text-red-600 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded-full">
                                    <span className="material-symbols-outlined text-[14px] mr-1">trending_up</span> +1.2%
                                </span>
                            </div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{highlightText("Avg. Pressure", searchQuery)}</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{summary.avg_pressure.toFixed(1)} Bar</p>
                        </div>

                        <div className="glass-card bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg text-orange-600 dark:text-orange-400">
                                    <span className="material-symbols-outlined">thermostat</span>
                                </div>
                                <span className="flex items-center text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full">
                                    <span className="material-symbols-outlined text-[14px] mr-1">trending_down</span> -0.5%
                                </span>
                            </div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{highlightText("Avg. Temperature", searchQuery)}</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{summary.avg_temperature.toFixed(1)}°C</p>
                        </div>
                    </div>

                    {/* Anomaly Banner */}
                    {summary.outliers && summary.outliers.length > 0 && (
                        <div ref={anomaliesRef} className="w-full @container">
                            <div className="flex flex-col gap-4 rounded-xl border-l-4 border-l-red-500 border-y border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-850 p-5 shadow-sm transition-all">
                                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                                    <div className="flex gap-4">
                                        <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded-full h-fit text-red-600 dark:text-red-400">
                                            <span className="material-symbols-outlined">warning</span>
                                        </div>
                                        <div className="flex flex-col gap-1">
                                            <p className="text-slate-900 dark:text-white text-base font-bold leading-tight">
                                                {highlightText("Critical Alert: System Anomaly Detected", searchQuery)}
                                            </p>
                                            <p className="text-slate-500 dark:text-slate-400 text-sm font-normal leading-normal">
                                                {summary.outliers.length} equipment units have exceeded safety thresholds.
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setShowDiagnostics(!showDiagnostics)}
                                        className="whitespace-nowrap flex cursor-pointer items-center justify-center overflow-hidden rounded-lg h-9 px-4 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800 text-sm font-medium leading-normal transition-colors"
                                    >
                                        {showDiagnostics ? 'Hide Details' : 'View Diagnostics'}
                                        <span className="material-symbols-outlined text-[18px] ml-1">
                                            {showDiagnostics ? 'expand_less' : 'expand_more'}
                                        </span>
                                    </button>
                                </div>

                                {/* Expanded Details */}
                                {showDiagnostics && (
                                    <div className="mt-4 border-t border-slate-200 dark:border-slate-700 pt-4 animate-in fade-in slide-in-from-top-2 duration-300">
                                        <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-3">Anomaly Breakdown</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                            {summary.outliers.map((outlier, idx) => (
                                                <div key={idx} className="p-3 bg-red-50/50 dark:bg-red-900/10 rounded-lg border border-red-100 dark:border-red-800/50 flex flex-col gap-1">
                                                    <div className="flex justify-between items-center">
                                                        <span className="font-semibold text-slate-800 dark:text-slate-200 text-sm">{highlightText(outlier.equipment || `Unit #${idx + 1}`, searchQuery)}</span>
                                                        <span className="text-xs font-bold text-red-600 bg-red-100 dark:bg-red-900/40 px-2 py-0.5 rounded-full">Critical</span>
                                                    </div>
                                                    <div className="text-xs text-slate-600 dark:text-slate-400 mt-1 space-y-1">
                                                        {outlier.parameters && outlier.parameters.map((param, pIdx) => (
                                                            <div key={pIdx} className="flex justify-between">
                                                                <span className="capitalize">{param.parameter}:</span>
                                                                <span className="font-mono font-medium text-red-600 dark:text-red-400">
                                                                    {param.value.toFixed(2)}
                                                                </span>
                                                            </div>
                                                        ))}
                                                        {(!outlier.parameters || outlier.parameters.length === 0) && (
                                                            <div className="italic text-slate-400">No details available</div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Charts Section */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Doughnut Chart */}
                        <div className="bg-white dark:bg-slate-850 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{highlightText("Equipment Distribution", searchQuery)}</h3>
                            </div>
                            <div className="flex-1 flex flex-col items-center justify-center relative min-h-[250px]">
                                <div className="relative w-full h-[200px] flex items-center justify-center">
                                    {summary.total_count > 0 ? (
                                        <Doughnut
                                            data={typeChartData}
                                            options={{
                                                cutout: '75%',
                                                maintainAspectRatio: false,
                                                plugins: { legend: { display: false } }
                                            }}
                                        />
                                    ) : (
                                        <p className="text-slate-400 text-sm">No data available</p>
                                    )}
                                    {/* Center Text */}
                                    {summary.total_count > 0 && (
                                        <div className="absolute inset-0 m-auto w-fit h-fit flex flex-col items-center justify-center pointer-events-none">
                                            <span className="text-4xl font-bold text-slate-900 dark:text-white leading-none">{summary.total_count}</span>
                                            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mt-1">TOTAL</span>
                                        </div>
                                    )}
                                </div>
                                {/* Custom Legend */}
                                {summary.total_count > 0 && (
                                    <div className="flex flex-wrap justify-center gap-x-4 gap-y-2 mt-6">
                                        {typeChartData.labels.map((label, index) => (
                                            <div key={label} className="flex items-center gap-1.5">
                                                <div
                                                    className="w-2.5 h-2.5 rounded-full"
                                                    style={{ backgroundColor: typeChartData.datasets[0].backgroundColor[index] }}
                                                ></div>
                                                <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
                                                    {label}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Bar Chart */}
                        <div className="lg:col-span-2 bg-white dark:bg-slate-850 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{highlightText("Parameter Averages", searchQuery)}</h3>
                                    <p className="text-xs text-slate-500">Global averages for all equipment.</p>
                                </div>
                            </div>
                            <div className="flex-1 min-h-[250px]">
                                <Bar
                                    data={statsChartData}
                                    options={{
                                        maintainAspectRatio: false,
                                        responsive: true,
                                        scales: {
                                            y: { grid: { color: colors.grid }, ticks: { color: colors.text } },
                                            x: { grid: { display: false }, ticks: { color: colors.text } }
                                        },
                                        plugins: { legend: { display: false } }
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700 relative overflow-hidden">
                        <button
                            onClick={() => setShowUploadModal(false)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                        >
                            <span className="material-symbols-outlined">close</span>
                        </button>
                        <div className="p-6">
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Upload Equipment Logs</h3>
                            <FileUpload onUploadSuccess={(d) => {
                                onUploadSuccess(d);
                                setShowUploadModal(false);
                            }} />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default MainPage;
