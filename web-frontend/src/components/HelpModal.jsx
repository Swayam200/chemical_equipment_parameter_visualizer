import React from 'react';

const HelpModal = ({ onClose }) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-2xl border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col max-h-[90vh]">
                <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">help</span>
                        Project Guide
                    </h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                <div className="p-6 overflow-y-auto space-y-6 text-slate-600 dark:text-slate-300">
                    <section>
                        <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Introduction</h4>
                        <p>
                            ChemVis is a comprehensive tool for visualizing and analyzing chemical equipment parameters.
                            It helps engineers monitor real-time data, detect anomalies, and generate reports.
                        </p>
                    </section>

                    <section>
                        <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Dashboard & Charts</h4>
                        <ul className="list-disc pl-5 space-y-1">
                            <li><strong>System Overview:</strong> Displays aggregated metrics for all equipment.</li>
                            <li><strong>Distribution Chart:</strong> Shows the count of different equipment types (Reactors, Pumps, etc.).</li>
                            <li><strong>Averages Chart:</strong> Compares global average Flowrate, Pressure, and Temperature.</li>
                        </ul>
                    </section>

                    <section>
                        <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Anomaly Detection</h4>
                        <p>
                            The system automatically flags equipment that exceeds safety thresholds.
                            <ul className="list-disc pl-5 mt-1">
                                <li><strong>Warning:</strong> Parameter exceeds the configured percentile (e.g., 95th).</li>
                                <li><strong>Critical (Outlier):</strong> Parameter is statistically anomalous (IQR method).</li>
                            </ul>
                            You can configure these sensitivity settings in the <strong>Configuration</strong> menu.
                        </p>
                    </section>

                    <section>
                        <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Features</h4>
                        <ul className="list-disc pl-5 space-y-1">
                            <li><strong>Upload Logs:</strong> Import CSV files to analyze new batches.</li>
                            <li><strong>Export Data:</strong> Download PDF reports of the current analysis.</li>
                            <li><strong>History:</strong> View and restore previous analysis sessions.</li>
                        </ul>
                    </section>
                </div>

                <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-primary hover:bg-blue-600 text-white rounded-lg text-sm font-semibold transition-colors"
                    >
                        Got it
                    </button>
                </div>
            </div>
        </div>
    );
};

export default HelpModal;
