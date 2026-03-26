import axios from 'axios';
import type { ApiError } from '../types/api';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
});

// Request interceptor: attach store ID
api.interceptors.request.use((config) => {
  // Dynamic import to avoid circular deps
  const { useAppStore } = require('../stores/appStore');
  const storeId = useAppStore.getState().activeStoreId;
  if (storeId) {
    config.headers['X-Store-Id'] = storeId;
  }
  return config;
});

// Response interceptor: normalize errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data) {
      const data = error.response.data;
      const apiError: ApiError = {
        message: data.error || 'Unknown error',
        code: data.code || 'UNKNOWN',
        detail: data.detail || null,
      };
      return Promise.reject(apiError);
    }
    return Promise.reject({
      message: error.message || 'Network error',
      code: 'NETWORK_ERROR',
      detail: null,
    });
  }
);

export default api;
