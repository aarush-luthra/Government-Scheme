import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        const payload = await authService.me();
        if (payload.is_logged_in) {
          setUser({
            id: payload.user_id,
            name: payload.user_name,
            role: payload.role || 'user'
          });
        }
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    bootstrap();
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    isAuthenticated: !!user,
    async login(email, password) {
      const payload = await authService.login(email, password);
      if (!payload.success) {
        throw new Error(payload.message || 'Login failed');
      }
      if (payload.access_token) {
        localStorage.setItem('access_token', payload.access_token);
      }
      setUser({
        id: payload.user.user_id,
        name: payload.user.name,
        role: payload.user.role || 'user'
      });
      return payload;
    },
    async logout() {
      await authService.logout();
      localStorage.removeItem('access_token');
      setUser(null);
    }
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return ctx;
}
