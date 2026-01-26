import React, { useMemo, useState, useEffect } from 'react';
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
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { FaFilePdf, FaChevronDown, FaChevronUp, FaExclamationTriangle, FaCheckCircle, FaTimesCircle, FaCog } from 'react-icons/fa';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement
);

const Dashboard = ({ data }) => {
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [showOutliers, setShowOutliers] = useState(false);
    const [showCorrelation, setShowCorrelation] = useState(false);
    const [thresholdSettings, setThresholdSettings] = useState(null);
    
    // Fetch threshold settings on mount
    useEffect(() => {
        const fetchThresholds = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('http://127.0.0.1:8000/api/thresholds/', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.ok) {
                    const thresholds = await response.json();
                    setThresholdSettings(thresholds);
                }
            } catch (error) {
                console.error('Failed to fetch threshold settings:', error);
            }
        };
        fetchThresholds();
    }, []);
    
    if (!data) return null;

    const { summary, processed_data, id } = data;

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
                        'rgba(88, 166, 255, 0.6)',
                        'rgba(238, 130, 238, 0.6)',
                        'rgba(46, 160, 67, 0.6)',
                        'rgba(248, 81, 73, 0.6)',
                        'rgba(219, 109, 40, 0.6)',
                    ],
                    borderColor: [
                        'rgba(88, 166, 255, 1)',
                        'rgba(238, 130, 238, 1)',
                        'rgba(46, 160, 67, 1)',
                        'rgba(248, 81, 73, 1)',
                        'rgba(219, 109, 40, 1)',
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
                    backgroundColor: 'rgba(88, 166, 255, 0.6)',
                    borderColor: '#58a6ff',
                    borderWidth: 1,
                },
                {
                    label: 'Avg Pressure',
                    data: types.map(t => summary.type_comparison[t].avg_pressure),
                    backgroundColor: 'rgba(238, 130, 238, 0.6)',
                    borderColor: '#ee82ee',
                    borderWidth: 1,
                },
                {
                    label: 'Avg Temperature',
                    data: types.map(t => summary.type_comparison[t].avg_temperature),
                    backgroundColor: 'rgba(248, 81, 73, 0.6)',
                    borderColor: '#f85149',
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
                    backgroundColor: 'rgba(88, 166, 255, 0.5)',
                    borderColor: '#58a6ff',
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
                    borderColor: '#58a6ff',
                    backgroundColor: 'rgba(88, 166, 255, 0.2)',
                    tension: 0.4
                },
                {
                    label: 'Temperature',
                    data: subset.map(d => d['Temperature']),
                    borderColor: '#f85149',
                    backgroundColor: 'rgba(248, 81, 73, 0.2)',
                    tension: 0.4
                }
            ]
        }
    }, [processed_data]);

    const downloadPDFReport = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                alert('Authentication token not found. Please login again.');
                return;
            }
            
            const response = await fetch(`http://127.0.0.1:8000/api/report/${id}/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `equipment_report_${id}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const errorText = await response.text();
                console.error('Download failed:', response.status, errorText);
                alert(`Failed to download report. Status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert('Error downloading report. Please check your connection.');
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>Dashboard - Upload #{id}</h2>
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
                        background: 'linear-gradient(135deg, #58a6ff 0%, #4a8ed9 100%)',
                        padding: '10px 20px',
                        borderRadius: '8px',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                    }}
                >
                    <FaFilePdf size={18} /> Download Comprehensive PDF Report
                </button>
            </div>

            {/* Health Overview */}
            {summary.outliers && summary.outliers.length > 0 && (
                <div className="glass-card" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: '#ef4444' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <FaExclamationTriangle size={24} color="#ef4444" />
                        <div>
                            <h3 style={{ margin: 0, color: '#ef4444' }}>⚠️ {summary.outliers.length} Equipment Outliers Detected</h3>
                            <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                Equipment with unusual parameter readings. Click to view details.
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
                                <div key={idx} style={{ marginBottom: '12px', padding: '12px', background: '#0d1117', borderRadius: '6px' }}>
                                    <strong style={{ color: '#ef4444' }}>{outlier.equipment}</strong>
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

            {/* Threshold Configuration Display */}
            {thresholdSettings && (
                <div className="glass-card" style={{ backgroundColor: 'rgba(88, 166, 255, 0.1)', borderColor: '#58a6ff' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <FaCog size={24} color="#58a6ff" />
                        <div>
                            <h3 style={{ margin: 0, color: '#58a6ff' }}>⚙️ Current Threshold Configuration</h3>
                            <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)' }}>
                                Analysis thresholds configured in backend .env file
                            </p>
                        </div>
                    </div>
                    
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
                                                    afterLabel: function(context) {
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
                <h3>Flowrate & Temperature Trends</h3>
                <div style={{ height: '300px' }}>
                    <Line data={flowChartData} options={{ responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }, x: { ticks: { color: '#8b949e' }, grid: { display: false } } }, plugins: { legend: { labels: { color: '#e6edf3' } } } }} />
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
        </div>
    );
};

export default Dashboard;
