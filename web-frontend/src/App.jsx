import React, { useState, useEffect } from 'react';
import HistorySidebar from './components/HistorySidebar';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import api from './api';

function App() {
  const [currentData, setCurrentData] = useState(null);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // We could verify token validity here, but for now just assume true
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    // Login component already set localStorage
    const token = localStorage.getItem('access_token');
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setIsAuthenticated(true);
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
        <header>
          <h1>Equipment Visualizer</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            Upload CSV data to analyze chemical equipment parameters.
          </p>
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
