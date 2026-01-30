import React, { useMemo, useState, useEffect, useRef } from 'react';
import api, { formatErrorMessage } from '../api';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement
} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { FaFilePdf, FaChevronDown, FaChevronUp, FaExclamationTriangle, FaCheckCircle, FaTimesCircle, FaCog, FaSearchPlus, FaUndo, FaSave, FaSync } from 'react-icons/fa';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement,
    zoomPlugin
);

// Theme-aware color palettes
const chartColors = {
    dark: {
        primary: 'rgba(102, 252, 241, 0.7)',      // Neon Cyan
        primaryBorder: '#66fcf1',
        secondary: 'rgba(69, 162, 158, 0.7)',     // Teal  
        secondaryBorder: '#45a29e',
        tertiary: 'rgba(252, 32, 68, 0.7)',       // Neon Red
        tertiaryBorder: '#fc2044',
        quaternary: 'rgba(32, 252, 143, 0.7)',    // Neon Green
        quaternaryBorder: '#20fc8f',
        quinary: 'rgba(224, 168, 0, 0.7)',        // Amber
        quinaryBorder: '#e0a800',
        senary: 'rgba(168, 85, 247, 0.7)',        // Purple
        senaryBorder: '#a855f7',
        grid: '#30363d',
        text: '#8b949e',
        legendText: '#e6edf3',
        tooltipBg: 'rgba(11, 12, 16, 0.95)',
        tooltipTitle: '#66fcf1',
        tooltipBody: '#c5c6c7',
        tooltipBorder: '#45a29e',
    },
    light: {
        primary: 'rgba(6, 182, 212, 0.75)',       // Cyan-500 (darker, more saturated)
        primaryBorder: '#0891b2',
        secondary: 'rgba(20, 184, 166, 0.75)',    // Teal-500
        secondaryBorder: '#0d9488',
        tertiary: 'rgba(239, 68, 68, 0.75)',      // Red-500 (warmer coral)
        tertiaryBorder: '#dc2626',
        quaternary: 'rgba(34, 197, 94, 0.75)',    // Green-500
        quaternaryBorder: '#16a34a',
        quinary: 'rgba(245, 158, 11, 0.75)',      // Amber-500
        quinaryBorder: '#d97706',
        senary: 'rgba(139, 92, 246, 0.75)',       // Violet-500
        senaryBorder: '#7c3aed',
        grid: '#e2e8f0',          // Slate-200
        text: '#64748b',          // Slate-500
        legendText: '#0f172a',    // Slate-900 (matches --text-primary)
        tooltipBg: 'rgba(255, 255, 255, 0.98)',
        tooltipTitle: '#0f172a',  // Slate-900
        tooltipBody: '#475569',   // Slate-600
        tooltipBorder: '#e2e8f0', // Slate-200
    }
};

const Dashboard = ({ data, onRefresh }) => {
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [showOutliers, setShowOutliers] = useState(false);
    const [showCorrelation, setShowCorrelation] = useState(false);
    const [showThresholds, setShowThresholds] = useState(false);
    const [thresholdSettings, setThresholdSettings] = useState(null);
    const [theme, setTheme] = useState('dark');

    // Editable threshold state
    const [editWarning, setEditWarning] = useState(0.75);
    const [editIqr, setEditIqr] = useState(1.5);
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState(null);

    // Chart refs for reset zoom functionality
    const lineChartRef = useRef(null);
    const barChartRef = useRef(null);
    const typeComparisonRef = useRef(null);

    // Detect theme changes
    useEffect(() => {
        const checkTheme = () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            setTheme(currentTheme);
        };

        checkTheme();

        // Watch for theme changes
        const observer = new MutationObserver(checkTheme);
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

        return () => observer.disconnect();
    }, []);

    // Get current color palette
    const colors = chartColors[theme] || chartColors.dark;

    // Common enhanced tooltip configuration (theme-aware)
    const enhancedTooltip = useMemo(() => ({
        enabled: true,
        backgroundColor: colors.tooltipBg,
        titleColor: colors.tooltipTitle,
        bodyColor: colors.tooltipBody,
        borderColor: colors.tooltipBorder,
        borderWidth: 1,
        padding: 12,
        cornerRadius: 4,
        titleFont: { size: 14, weight: 'bold', family: "'JetBrains Mono', monospace" },
        bodyFont: { size: 12, family: "'Inter', sans-serif" },
        displayColors: true,
        boxPadding: 4,
    }), [colors]);

    // Zoom and Pan configuration
    const zoomOptions = {
        pan: {
            enabled: true,
            mode: 'xy',
            modifierKey: 'ctrl', // Hold Ctrl to pan
        },
        zoom: {
            wheel: {
                enabled: true,
            },
            pinch: {
                enabled: true,
            },
            mode: 'xy',
            onZoomComplete: ({ chart }) => {
                chart.update('none');
            }
        },
    };

    // Reset zoom function
    const resetZoom = (chartRef) => {
        if (chartRef.current) {
            chartRef.current.resetZoom();
        }
    };

    // Fetch threshold settings on mount
    useEffect(() => {
        const fetchThresholds = async () => {
            try {
                const response = await api.get('/thresholds/');
                setThresholdSettings(response.data);
                setEditWarning(response.data.warning_percentile);
                setEditIqr(response.data.outlier_iqr_multiplier);
            } catch (error) {
                console.error('Failed to fetch threshold settings:', error);
            }
        };
        fetchThresholds();
    }, []);

    // Save threshold settings
    const saveThresholds = async () => {
        setIsSaving(true);
        setSaveMessage(null);
        try {
            const response = await api.put('/thresholds/', {
                warning_percentile: editWarning,
                outlier_iqr_multiplier: editIqr
            });
            setThresholdSettings(response.data);
            setSaveMessage({ type: 'success', text: 'Settings saved! Refresh data to see changes.' });
            if (onRefresh) {
                setTimeout(() => onRefresh(), 500);
            }
        } catch (error) {
            setSaveMessage({ type: 'error', text: formatErrorMessage(error) });
        } finally {
            setIsSaving(false);
        }
    };

    // Reset to defaults
    const resetThresholds = async () => {
        setIsSaving(true);
        setSaveMessage(null);
        try {
            const response = await api.delete('/thresholds/');
            setThresholdSettings(response.data);
            setEditWarning(response.data.warning_percentile);
            setEditIqr(response.data.outlier_iqr_multiplier);
            setSaveMessage({ type: 'success', text: 'Reset to defaults!' });
            if (onRefresh) {
                setTimeout(() => onRefresh(), 500);
            }
        } catch (error) {
            setSaveMessage({ type: 'error', text: formatErrorMessage(error) });
        } finally {
            setIsSaving(false);
        }
    };

    if (!data) return null;

    const { summary, processed_data, id, user_upload_index } = data;
    const displayId = user_upload_index || id;

    // Chart Data Preparation (theme-aware)
    const typeChartData = useMemo(() => {
        const labels = Object.keys(summary.type_distribution);
        const values = Object.values(summary.type_distribution);
        return {
            labels,
            datasets: [
                {
                    label: 'Equipment Type',
                    data: values,
                    backgroundColor: [
                        colors.primary,
                        colors.secondary,
                        colors.quaternary,
                        colors.tertiary,
                        colors.quinary,
                        colors.senary,
                    ],
                    borderColor: [
                        colors.primaryBorder,
                        colors.secondaryBorder,
                        colors.quaternaryBorder,
                        colors.tertiaryBorder,
                        colors.quinaryBorder,
                        colors.senaryBorder,
                    ],
                    borderWidth: 2,
                },
            ],
        };
    }, [summary, colors]);

    // Type Comparison Chart (theme-aware)
    const typeComparisonData = useMemo(() => {
        if (!summary.type_comparison) return null;
        const types = Object.keys(summary.type_comparison);
        return {
            labels: types,
            datasets: [
                {
                    label: 'Avg Flowrate',
                    data: types.map(t => summary.type_comparison[t].avg_flowrate),
                    backgroundColor: colors.primary,
                    borderColor: colors.primaryBorder,
                    borderWidth: 1,
                },
                {
                    label: 'Avg Pressure',
                    data: types.map(t => summary.type_comparison[t].avg_pressure),
                    backgroundColor: colors.secondary,
                    borderColor: colors.secondaryBorder,
                    borderWidth: 1,
                },
                {
                    label: 'Avg Temperature',
                    data: types.map(t => summary.type_comparison[t].avg_temperature),
                    backgroundColor: colors.tertiary,
                    borderColor: colors.tertiaryBorder,
                    borderWidth: 1,
                }
            ]
        };
    }, [summary, colors]);

    // Correlation Heatmap Data
    const correlationData = useMemo(() => {
        if (!summary.correlation_matrix) return null;
        const params = ['Flowrate', 'Pressure', 'Temperature'];
        return params.map(row =>
            params.map(col => summary.correlation_matrix[row][col])
        );
    }, [summary]);

    // Stats Bar Chart (theme-aware)
    const statsChartData = useMemo(() => {
        return {
            labels: ['Avg Flowrate', 'Avg Pressure', 'Avg Temp'],
            datasets: [
                {
                    label: 'Averages',
                    data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature],
                    backgroundColor: [colors.primary, colors.secondary, colors.tertiary],
                    borderColor: [colors.primaryBorder, colors.secondaryBorder, colors.tertiaryBorder],
                    borderWidth: 2,
                },
            ],
        };
    }, [summary, colors]);

    // Line Chart for Flowrate over items (theme-aware)
    const flowChartData = useMemo(() => {
        const subset = processed_data.slice(0, 30);
        return {
            labels: subset.map(d => d['Equipment Name']),
            datasets: [
                {
                    label: 'Flowrate',
                    data: subset.map(d => d['Flowrate']),
                    borderColor: colors.primaryBorder,
                    backgroundColor: colors.primary.replace('0.7', '0.2').replace('0.75', '0.2'),
                    tension: 0.4,
                    borderWidth: 2,
                },
                {
                    label: 'Temperature',
                    data: subset.map(d => d['Temperature']),
                    borderColor: colors.tertiaryBorder,
                    backgroundColor: colors.tertiary.replace('0.7', '0.2').replace('0.75', '0.2'),
                    tension: 0.4,
                    borderWidth: 2,
                }
            ]
        }
    }, [processed_data, colors]);

    const downloadPDFReport = async () => {
        try {
            const response = await api.get(`/report/${id}/`, {
                responseType: 'blob'
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `equipment_report_${id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert(`Failed to download report. ${error.message}`);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>Dashboard - Upload #{displayId}</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Comprehensive analysis of {summary.total_count} equipment items with advanced visualizations.</p>
                </div>
                <button
                    onClick={downloadPDFReport}
                    className="btn"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        textDecoration: 'none',
                        background: 'var(--accent-color)',
                        padding: '10px 20px',
                        borderRadius: '2px', // Square
                        border: 'none',
                        color: '#0b0c10',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold',
                        letterSpacing: '1px'
                    }}
                >
                    <FaFilePdf size={18} /> GENERATE REPORT
                </button>
            </div>

            {/* Health Overview */}
            {summary.outliers && summary.outliers.length > 0 && (
                <div className="glass-card" style={{ backgroundColor: 'rgba(220, 38, 38, 0.06)', borderColor: 'var(--danger)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <FaExclamationTriangle size={24} style={{ color: 'var(--danger)' }} />
                        <div>
                            <h3 style={{ margin: 0, color: 'var(--danger)' }}>⚠️ {summary.outliers.length} SYSTEM ANOMALIES DETECTED</h3>
                            <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                Equipment exceeding operational safety parameters.
                            </p>
                        </div>
                        <button
                            onClick={() => setShowOutliers(!showOutliers)}
                            style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '20px' }}
                        >
                            {showOutliers ? <FaChevronUp /> : <FaChevronDown />}
                        </button>
                    </div>

                    {showOutliers && (
                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
                            {summary.outliers.map((outlier, idx) => (
                                <div key={idx} style={{ marginBottom: '12px', padding: '12px', background: 'var(--card-bg)', borderRadius: '2px', border: '1px solid var(--danger)' }}>
                                    <strong style={{ color: 'var(--danger)', fontFamily: 'var(--font-family)' }}>{outlier.equipment}</strong>
                                    <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                        {outlier.parameters.map((param, pidx) => (
                                            <span key={pidx} style={{ padding: '4px 8px', background: 'var(--border-color)', borderRadius: '4px', fontSize: '0.9rem' }}>
                                                {param.parameter}: <strong>{param.value.toFixed(2)}</strong>
                                                <span style={{ color: 'var(--text-muted)' }}> (expected: {param.lower_bound.toFixed(2)} - {param.upper_bound.toFixed(2)})</span>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}



            {/* Basic Stats with Min/Max */}
            <div className="stats-grid">
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.total_count}</div>
                    <div className="stat-label">Total Equipment</div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_flowrate.toFixed(1)}</div>
                    <div className="stat-label">Avg Flowrate</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Min: {summary.min_flowrate.toFixed(1)} | Max: {summary.max_flowrate.toFixed(1)}
                    </div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_pressure.toFixed(1)}</div>
                    <div className="stat-label">Avg Pressure</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Min: {summary.min_pressure.toFixed(1)} | Max: {summary.max_pressure.toFixed(1)}
                    </div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_temperature.toFixed(1)}</div>
                    <div className="stat-label">Avg Temperature</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Min: {summary.min_temperature.toFixed(1)} | Max: {summary.max_temperature.toFixed(1)}
                    </div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div className="glass-card">
                    <h3>Equipment Types</h3>
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
                        <Doughnut data={typeChartData} options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'right',
                                    labels: { color: colors.legendText }
                                }
                            }
                        }} />
                    </div>
                </div>
                <div className="glass-card">
                    <h3>Parameter Averages</h3>
                    <div style={{ height: '300px' }}>
                        <Bar data={statsChartData} options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { ticks: { color: colors.text }, grid: { color: colors.grid } },
                                x: { ticks: { color: colors.text }, grid: { display: false } }
                            },
                            plugins: { legend: { display: false } }
                        }} />
                    </div>
                </div>
            </div>

            {/* Advanced Analytics Section (Expandable) */}
            <div className="glass-card">
                <div
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                    onClick={() => setShowAdvanced(!showAdvanced)}
                >
                    <h3 style={{ margin: 0 }}>🔬 Advanced Analytics</h3>
                    <button style={{ background: 'none', border: 'none', color: 'var(--accent-color)', cursor: 'pointer', fontSize: '20px' }}>
                        {showAdvanced ? <FaChevronUp /> : <FaChevronDown />}
                    </button>
                </div>

                {showAdvanced && (
                    <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <div>
                            <h4 style={{ marginBottom: '16px' }}>Equipment Type Comparison</h4>
                            <div style={{ height: '300px' }}>
                                <Bar
                                    data={typeComparisonData}
                                    options={{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        scales: {
                                            y: { ticks: { color: colors.text }, grid: { color: colors.grid } },
                                            x: { ticks: { color: colors.text }, grid: { display: false } }
                                        },
                                        plugins: {
                                            legend: {
                                                labels: { color: colors.legendText },
                                                position: 'top'
                                            },
                                            tooltip: {
                                                ...enhancedTooltip,
                                                callbacks: {
                                                    afterLabel: function (context) {
                                                        const type = context.label;
                                                        const count = summary.type_comparison[type].count;
                                                        return `Count: ${count}`;
                                                    }
                                                }
                                            }
                                        }
                                    }}
                                />
                            </div>
                        </div>

                        {/* Correlation Heatmap */}
                        <div>
                            <div
                                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', marginBottom: '16px' }}
                                onClick={() => setShowCorrelation(!showCorrelation)}
                            >
                                <h4 style={{ margin: 0 }}>Parameter Correlation Matrix</h4>
                                <button style={{ background: 'none', border: 'none', color: 'var(--accent-color)', cursor: 'pointer' }}>
                                    {showCorrelation ? 'Hide' : 'Show'}
                                </button>
                            </div>

                            {showCorrelation && (
                                <div style={{ display: 'flex', justifyContent: 'center' }}>
                                    <table style={{ borderCollapse: 'collapse', textAlign: 'center' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ padding: '8px', border: '1px solid var(--border-color)' }}></th>
                                                <th style={{ padding: '8px', border: '1px solid var(--border-color)' }}>Flowrate</th>
                                                <th style={{ padding: '8px', border: '1px solid var(--border-color)' }}>Pressure</th>
                                                <th style={{ padding: '8px', border: '1px solid var(--border-color)' }}>Temperature</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {['Flowrate', 'Pressure', 'Temperature'].map((row, i) => (
                                                <tr key={row}>
                                                    <td style={{ padding: '8px', border: '1px solid var(--border-color)', fontWeight: 'bold' }}>{row}</td>
                                                    {['Flowrate', 'Pressure', 'Temperature'].map((col, j) => {
                                                        const value = correlationData[i][j];
                                                        const intensity = Math.abs(value);
                                                        const color = value > 0
                                                            ? `rgba(8, 145, 178, ${intensity})`
                                                            : `rgba(220, 38, 38, ${intensity})`;
                                                        return (
                                                            <td
                                                                key={col}
                                                                style={{
                                                                    padding: '16px',
                                                                    border: '1px solid var(--border-color)',
                                                                    backgroundColor: color,
                                                                    fontWeight: 'bold'
                                                                }}
                                                            >
                                                                {value.toFixed(2)}
                                                            </td>
                                                        );
                                                    })}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                        {/* Statistical Summary */}
                        <div>
                            <h4 style={{ marginBottom: '12px' }}>Statistical Summary</h4>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                                <div style={{ padding: '12px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Flowrate Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px', color: colors.primaryBorder }}>
                                        {summary.std_flowrate.toFixed(2)}
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Pressure Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px', color: colors.secondaryBorder }}>
                                        {summary.std_pressure.toFixed(2)}
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Temperature Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px', color: colors.tertiaryBorder }}>
                                        {summary.std_temperature.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="glass-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0 }}>Flowrate & Temperature Trends</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <FaSearchPlus style={{ marginRight: '4px' }} />
                            Scroll to zoom • Ctrl+drag to pan
                        </span>
                        <button
                            onClick={() => resetZoom(lineChartRef)}
                            style={{
                                background: 'transparent',
                                border: '1px solid var(--accent-color)',
                                color: 'var(--accent-color)',
                                padding: '4px 8px',
                                borderRadius: '2px',
                                cursor: 'pointer',
                                fontSize: '0.75rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            }}
                        >
                            <FaUndo size={10} /> Reset
                        </button>
                    </div>
                </div>
                <div style={{ height: '300px' }}>
                    <Line
                        ref={lineChartRef}
                        data={flowChartData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            interaction: {
                                mode: 'index',
                                intersect: false,
                            },
                            scales: {
                                y: {
                                    ticks: { color: colors.text },
                                    grid: { color: colors.grid }
                                },
                                x: {
                                    ticks: { color: colors.text, maxRotation: 45 },
                                    grid: { display: false }
                                }
                            },
                            plugins: {
                                legend: { labels: { color: colors.legendText } },
                                tooltip: {
                                    ...enhancedTooltip,
                                    callbacks: {
                                        title: (items) => `Equipment: ${items[0].label}`,
                                        afterBody: (items) => {
                                            const index = items[0].dataIndex;
                                            const equipment = processed_data[index];
                                            if (equipment) {
                                                return [
                                                    '',
                                                    `Type: ${equipment['Type']}`,
                                                    `Pressure: ${equipment['Pressure']?.toFixed(2)}`,
                                                    `Health: ${equipment['health_status']?.toUpperCase() || 'N/A'}`
                                                ];
                                            }
                                            return [];
                                        }
                                    }
                                },
                                zoom: zoomOptions
                            }
                        }}
                    />
                </div>
            </div>

            <div className="glass-card">
                <h3>Equipment Data with Health Status</h3>
                <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Equipment Name</th>
                                <th>Type</th>
                                <th>Flowrate</th>
                                <th>Pressure</th>
                                <th>Temperature</th>
                            </tr>
                        </thead>
                        <tbody>
                            {processed_data.slice(0, 50).map((row, idx) => (
                                <tr key={idx} style={{ backgroundColor: row.health_status === 'critical' ? 'rgba(239, 68, 68, 0.1)' : row.health_status === 'warning' ? 'rgba(245, 158, 11, 0.1)' : 'transparent' }}>
                                    <td>
                                        {row.health_status === 'critical' && <FaTimesCircle color="#ef4444" title="Critical" />}
                                        {row.health_status === 'warning' && <FaExclamationTriangle color="#f59e0b" title="Warning" />}
                                        {row.health_status === 'normal' && <FaCheckCircle color="#10b981" title="Normal" />}
                                    </td>
                                    <td>{row['Equipment Name']}</td>
                                    <td>{row['Type']}</td>
                                    <td>{row['Flowrate']}</td>
                                    <td>{row['Pressure']}</td>
                                    <td>{row['Temperature']}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Threshold Configuration Display (Collapsible, at bottom) */}
            {thresholdSettings && (
                <div className="glass-card" style={{ backgroundColor: 'var(--glass-border)', borderColor: 'var(--accent-color)' }}>
                    <div
                        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                        onClick={() => setShowThresholds(!showThresholds)}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <FaCog size={24} style={{ color: 'var(--accent-color)' }} />
                            <div>
                                <h3 style={{ margin: 0, color: 'var(--accent-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    ⚙️ THRESHOLD SETTINGS
                                    {thresholdSettings.is_custom && (
                                        <span style={{
                                            fontSize: '0.7rem',
                                            background: 'var(--accent-color)',
                                            color: 'var(--bg-color)',
                                            padding: '2px 8px',
                                            borderRadius: '12px',
                                            fontWeight: 'normal'
                                        }}>CUSTOM</span>
                                    )}
                                </h3>
                                <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                    Configure warning &amp; critical thresholds (Click to expand)
                                </p>
                            </div>
                        </div>
                        <button style={{ background: 'none', border: 'none', color: 'var(--accent-color)', cursor: 'pointer', fontSize: '20px' }}>
                            {showThresholds ? <FaChevronUp /> : <FaChevronDown />}
                        </button>
                    </div>

                    {showThresholds && (
                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                {/* Warning Percentile Control */}
                                <div style={{ padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                        <strong style={{ color: colors.quinaryBorder }}>Warning Level</strong>
                                        <span style={{
                                            fontSize: '1.3rem',
                                            fontWeight: 'bold',
                                            color: colors.quinaryBorder
                                        }}>
                                            {(editWarning * 100).toFixed(0)}th %ile
                                        </span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0.50"
                                        max="0.95"
                                        step="0.01"
                                        value={editWarning}
                                        onChange={(e) => setEditWarning(parseFloat(e.target.value))}
                                        style={{
                                            width: '100%',
                                            height: '8px',
                                            cursor: 'pointer',
                                            accentColor: colors.quinaryBorder
                                        }}
                                    />
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                        <span>50%</span>
                                        <span>95%</span>
                                    </div>
                                    <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        Equipment with parameters above this percentile are flagged as ⚠️ warnings
                                    </div>
                                </div>

                                {/* IQR Multiplier Control */}
                                <div style={{ padding: '16px', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                        <strong style={{ color: colors.tertiaryBorder }}>Critical Level</strong>
                                        <span style={{
                                            fontSize: '1.3rem',
                                            fontWeight: 'bold',
                                            color: colors.tertiaryBorder
                                        }}>
                                            {editIqr.toFixed(1)} × IQR
                                        </span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0.5"
                                        max="3.0"
                                        step="0.1"
                                        value={editIqr}
                                        onChange={(e) => setEditIqr(parseFloat(e.target.value))}
                                        style={{
                                            width: '100%',
                                            height: '8px',
                                            cursor: 'pointer',
                                            accentColor: colors.tertiaryBorder
                                        }}
                                    />
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                        <span>0.5×</span>
                                        <span>3.0×</span>
                                    </div>
                                    <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        Values beyond Q3 + this multiplier × IQR are marked as 🔴 critical/outliers
                                    </div>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div style={{ marginTop: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                                <button
                                    onClick={saveThresholds}
                                    disabled={isSaving}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '10px 20px',
                                        background: 'var(--accent-color)',
                                        color: 'var(--bg-color)',
                                        border: 'none',
                                        borderRadius: '6px',
                                        cursor: isSaving ? 'wait' : 'pointer',
                                        fontWeight: 'bold',
                                        opacity: isSaving ? 0.7 : 1
                                    }}
                                >
                                    <FaSave /> {isSaving ? 'Saving...' : 'Save Settings'}
                                </button>
                                <button
                                    onClick={resetThresholds}
                                    disabled={isSaving || !thresholdSettings.is_custom}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '10px 20px',
                                        background: 'transparent',
                                        color: 'var(--text-secondary)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: '6px',
                                        cursor: (isSaving || !thresholdSettings.is_custom) ? 'not-allowed' : 'pointer',
                                        opacity: (isSaving || !thresholdSettings.is_custom) ? 0.5 : 1
                                    }}
                                >
                                    <FaSync /> Reset to Defaults
                                </button>

                                {/* Status Message */}
                                {saveMessage && (
                                    <span style={{
                                        marginLeft: '8px',
                                        color: saveMessage.type === 'success' ? 'var(--success)' : 'var(--danger)',
                                        fontSize: '0.9rem'
                                    }}>
                                        {saveMessage.type === 'success' ? '✓' : '✗'} {saveMessage.text}
                                    </span>
                                )}
                            </div>

                            <div style={{ marginTop: '12px', padding: '8px', background: 'var(--card-bg)', borderRadius: '4px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                💡 <strong>Note:</strong> Changes apply to all your uploads. Existing data will be recalculated with new thresholds when viewed.
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
