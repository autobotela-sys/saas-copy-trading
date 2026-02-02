// Authentication utilities
import { authApi, User, Token } from './api';
export type { User };
import { useRouter } from 'next/navigation';

const AUTH_TOKEN_KEY = 'auth_token';
const USER_KEY = 'user';

// Store auth token
export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
};

// Get auth token
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(AUTH_TOKEN_KEY);
};

// Store user data
export const setUser = (user: User): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
};

// Get user data
export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

// Clear auth data
export const clearAuth = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return getAuthToken() !== null;
};

// Check if user is admin
export const isAdmin = (): boolean => {
  const user = getUser();
  return user?.role === 'ADMIN';
};

// Login function
export const login = async (email: string, password: string): Promise<User> => {
  const tokenData = await authApi.login({ email, password });
  setAuthToken(tokenData.access_token);
  
  const user = await authApi.getCurrentUser();
  setUser(user);
  
  return user;
};

// Logout function
export const logout = (): void => {
  clearAuth();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
};

// Register function
export const register = async (email: string, password: string): Promise<User> => {
  const user = await authApi.register({ email, password });
  return user;
};

// Refresh user data
export const refreshUser = async (): Promise<User | null> => {
  try {
    const user = await authApi.getCurrentUser();
    setUser(user);
    return user;
  } catch {
    clearAuth();
    return null;
  }
};
