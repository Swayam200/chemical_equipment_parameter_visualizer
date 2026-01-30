import React, { useState } from 'react';
import { FaLock, FaUserPlus } from 'react-icons/fa';
import api from '../api';
import loginBg from '../assets/images/chemical_plant_login.jpg';

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

      // Store JWT token and username
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username);

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

      // Store JWT token and username
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username);

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
      backgroundImage: `linear-gradient(rgba(11, 12, 16, 0.8), rgba(11, 12, 16, 0.9)), url(${loginBg})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed'
    }}>
      <div className="glass-card" style={{
        width: '400px',
        textAlign: 'center',
        padding: '32px',
        border: '1px solid var(--accent-color)',
        boxShadow: '0 0 20px rgba(69, 162, 158, 0.15)'
      }}>
        <div style={{ marginBottom: '24px', color: 'var(--accent-color)' }}>
          {isRegisterMode ? <FaUserPlus size={48} /> : <FaLock size={48} />}
        </div>

        <h2 style={{
          fontSize: '1.8rem',
          marginBottom: '8px',
          borderLeft: 'none',
          paddingLeft: 0,
          textShadow: '0 0 10px rgba(102, 252, 241, 0.4)'
        }}>
          {isRegisterMode ? 'INITIATE ACCESS' : 'SYSTEM LOGIN'}
        </h2>

        <p style={{
          color: 'var(--text-secondary)',
          marginBottom: '32px',
          fontFamily: 'var(--font-family)',
          fontSize: '0.85rem',
          letterSpacing: '1px'
        }}>
          {isRegisterMode
            ? 'CREATE AUTHORIZED PERSONNEL CREDENTIALS'
            : 'AUTHENTICATION REQUIRED FOR TERMINAL ACCESS'}
        </p>

        <form onSubmit={isRegisterMode ? handleRegister : handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="USERNAME"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '14px',
                background: 'rgba(11, 12, 16, 0.8)',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {isRegisterMode && (
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{
                  width: '100%',
                  padding: '14px',
                  background: 'rgba(11, 12, 16, 0.8)',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          )}

          <div style={{ position: 'relative' }}>
            <input
              type="password"
              placeholder="PASSWORD"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '14px',
                background: 'rgba(11, 12, 16, 0.8)',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {isRegisterMode && (
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                placeholder="CONFIRM CREDENTIALS"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '14px',
                  background: 'rgba(11, 12, 16, 0.8)',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          )}

          {error && (
            <div style={{
              color: 'var(--danger)',
              fontSize: '0.8rem',
              fontFamily: 'var(--font-family)',
              border: '1px solid var(--danger)',
              padding: '8px',
              background: 'rgba(252, 32, 68, 0.1)'
            }}>
              ERROR: {error.toUpperCase()}
            </div>
          )}

          {success && (
            <div style={{
              color: 'var(--success)',
              fontSize: '0.8rem',
              fontFamily: 'var(--font-family)',
              border: '1px solid var(--success)',
              padding: '8px',
              background: 'rgba(32, 252, 143, 0.1)'
            }}>
              SUCCESS: {success.toUpperCase()}
            </div>
          )}

          <button type="submit" className="btn" style={{ marginTop: '8px' }}>
            {isRegisterMode ? 'ESTABLISH LINK' : 'ACCESS TERMINAL'}
          </button>
        </form>

        <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontFamily: 'var(--font-family)' }}>
            {isRegisterMode ? 'EXISTING PERSONNEL?' : "NEW PERSONNEL?"}{' '}
            <span
              onClick={toggleMode}
              style={{
                color: 'var(--accent-color)',
                cursor: 'pointer',
                textDecoration: 'none',
                fontWeight: 'bold',
                marginLeft: '8px',
                borderBottom: '1px dashed var(--accent-color)'
              }}
            >
              {isRegisterMode ? 'LOGIN' : 'REGISTER'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
