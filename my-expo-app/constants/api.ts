import axios from 'axios';
import appStorage from '../services/appStorage';

// Expo Go en celular no puede usar 127.0.0.1 del PC.
// Usa la IP local de esta maquina y permite override por variable de entorno.
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL?.trim() ||
  'http://190.157.8.108:8000/api/';

const API = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

API.interceptors.request.use(
  async config => {
    const token = await appStorage.getItem('token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export { API_BASE_URL };
export default API;
