import React, { useState } from 'react';
import api from '../api';
import loginBg from '../assets/images/chemical_plant_login.jpg';

const Login = ({ onLogin, theme, toggleTheme }) => {
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
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username);
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
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username);
      setSuccess("Registration successful! Logging you in...");
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
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative bg-cover bg-center" style={{ backgroundImage: `url(${loginBg})` }}>
      <div className={`absolute inset-0 ${theme === 'light' ? 'bg-slate-50/90' : 'bg-slate-900/90'}`}></div>

      {toggleTheme && (
        <button
          onClick={toggleTheme}
          className="absolute top-5 right-5 z-20 p-2 rounded-lg bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 transition-all"
        >
          {theme === 'dark' ? <span className="material-symbols-outlined">light_mode</span> : <span className="material-symbols-outlined">dark_mode</span>}
        </button>
      )}

      <div className="relative z-10 w-full max-w-md p-8 bg-white dark:bg-slate-850/90 backdrop-blur-md rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700">
        <div className="text-center mb-8">
          {/* Circular Container with simplified padding to ensure logo fills it nicely */}
          <div className="inline-block p-1 rounded-full bg-white ring-4 ring-primary/10 mb-4 shadow-lg overflow-hidden">
            <img src="/logo.png" alt="Carbon Sleuth Logo" className="w-28 h-28 object-cover rounded-full" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            {isRegisterMode ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">
            {isRegisterMode ? 'Join the authorized personnel registry' : 'Enter your credentials to access the terminal'}
          </p>
        </div>

        <form onSubmit={isRegisterMode ? handleRegister : handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-slate-900 dark:text-white transition-all"
              placeholder="Enter username"
            />
          </div>

          {isRegisterMode && (
            <div>
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-slate-900 dark:text-white transition-all"
                placeholder="name@company.com"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-slate-900 dark:text-white transition-all"
              placeholder="••••••••"
            />
          </div>

          {isRegisterMode && (
            <div>
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-slate-900 dark:text-white transition-all"
                placeholder="••••••••"
              />
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-xs font-medium flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">error</span>
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-600 dark:text-green-400 text-xs font-medium flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              {success}
            </div>
          )}

          <button
            type="submit"
            className="w-full py-2.5 bg-primary hover:bg-blue-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-blue-500/30 transition-all transform active:scale-95"
          >
            {isRegisterMode ? 'Register Account' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {isRegisterMode ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={toggleMode}
              className="text-primary font-semibold hover:underline"
            >
              {isRegisterMode ? 'Sign In' : 'Create Account'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
