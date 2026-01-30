import React, { useState, useEffect } from 'react';
import HistorySidebar from './components/HistorySidebar';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import api from './api';
import { FaSignOutAlt, FaUser } from 'react-icons/fa';

function App() {
  const [currentData, setCurrentData] = useState(null);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUsername = localStorage.getItem('username');
    if (token) {
      // We could verify token validity here, but for now just assume true
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      if (storedUsername) setUsername(storedUsername);
    }
  }, []);

  const handleLoginSuccess = (user) => {
    // Login component already set localStorage
    const token = localStorage.getItem('access_token');
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setIsAuthenticated(true);
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) setUsername(storedUsername);
  };

  const handleLogout = () => {
    // Clear all auth data
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    delete api.defaults.headers.common['Authorization'];

    // Reset state
    setIsAuthenticated(false);
    setCurrentData(null);
    setUsername('');
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLoginSuccess} />;
  }

  const handleUploadSuccess = (data) => {
    setCurrentData(data);
    setRefreshHistory(prev => prev + 1);
  };

  const handleHistorySelect = (data) => {
    setCurrentData(data);
  };

  return (
    <div className="app-container">
      <HistorySidebar
        onSelectHistory={handleHistorySelect}
        refreshTrigger={refreshHistory}
      />

      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Equipment Visualizer</h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
              Upload CSV data to analyze chemical equipment parameters.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {username && (
              <span style={{
                color: 'var(--text-secondary)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.9rem'
              }}>
                <FaUser size={14} /> {username}
              </span>
            )}
            <button
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'transparent',
                border: '1px solid var(--danger)',
                color: 'var(--danger)',
                padding: '8px 16px',
                borderRadius: '2px',
                cursor: 'pointer',
                fontFamily: 'var(--font-family)',
                fontWeight: 'bold',
                fontSize: '0.85rem',
                letterSpacing: '1px',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--danger)';
                e.target.style.color = '#0b0c10';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'transparent';
                e.target.style.color = 'var(--danger)';
              }}
            >
              <FaSignOutAlt /> LOGOUT
            </button>
          </div>
        </header>

        <FileUpload onUploadSuccess={handleUploadSuccess} />

        {currentData && (
          <Dashboard data={currentData} />
        )}

        {!currentData && (
          <div style={{ marginTop: '40px', textAlign: 'center', opacity: 0.5 }}>
            <h3>No data selected. Upload a file or select from history.</h3>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
