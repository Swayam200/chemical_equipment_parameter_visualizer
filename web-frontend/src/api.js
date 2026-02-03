/**
 * API Client Module
 * Configures Axios instance with:
 * - Relative base URL for Vercel proxy
 * - JWT token refresh interceptor
 * - Error message formatting utilities
 *
 * @module api
 */
import axios from 'axios';

/**
 * Configured Axios instance.
 * Uses relative '/api' path for Vercel rewrites to proxy to backend.
 */
const api = axios.create({
  baseURL: '/api',
});

// AI Summary Helper
api.saveAISummary = (uploadId, summaryText) => {
  return api.post(`/upload/${uploadId}/summary/`, { summary: summaryText });
};

// Token refresh interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post('/api/token/refresh/', {
            refresh: refreshToken
          });

          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // Update the authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

          // Retry the original request
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('username');
          window.location.reload();
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
        window.location.reload();
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Formats API errors into user-friendly messages.
 * Handles various backend error formats:
 * - String errors
 * - { error: string }
 * - { detail: string }
 * - { field: [errors] } (validation)
 * - Network errors
 *
 * @param {Error} error - Axios error object
 * @returns {string} Human-readable error message
 */
export const formatErrorMessage = (error) => {

  if (error.response?.data) {
    const data = error.response.data;

    // Handle different error formats from backend
    if (typeof data === 'string') {
      return data;
    }
    if (data.error) {
      return data.error;
    }
    if (data.detail) {
      return data.detail;
    }
    if (data.message) {
      return data.message;
    }
    // Handle validation errors (object with field names)
    if (typeof data === 'object') {
      const messages = [];
      for (const [field, errors] of Object.entries(data)) {
        if (Array.isArray(errors)) {
          messages.push(`${field}: ${errors.join(', ')}`);
        } else if (typeof errors === 'string') {
          messages.push(`${field}: ${errors}`);
        }
      }
      if (messages.length > 0) {
        return messages.join('\n');
      }
    }
  }

  // Network errors
  if (error.code === 'NETWORK_ERROR' || !error.response) {
    return 'Network error. Please check your connection and try again.';
  }

  // Default fallback
  return error.message || 'An unexpected error occurred. Please try again.';
};

// File size constants
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const MAX_FILE_SIZE_DISPLAY = '5MB';

export default api;
