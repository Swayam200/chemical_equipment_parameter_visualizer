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
import { FaFilePdf, FaChevronDown, FaChevronUp, FaExclamationTriangle, FaCheckCircle, FaTimesCircle, FaCog, FaSearchPlus, FaUndo } from 'react-icons/fa';

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

const Dashboard = ({ data }) => {
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [showOutliers, setShowOutliers] = useState(false);
    const [showCorrelation, setShowCorrelation] = useState(false);
    const [showThresholds, setShowThresholds] = useState(false);
    const [thresholdSettings, setThresholdSettings] = useState(null);

    // Chart refs for reset zoom functionality
    const lineChartRef = useRef(null);
    const barChartRef = useRef(null);
    const typeComparisonRef = useRef(null);

    // Common enhanced tooltip configuration
    const enhancedTooltip = {
        enabled: true,
        backgroundColor: 'rgba(11, 12, 16, 0.95)',
        titleColor: '#66fcf1',
        bodyColor: '#c5c6c7',
        borderColor: '#45a29e',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 4,
        titleFont: { size: 14, weight: 'bold', family: "'JetBrains Mono', monospace" },
        bodyFont: { size: 12, family: "'Inter', sans-serif" },
        displayColors: true,
        boxPadding: 4,
    };

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
            } catch (error) {
                console.error('Failed to fetch threshold settings:', error);
            }
        };
        fetchThresholds();
    }, []);

    if (!data) return null;

    const { summary, processed_data, id, user_upload_index } = data;
    const displayId = user_upload_index || id;

    // Chart Data Preparation
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
                        'rgba(102, 252, 241, 0.6)', // Cyan
                        'rgba(69, 162, 158, 0.6)',  // Teal
                        'rgba(32, 252, 143, 0.6)',  // Neon Green
                        'rgba(252, 32, 68, 0.6)',   // Neon Red
                        'rgba(224, 168, 0, 0.6)',   // Amber
                    ],
                    borderColor: [
                        '#66fcf1',
                        '#45a29e',
                        '#20fc8f',
                        '#fc2044',
                        '#e0a800',
                    ],
                    borderWidth: 1,
                },
            ],
        };
    }, [summary]);

    // Type Comparison Chart (NEW)
    const typeComparisonData = useMemo(() => {
        if (!summary.type_comparison) return null;
        const types = Object.keys(summary.type_comparison);
        return {
            labels: types,
            datasets: [
                {
                    label: 'Avg Flowrate',
                    data: types.map(t => summary.type_comparison[t].avg_flowrate),
                    backgroundColor: 'rgba(102, 252, 241, 0.6)',
                    borderColor: '#66fcf1',
                    borderWidth: 1,
                },
                {
                    label: 'Avg Pressure',
                    data: types.map(t => summary.type_comparison[t].avg_pressure),
                    backgroundColor: 'rgba(69, 162, 158, 0.6)',
                    borderColor: '#45a29e',
                    borderWidth: 1,
                },
                {
                    label: 'Avg Temperature',
                    data: types.map(t => summary.type_comparison[t].avg_temperature),
                    backgroundColor: 'rgba(252, 32, 68, 0.6)',
                    borderColor: '#fc2044',
                    borderWidth: 1,
                }
            ]
        };
    }, [summary]);

    // Correlation Heatmap Data (NEW)
    const correlationData = useMemo(() => {
        if (!summary.correlation_matrix) return null;
        const params = ['Flowrate', 'Pressure', 'Temperature'];
        return params.map(row =>
            params.map(col => summary.correlation_matrix[row][col])
        );
    }, [summary]);

    const statsChartData = useMemo(() => {
        return {
            labels: ['Avg Flowrate', 'Avg Pressure', 'Avg Temp'],
            datasets: [
                {
                    label: 'Averages',
                    data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature],
                    backgroundColor: 'rgba(102, 252, 241, 0.5)',
                    borderColor: '#66fcf1',
                    borderWidth: 1,
                },
            ],
        };
    }, [summary]);

    // Line Chart for Flowrate over items 
    const flowChartData = useMemo(() => {
        // Just taking first 20 items to avoid overcrowding if large
        const subset = processed_data.slice(0, 30);
        return {
            labels: subset.map(d => d['Equipment Name']),
            datasets: [
                {
                    label: 'Flowrate',
                    data: subset.map(d => d['Flowrate']),
                    borderColor: '#66fcf1',
                    backgroundColor: 'rgba(102, 252, 241, 0.2)',
                    tension: 0.4
                },
                {
                    label: 'Temperature',
                    data: subset.map(d => d['Temperature']),
                    borderColor: '#fc2044',
                    backgroundColor: 'rgba(252, 32, 68, 0.2)',
                    tension: 0.4
                }
            ]
        }
    }, [processed_data]);

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
                <div className="glass-card" style={{ backgroundColor: 'rgba(252, 32, 68, 0.05)', borderColor: '#fc2044' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <FaExclamationTriangle size={24} color="#fc2044" />
                        <div>
                            <h3 style={{ margin: 0, color: '#fc2044' }}>⚠️ {summary.outliers.length} SYSTEM ANOMALIES DETECTED</h3>
                            <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                Equipment exceeding operational safety parameters.
                            </p>
                        </div>
                        <button
                            onClick={() => setShowOutliers(!showOutliers)}
                            style={{ marginLeft: 'auto', background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '20px' }}
                        >
                            {showOutliers ? <FaChevronUp /> : <FaChevronDown />}
                        </button>
                    </div>

                    {showOutliers && (
                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #30363d' }}>
                            {summary.outliers.map((outlier, idx) => (
                                <div key={idx} style={{ marginBottom: '12px', padding: '12px', background: '#0b0c10', borderRadius: '2px', border: '1px solid #fc2044' }}>
                                    <strong style={{ color: '#fc2044', fontFamily: 'var(--font-family)' }}>{outlier.equipment}</strong>
                                    <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                        {outlier.parameters.map((param, pidx) => (
                                            <span key={pidx} style={{ padding: '4px 8px', background: '#30363d', borderRadius: '4px', fontSize: '0.9rem' }}>
                                                {param.parameter}: <strong>{param.value.toFixed(2)}</strong>
                                                <span style={{ color: '#8b949e' }}> (expected: {param.lower_bound.toFixed(2)} - {param.upper_bound.toFixed(2)})</span>
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
                    <div style={{ fontSize: '0.8rem', color: '#8b949e', marginTop: '4px' }}>
                        Min: {summary.min_flowrate.toFixed(1)} | Max: {summary.max_flowrate.toFixed(1)}
                    </div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_pressure.toFixed(1)}</div>
                    <div className="stat-label">Avg Pressure</div>
                    <div style={{ fontSize: '0.8rem', color: '#8b949e', marginTop: '4px' }}>
                        Min: {summary.min_pressure.toFixed(1)} | Max: {summary.max_pressure.toFixed(1)}
                    </div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_temperature.toFixed(1)}</div>
                    <div className="stat-label">Avg Temperature</div>
                    <div style={{ fontSize: '0.8rem', color: '#8b949e', marginTop: '4px' }}>
                        Min: {summary.min_temperature.toFixed(1)} | Max: {summary.max_temperature.toFixed(1)}
                    </div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div className="glass-card">
                    <h3>Equipment Types</h3>
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
                        <Doughnut data={typeChartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#e6edf3' } } } }} />
                    </div>
                </div>
                <div className="glass-card">
                    <h3>Parameter Averages</h3>
                    <div style={{ height: '300px' }}>
                        <Bar data={statsChartData} options={{ responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }, x: { ticks: { color: '#8b949e' }, grid: { display: false } } }, plugins: { legend: { display: false } } }} />
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
                    <button style={{ background: 'none', border: 'none', color: '#58a6ff', cursor: 'pointer', fontSize: '20px' }}>
                        {showAdvanced ? <FaChevronUp /> : <FaChevronDown />}
                    </button>
                </div>

                {showAdvanced && (
                    <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        {/* Type Comparison Chart */}
                        <div>
                            <h4 style={{ marginBottom: '16px' }}>Equipment Type Comparison</h4>
                            <div style={{ height: '300px' }}>
                                <Bar
                                    data={typeComparisonData}
                                    options={{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        scales: {
                                            y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
                                            x: { ticks: { color: '#8b949e' }, grid: { display: false } }
                                        },
                                        plugins: {
                                            legend: {
                                                labels: { color: '#e6edf3' },
                                                position: 'top'
                                            },
                                            tooltip: {
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
                                <button style={{ background: 'none', border: 'none', color: '#58a6ff', cursor: 'pointer' }}>
                                    {showCorrelation ? 'Hide' : 'Show'}
                                </button>
                            </div>

                            {showCorrelation && (
                                <div style={{ display: 'flex', justifyContent: 'center' }}>
                                    <table style={{ borderCollapse: 'collapse', textAlign: 'center' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ padding: '8px', border: '1px solid #30363d' }}></th>
                                                <th style={{ padding: '8px', border: '1px solid #30363d' }}>Flowrate</th>
                                                <th style={{ padding: '8px', border: '1px solid #30363d' }}>Pressure</th>
                                                <th style={{ padding: '8px', border: '1px solid #30363d' }}>Temperature</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {['Flowrate', 'Pressure', 'Temperature'].map((row, i) => (
                                                <tr key={row}>
                                                    <td style={{ padding: '8px', border: '1px solid #30363d', fontWeight: 'bold' }}>{row}</td>
                                                    {['Flowrate', 'Pressure', 'Temperature'].map((col, j) => {
                                                        const value = correlationData[i][j];
                                                        const intensity = Math.abs(value);
                                                        const color = value > 0
                                                            ? `rgba(88, 166, 255, ${intensity})`
                                                            : `rgba(248, 81, 73, ${intensity})`;
                                                        return (
                                                            <td
                                                                key={col}
                                                                style={{
                                                                    padding: '16px',
                                                                    border: '1px solid #30363d',
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
                                <div style={{ padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <div style={{ color: '#8b949e', fontSize: '0.9rem' }}>Flowrate Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px' }}>
                                        {summary.std_flowrate.toFixed(2)}
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <div style={{ color: '#8b949e', fontSize: '0.9rem' }}>Pressure Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px' }}>
                                        {summary.std_pressure.toFixed(2)}
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <div style={{ color: '#8b949e', fontSize: '0.9rem' }}>Temperature Std Dev</div>
                                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold', marginTop: '4px' }}>
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
                                    ticks: { color: '#8b949e' },
                                    grid: { color: '#30363d' }
                                },
                                x: {
                                    ticks: { color: '#8b949e', maxRotation: 45 },
                                    grid: { display: false }
                                }
                            },
                            plugins: {
                                legend: { labels: { color: '#e6edf3' } },
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
                <div className="glass-card" style={{ backgroundColor: 'rgba(69, 162, 158, 0.05)', borderColor: '#45a29e' }}>
                    <div
                        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                        onClick={() => setShowThresholds(!showThresholds)}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <FaCog size={24} color="#45a29e" />
                            <div>
                                <h3 style={{ margin: 0, color: '#45a29e' }}>⚙️ SYSTEM THRESHOLDS</h3>
                                <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                    Active analysis configuration (Click to expand)
                                </p>
                            </div>
                        </div>
                        <button style={{ background: 'none', border: 'none', color: '#45a29e', cursor: 'pointer', fontSize: '20px' }}>
                            {showThresholds ? <FaChevronUp /> : <FaChevronDown />}
                        </button>
                    </div>

                    {showThresholds && (
                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #30363d' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                <div style={{ padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <strong style={{ color: '#f59e0b', fontSize: '1.2rem' }}>
                                        {(thresholdSettings.warning_percentile * 100).toFixed(0)}th Percentile
                                    </strong>
                                    <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                        <strong>Warning Level:</strong> Equipment with parameters above this percentile are flagged as warnings
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <strong style={{ color: '#ef4444', fontSize: '1.2rem' }}>
                                        Q3 + {thresholdSettings.outlier_iqr_multiplier} × IQR
                                    </strong>
                                    <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                        <strong>Critical/Outlier Level:</strong> Values beyond this threshold are marked as outliers
                                    </div>
                                </div>
                            </div>
                            <div style={{ marginTop: '12px', padding: '8px', background: '#161b22', borderRadius: '4px', fontSize: '0.85rem', color: '#8b949e' }}>
                                💡 <strong>Tip:</strong> To adjust these thresholds, modify <code>WARNING_PERCENTILE</code> and <code>OUTLIER_IQR_MULTIPLIER</code> in your backend <code>.env</code> file, then restart the Django server.
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
