import React, { useMemo } from 'react';
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
import { FaFilePdf } from 'react-icons/fa';

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

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>Dashboard - Upload #{id}</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Analysis of {summary.total_count} equipment items.</p>
                </div>
                <a href={`http://127.0.0.1:8000/api/report/${id}/`} target="_blank" rel="noreferrer" className="btn" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
                    <FaFilePdf /> Download PDF Report
                </a>
            </div>

            <div className="stats-grid">
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.total_count}</div>
                    <div className="stat-label">Total Equipment</div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_flowrate.toFixed(1)}</div>
                    <div className="stat-label">Avg Flowrate</div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_pressure.toFixed(1)}</div>
                    <div className="stat-label">Avg Pressure</div>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div className="stat-value">{summary.avg_temperature.toFixed(1)}</div>
                    <div className="stat-label">Avg Temperature</div>
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

            <div className="glass-card">
                <h3>Flowrate & Temperature Trends</h3>
                <div style={{ height: '300px' }}>
                    <Line data={flowChartData} options={{ responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }, x: { ticks: { color: '#8b949e' }, grid: { display: false } } }, plugins: { legend: { labels: { color: '#e6edf3' } } } }} />
                </div>
            </div>

            <div className="glass-card">
                <h3>Raw Data (Top 50)</h3>
                <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Equipment Name</th>
                                <th>Type</th>
                                <th>Flowrate</th>
                                <th>Pressure</th>
                                <th>Temperature</th>
                            </tr>
                        </thead>
                        <tbody>
                            {processed_data.slice(0, 50).map((row, idx) => (
                                <tr key={idx}>
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
