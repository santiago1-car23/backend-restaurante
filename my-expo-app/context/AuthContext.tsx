import React, { createContext, useContext, useState, useEffect } from 'react';
import API from '../constants/api';
import appStorage from '../services/appStorage';

interface AuthContextProps {
  token: string | null;
  user: any;
  login: (username: string, password: string) => Promise<boolean | string>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextProps>({
  token: null,
  user: null,
  login: async () => false,
  logout: () => {},
  loading: false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);


  useEffect(() => {
    const loadToken = async () => {
      setLoading(true);
      const storedToken = await appStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
        await fetchUser(storedToken);
      }
      setLoading(false);
    };
    loadToken();
  }, []);


  const fetchUser = async (token: string) => {
    try {
      const res = await API.get('usuarios/me/', {
        headers: { Authorization: `Token ${token}` },
      });
      setUser(res.data);
    } catch {
      setToken(null);
      setUser(null);
      await appStorage.removeItem('token');
    }
  };

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const res = await API.post('auth/', { username, password });
      setToken(res.data.token);
      setUser(res.data.user);
      await appStorage.setItem('token', res.data.token);
      return true;
    } catch (error: any) {
      // Log completo para depuración
      console.log('LOGIN ERROR:', error, error?.response?.data);
      if (error.response && error.response.data) {
        const data = error.response.data;
        if (typeof data === 'string') return data;
        if (data.detail) return data.detail;
        if (data.non_field_errors) return data.non_field_errors.join(' ');
        return JSON.stringify(data);
      }
      if (error.message) return error.message;
      return 'Error desconocido';
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setToken(null);
    setUser(null);
    await appStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
