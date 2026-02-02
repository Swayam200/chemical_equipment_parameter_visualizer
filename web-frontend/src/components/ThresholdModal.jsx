import React, { useState, useEffect } from 'react';
import api, { formatErrorMessage } from '../api';

const ThresholdModal = ({ onClose }) => {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [settings, setSettings] = useState({
        warning_percentile: 0.75,
        outlier_iqr_multiplier: 1.5,
    });
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            const response = await api.get('thresholds/');
            setSettings({
                warning_percentile: response.data.warning_percentile,
                outlier_iqr_multiplier: response.data.outlier_iqr_multiplier,
            });
            setError(null);
        } catch (err) {
            setError(formatErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setError(null);
            await api.put('thresholds/', settings);
            setSuccess('Settings saved successfully!');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(formatErrorMessage(err));
        } finally {
            setSaving(false);
        }
    };

    const handleReset = async () => {
        if (!window.confirm("Are you sure you want to reset to default thresholds?")) return;
        try {
            setSaving(true);
            await api.delete('thresholds/');
            await fetchSettings(); // Reload defaults
            setSuccess('Reset to defaults.');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(formatErrorMessage(err));
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col max-h-[90vh]">
                <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">Configuration</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                <div className="p-6 overflow-y-auto">
                    {loading ? (
                        <div className="flex justify-center p-8">
                            <span className="material-symbols-outlined animate-spin text-3xl text-primary">progress_activity</span>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {error && (
                                <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm border border-red-200 dark:border-red-800">
                                    {error}
                                </div>
                            )}
                            {success && (
                                <div className="bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 p-3 rounded-lg text-sm border border-green-200 dark:border-green-800">
                                    {success}
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Warning Percentile ({Math.round(settings.warning_percentile * 100)}%)
                                </label>
                                <input
                                    type="range"
                                    min="0.50"
                                    max="0.95"
                                    step="0.05"
                                    value={settings.warning_percentile}
                                    onChange={(e) => setSettings({ ...settings, warning_percentile: parseFloat(e.target.value) })}
                                    className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
                                />
                                <p className="text-xs text-slate-500 mt-1">
                                    Parameters above this percentile are flagged as warnings.
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Outlier IQR Multiplier ({settings.outlier_iqr_multiplier}x)
                                </label>
                                <input
                                    type="number"
                                    min="0.5"
                                    max="3.0"
                                    step="0.1"
                                    value={settings.outlier_iqr_multiplier}
                                    onChange={(e) => setSettings({ ...settings, outlier_iqr_multiplier: parseFloat(e.target.value) })}
                                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                />
                                <p className="text-xs text-slate-500 mt-1">
                                    Controls sensitivity of anomaly detection (Lower = More Sensitive).
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-between">
                    <button
                        onClick={handleReset}
                        disabled={saving || loading}
                        className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-500 text-sm font-medium transition-colors"
                    >
                        Reset Defaults
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving || loading}
                        className="px-6 py-2 bg-primary hover:bg-blue-600 text-white rounded-lg text-sm font-semibold shadow-sm shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {saving && <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>}
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ThresholdModal;
