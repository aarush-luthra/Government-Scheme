import { apiRequest } from './apiClient';

export async function searchSchemes(query, limit = 8) {
  return apiRequest('/api/v1/schemes/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit })
  });
}

export async function autosuggestSchemes(query, limit = 8) {
  const encoded = encodeURIComponent(query);
  return apiRequest(`/api/v1/schemes/autosuggest?q=${encoded}&limit=${limit}`);
}

export async function compareSchemes(schemeNames) {
  return apiRequest('/api/v1/schemes/compare', {
    method: 'POST',
    body: JSON.stringify({ scheme_names: schemeNames })
  });
}

export async function fetchDashboard() {
  return apiRequest('/api/v1/saved-dashboard');
}

export async function dispatchAlertsNow() {
  return apiRequest('/api/v1/alerts/dispatch', { method: 'POST' });
}

export async function saveScheme(schemeName) {
  return apiRequest('/api/v1/saved-schemes', {
    method: 'POST',
    body: JSON.stringify({ scheme_name: schemeName })
  });
}

export async function unsaveScheme(schemeName) {
  const encoded = encodeURIComponent(schemeName);
  return apiRequest(`/api/v1/saved-schemes/${encoded}`, {
    method: 'DELETE'
  });
}

export async function getChecklist(schemeName) {
  const encoded = encodeURIComponent(schemeName);
  return apiRequest(`/api/v1/checklists/${encoded}`);
}

export async function generateChecklist(schemeName) {
  return apiRequest('/api/v1/checklists/generate', {
    method: 'POST',
    body: JSON.stringify({ scheme_name: schemeName })
  });
}

export async function updateChecklist(schemeName, items) {
  const encoded = encodeURIComponent(schemeName);
  return apiRequest(`/api/v1/checklists/${encoded}`, {
    method: 'POST',
    body: JSON.stringify({ scheme_name: schemeName, items })
  });
}

export async function fetchAdminIngestionHealth() {
  return apiRequest('/api/v1/admin/ingestion-health');
}

export async function fetchAdminAnalytics() {
  return apiRequest('/api/v1/admin/analytics');
}
