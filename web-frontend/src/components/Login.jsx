import React, { useState } from 'react';
import { FaLock, FaUserPlus } from 'react-icons/fa';
import api from '../api';

const Login = ({ onLogin }) => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    if (!username || !password) {
      setError("Please enter both username and password");
      return;
    }

    try {
      const response = await api.post('login/', { username, password });

      // Store JWT token
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      // Notify parent
      onLogin();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Login failed");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    if (!username || !email || !password || !confirmPassword) {
      setError("All fields are required");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    try {
      const response = await api.post('register/', { username, email, password });

      // Store JWT token
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      setSuccess("Registration successful! Logging you in...");
      
      // Auto-login after 1 second
      setTimeout(() => {
        onLogin();
      }, 1000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Registration failed");
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setError(null);
    setSuccess(null);
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 50%, rgba(88, 166, 255, 0.1) 0%, transparent 50%)'
    }}>
      <div className="glass-card" style={{ width: '400px', textAlign: 'center' }}>
        <div style={{ marginBottom: '20px', color: 'var(--accent-color)' }}>
          {isRegisterMode ? <FaUserPlus size={40} /> : <FaLock size={40} />}
        </div>
        <h2>{isRegisterMode ? 'Create Account' : 'Access Required'}</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          {isRegisterMode 
            ? 'Register to access the Chemical Visualizer.' 
            : 'Please log in to access the Chemical Visualizer.'}
        </p>

        <form onSubmit={isRegisterMode ? handleRegister : handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: '12px', borderRadius: '6px', background: '#0d1117', border: '1px solid #30363d', color: '#fff' }}
          />
          {isRegisterMode && (
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ padding: '12px', borderRadius: '6px', background: '#0d1117', border: '1px solid #30363d', color: '#fff' }}
            />
          )}
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '12px', borderRadius: '6px', background: '#0d1117', border: '1px solid #30363d', color: '#fff' }}
          />
          {isRegisterMode && (
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{ padding: '12px', borderRadius: '6px', background: '#0d1117', border: '1px solid #30363d', color: '#fff' }}
            />
          )}
          {error && <p style={{ color: 'var(--danger)', fontSize: '0.9rem' }}>{error}</p>}
          {success && <p style={{ color: 'var(--success)', fontSize: '0.9rem' }}>{success}</p>}
          <button type="submit" className="btn">
            {isRegisterMode ? 'Register' : 'Log In'}
          </button>
        </form>

        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #30363d' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {isRegisterMode ? 'Already have an account?' : "Don't have an account?"}{' '}
            <span 
              onClick={toggleMode}
              style={{ color: 'var(--accent-color)', cursor: 'pointer', textDecoration: 'underline' }}
            >
              {isRegisterMode ? 'Login' : 'Register'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
