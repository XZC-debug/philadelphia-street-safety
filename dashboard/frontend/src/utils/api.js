import axios from 'axios';

// Use environment variable if available, otherwise default to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL
  ? `${process.env.REACT_APP_API_URL}/api`
  : 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// API 调用函数
export const apiService = {
  // 获取所有街区
  getNeighborhoods: () => api.get('/neighborhoods'),

  // 获取街区的地理数据
  getNeighborhoodData: (neighborhood) =>
    api.get(`/data/${encodeURIComponent(neighborhood)}`),

  // 获取犯罪事件
  getIncidents: (neighborhood, params = {}) =>
    api.get(`/incidents/${encodeURIComponent(neighborhood)}`, { params }),

  // 获取街区统计
  getStats: (neighborhood) =>
    api.get(`/stats/${encodeURIComponent(neighborhood)}`),

  // 获取所有街区对比数据
  getComparison: () => api.get('/comparison'),
};

export default api;
