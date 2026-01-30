import React, { useEffect, useState } from 'react';
import api from '../api';
import { FaFileCsv, FaHistory } from 'react-icons/fa';
import { HistorySkeleton } from './Skeleton';

const HistorySidebar = ({ onSelectHistory, refreshTrigger }) => {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchHistory = async () => {
        setIsLoading(true);
        try {
            const res = await api.get('history/');
            setHistory(res.data);
        } catch (err) {
            console.error("Failed to fetch history");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, [refreshTrigger]);

    return (
        <div className="glass-card sidebar">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                <FaHistory />
                <h2>History</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {isLoading ? (
                    <HistorySkeleton />
                ) : history.length === 0 ? (
                    <p style={{ opacity: 0.5 }}>No recent uploads.</p>
                ) : (
                    history.map((item) => (
                        <div
                            key={item.id}
                            className="history-item"
                            style={{
                                padding: '12px',
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                border: '1px solid transparent',
                                transition: 'all 0.2s'
                            }}
                            onClick={() => onSelectHistory(item)}
                            onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent-color)'}
                            onMouseLeave={(e) => e.currentTarget.style.borderColor = 'transparent'}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                <FaFileCsv color="var(--accent-color)" />
                                <span style={{ fontWeight: 500 }}>Upload #{item.user_upload_index || item.id}</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                {new Date(item.uploaded_at).toLocaleString()}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default HistorySidebar;

