import React, { useMemo, useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import api from '../api';
import { chartColors } from '../chartConfig';
import { useSearch } from '../context/SearchContext';

import { highlightText } from '../utils/textUtils';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const AdvancedAnalyticsPage = ({ data, theme = 'dark' }) => {
    const { searchQuery } = useSearch();

    // --- State Management ---
    // Toggle for the "Customize View" dropdown menu
    const [showViewMenu, setShowViewMenu] = useState(false);

    // Controls visibility of individual dashboard sections
    const [viewSettings, setViewSettings] = useState({
        showTrends: true,
        showCorrelation: true,
        showEfficiency: true,
        showTable: true
    });

    // Filter state for the Equipment Data Log table ('all', 'normal', 'warning', 'critical')
    const [statusFilter, setStatusFilter] = useState('all');

    const summary = data?.summary || {
        correlation_matrix: null,
        type_comparison: {},
        type_distribution: {}
    };
    const processedData = data?.processed_data || [];
    const colors = chartColors[theme] || chartColors.dark;

    // Filtered Data for Table
    const filteredTableData = useMemo(() => {
        let filtered = processedData.slice(0, 50); // Base subset
        if (statusFilter !== 'all') {
            filtered = filtered.filter(item => item.health_status === statusFilter);
        }
        return filtered;
    }, [processedData, statusFilter]);

    // --- Chart Data: Trends ---
    const trendChartData = useMemo(() => {
        const subset = processedData.slice(0, 50); // Show first 50 for clarity
        return {
            labels: subset.map(d => d['Equipment Name']),
            datasets: [
                {
                    label: 'Flowrate (L/min)',
                    data: subset.map(d => d['Flowrate']),
                    borderColor: colors.primaryBorder,
                    backgroundColor: colors.primary,
                    tension: 0.4,
                    yAxisID: 'y',
                },
                {
                    label: 'Temperature (°C)',
                    data: subset.map(d => d['Temperature']),
                    borderColor: colors.secondaryBorder,
                    backgroundColor: colors.secondary,
                    tension: 0.4,
                    yAxisID: 'y1',
                    borderDash: [5, 5],
                }
            ]
        }
    }, [processedData, colors]);

    // --- Chart Data: Type Comparison ---
    const comparisonChartData = useMemo(() => {
        const types = Object.keys(summary.type_comparison || {});
        return {
            labels: types,
            datasets: [
                {
                    label: 'Avg Flowrate',
                    data: types.map(t => summary.type_comparison[t].avg_flowrate),
                    backgroundColor: colors.primary,
                },
                {
                    label: 'Avg Pressure',
                    data: types.map(t => summary.type_comparison[t].avg_pressure),
                    backgroundColor: colors.secondary,
                }
            ]
        }
    }, [summary, colors]);


    return (
        <>
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{highlightText("Advanced Analytics", searchQuery)}</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Deep dive into flowrate trends, correlations, and equipment health status.</p>
                </div>
                <div className="flex gap-3 relative">
                    {/* Customize View Dropdown Trigger */}
                    <button
                        onClick={() => setShowViewMenu(!showViewMenu)}
                        className={`flex items-center gap-2 px-4 py-2 border rounded-lg shadow-sm transition-colors text-sm font-medium ${showViewMenu ? 'bg-primary text-white border-primary' : 'bg-white dark:bg-surface-dark border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
                    >
                        <span className="material-symbols-outlined text-[18px]">tune</span>
                        Customize View
                    </button>

                    {/* Customize View Dropdown Content */}
                    {showViewMenu && (
                        <div className="absolute top-12 right-0 w-64 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 p-4 z-50 animate-in fade-in zoom-in-95 duration-200">
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Toggle Visibility</h4>
                            <div className="space-y-2">
                                <label className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-lg">
                                    <input type="checkbox" checked={viewSettings.showTrends} onChange={() => setViewSettings(prev => ({ ...prev, showTrends: !prev.showTrends }))} className="rounded text-primary focus:ring-primary h-4 w-4 border-slate-300 dark:border-slate-600" />
                                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Trend Analysis</span>
                                </label>
                                <label className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-lg">
                                    <input type="checkbox" checked={viewSettings.showCorrelation} onChange={() => setViewSettings(prev => ({ ...prev, showCorrelation: !prev.showCorrelation }))} className="rounded text-primary focus:ring-primary h-4 w-4 border-slate-300 dark:border-slate-600" />
                                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Correlation Matrix</span>
                                </label>
                                <label className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-lg">
                                    <input type="checkbox" checked={viewSettings.showEfficiency} onChange={() => setViewSettings(prev => ({ ...prev, showEfficiency: !prev.showEfficiency }))} className="rounded text-primary focus:ring-primary h-4 w-4 border-slate-300 dark:border-slate-600" />
                                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Comparisons</span>
                                </label>
                                <label className="flex items-center gap-3 cursor-pointer p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-lg">
                                    <input type="checkbox" checked={viewSettings.showTable} onChange={() => setViewSettings(prev => ({ ...prev, showTable: !prev.showTable }))} className="rounded text-primary focus:ring-primary h-4 w-4 border-slate-300 dark:border-slate-600" />
                                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Data Table</span>
                                </label>
                            </div>
                        </div>
                    )}

                    <button className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg shadow-sm transition-colors text-sm font-medium">
                        <span className="material-symbols-outlined text-[18px]">download</span>
                        Export Report
                    </button>
                </div>
            </div>

            {/* Trend Analysis Section */}
            {viewSettings.showTrends && (
                <section className="bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-border-dark shadow-sm overflow-hidden p-6">
                    {/* ... (Keep existing content inside, just wrapping) ... */}
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-1.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                                <span className="material-symbols-outlined text-xl">ssid_chart</span>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900 dark:text-white text-base">{highlightText("Flowrate & Temperature Trends", searchQuery)}</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">Real-time sensor data aggregation</p>
                            </div>
                        </div>
                    </div>
                    <div className="h-[320px] w-full">
                        <Line data={trendChartData} options={{ maintainAspectRatio: false, responsive: true, interaction: { mode: 'index', intersect: false }, scales: { y: { type: 'linear', display: true, position: 'left', grid: { color: colors.grid }, ticks: { color: colors.text } }, y1: { type: 'linear', display: true, position: 'right', grid: { display: false }, ticks: { color: colors.text } }, x: { ticks: { color: colors.text }, grid: { display: false } } }, plugins: { legend: { labels: { color: colors.legendText } } } }} />
                    </div>
                </section>
            )}

            <div className={`grid grid-cols-1 ${viewSettings.showCorrelation && viewSettings.showEfficiency ? 'lg:grid-cols-3' : 'lg:grid-cols-1'} gap-6`}>
                {/* Correlation Matrix */}
                {viewSettings.showCorrelation && (
                    <div className="bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-border-dark shadow-sm p-6 flex flex-col">
                        <h3 className="font-semibold text-slate-900 dark:text-white mb-4">{highlightText("Correlation Matrix", searchQuery)}</h3>
                        {summary.correlation_matrix ? (
                            <div className="flex-1 flex flex-col justify-center items-center">
                                {/* ... (Keeping correlation matrix content same) ... */}
                                <div className="grid grid-cols-4 gap-1 w-full max-w-[320px]">
                                    <div className="h-10"></div>
                                    <div className="h-10 flex items-end justify-center text-xs font-bold text-slate-500 pb-2">Pres</div>
                                    <div className="h-10 flex items-end justify-center text-xs font-bold text-slate-500 pb-2">Temp</div>
                                    <div className="h-10 flex items-end justify-center text-xs font-bold text-slate-500 pb-2">Flow</div>

                                    {/* Row 1: Pressure */}
                                    <div className="h-16 flex items-center justify-end text-xs font-bold text-slate-500 pr-2">Pres</div>
                                    {[1.0, summary.correlation_matrix.Pressure.Temperature, summary.correlation_matrix.Pressure.Flowrate].map((val, i) => (
                                        <div key={i} className={`h-16 rounded flex items-center justify-center text-sm font-bold ${val > 0.7 ? 'text-white' : 'text-slate-700'}`} style={{ backgroundColor: val > 0 ? `rgba(25, 127, 230, ${Math.abs(val)})` : `rgba(220, 38, 38, ${Math.abs(val)})` }}>
                                            {val.toFixed(2)}
                                        </div>
                                    ))}

                                    {/* Row 2: Temperature */}
                                    <div className="h-16 flex items-center justify-end text-xs font-bold text-slate-500 pr-2">Temp</div>
                                    {[summary.correlation_matrix.Temperature.Pressure, 1.0, summary.correlation_matrix.Temperature.Flowrate].map((val, i) => (
                                        <div key={i} className={`h-16 rounded flex items-center justify-center text-sm font-bold ${val > 0.7 ? 'text-white' : 'text-slate-700'}`} style={{ backgroundColor: val > 0 ? `rgba(25, 127, 230, ${Math.abs(val)})` : `rgba(220, 38, 38, ${Math.abs(val)})` }}>
                                            {val.toFixed(2)}
                                        </div>
                                    ))}

                                    {/* Row 3: Flowrate */}
                                    <div className="h-16 flex items-center justify-end text-xs font-bold text-slate-500 pr-2">Flow</div>
                                    {[summary.correlation_matrix.Flowrate.Pressure, summary.correlation_matrix.Flowrate.Temperature, 1.0].map((val, i) => (
                                        <div key={i} className={`h-16 rounded flex items-center justify-center text-sm font-bold ${val > 0.7 ? 'text-white' : 'text-slate-700'}`} style={{ backgroundColor: val > 0 ? `rgba(25, 127, 230, ${Math.abs(val)})` : `rgba(220, 38, 38, ${Math.abs(val)})` }}>
                                            {val.toFixed(2)}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="flex h-full items-center justify-center text-slate-500 underline text-sm">Select data to view correlation</div>
                        )}
                    </div>
                )}

                {/* Type Comparison Bar Chart */}
                {viewSettings.showEfficiency && (
                    <div className={`bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-border-dark shadow-sm p-6 flex flex-col ${viewSettings.showCorrelation ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
                        <h3 className="font-semibold text-slate-900 dark:text-white mb-4">{highlightText("Type Efficiency Comparison", searchQuery)}</h3>
                        <div className="flex-1 min-h-[250px]">
                            <Bar data={comparisonChartData} options={{ maintainAspectRatio: false, responsive: true, scales: { y: { grid: { color: colors.grid }, ticks: { color: colors.text } }, x: { grid: { display: false }, ticks: { color: colors.text } } }, plugins: { legend: { display: true, position: 'top', labels: { color: colors.legendText } } } }} />
                        </div>
                    </div>
                )}
            </div>

            {/* Data Table */}
            {viewSettings.showTable && (
                <section className="bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-border-dark shadow-sm flex flex-col overflow-hidden">
                    <div className="px-6 py-4 border-b border-border-light dark:border-border-dark flex flex-col sm:flex-row justify-between items-center gap-4">
                        <h3 className="font-semibold text-slate-900 dark:text-white">{highlightText("Equipment Data Log", searchQuery)}</h3>
                        {/* Status Filter Control */}
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold text-slate-500 uppercase">Filter Status:</span>
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="all">All Statuses</option>
                                <option value="warning">Warning</option>
                                <option value="critical">Critical</option>
                                <option value="normal">Normal</option>
                            </select>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm border-collapse">
                            <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase font-bold text-slate-500 dark:text-slate-400">
                                <tr>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700">Equipment Name</th>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700">Type</th>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700 text-right">Flowrate</th>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700 text-right">Pressure</th>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700 text-right">Temperature</th>
                                    <th className="px-6 py-3 border-b border-slate-200 dark:border-slate-700 text-center">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                {filteredTableData.map((row, idx) => (
                                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                        <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">{highlightText(row['Equipment Name'], searchQuery)}</td>
                                        <td className="px-6 py-3">{highlightText(row['Type'], searchQuery)}</td>
                                        <td className="px-6 py-3 text-right font-mono text-slate-700 dark:text-slate-300">{row['Flowrate']}</td>
                                        <td className="px-6 py-3 text-right font-mono text-slate-700 dark:text-slate-300">{row['Pressure']}</td>
                                        <td className="px-6 py-3 text-right font-mono text-slate-700 dark:text-slate-300">{row['Temperature']}</td>
                                        <td className="px-6 py-3 text-center">
                                            {row.health_status === 'normal' ? (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">Normal</span>
                                            ) : row.health_status === 'critical' ? (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">Critical</span>
                                            ) : (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">Warning</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                                {filteredTableData.length === 0 && (
                                    <tr>
                                        <td colSpan="6" className="text-center py-8 text-slate-500">No equipment matches the filter.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </section>
            )}
        </>
    );
};

export default AdvancedAnalyticsPage;
