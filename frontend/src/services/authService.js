import { apiRequest } from './apiClient';

export async function login(email, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });
}

export async function signup(form) {
  return apiRequest('/profile', {
    method: 'POST',
    body: JSON.stringify(form)
  });
}

export async function me() {
  return apiRequest('/auth/me');
}

export async function logout() {
  return apiRequest('/auth/logout', { method: 'POST' });
}
