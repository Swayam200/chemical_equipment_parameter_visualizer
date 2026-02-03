import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Layout from './components/Layout';
import MainPage from './pages/MainPage';
import AdvancedAnalyticsPage from './pages/AdvancedAnalyticsPage';
import HistoryPage from './pages/HistoryPage';
import api from './api';

function App() {
  const [currentData, setCurrentData] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || 'dark';
  });




  // Apply theme to document
  useEffect(() => {
    // Tailwind uses 'dark' class on html element
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Auth check
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUsername = localStorage.getItem('username');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      if (storedUsername) setUsername(storedUsername);
    }
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleLoginSuccess = () => {
    const token = localStorage.getItem('access_token');
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setIsAuthenticated(true);
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) setUsername(storedUsername);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    delete api.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setCurrentData(null);
    setUsername('');
  };

  const handleUploadSuccess = (data) => {
    setCurrentData(data);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLoginSuccess} theme={theme} toggleTheme={toggleTheme} />;
  }

  return (
    <Router>
      <Layout
        user={username}
        onLogout={handleLogout}
        toggleTheme={toggleTheme}
        theme={theme}
        data={currentData}
      >
        <Routes>
          <Route path="/" element={<MainPage data={currentData} onUploadSuccess={handleUploadSuccess} theme={theme} />} />
          <Route path="/analytics" element={<AdvancedAnalyticsPage data={currentData} theme={theme} />} />
          {/* Reuse MainPage or create specific History page. */}
          <Route path="/history" element={<HistoryPage onSelectHistory={handleUploadSuccess} />} />
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
