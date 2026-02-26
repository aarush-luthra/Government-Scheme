import { useEffect, useState } from 'react';
import { fetchAdminAnalytics, fetchAdminIngestionHealth } from '../services/schemeService';

export function AdminPanel() {
  const [rows, setRows] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const payload = await fetchAdminIngestionHealth();
        setRows(payload.rows || []);
        const analyticsPayload = await fetchAdminAnalytics();
        setAnalytics(analyticsPayload.analytics || null);
        setError('');
      } catch (err) {
        setError(err.message);
      }
    }
    load();
  }, []);

  return (
    <main className="layout">
      <h1>Admin Dashboard</h1>
      {error ? <p data-testid="admin-error" className="error">{error}</p> : null}
      {analytics ? (
        <section className="card">
          <h2>Analytics Dashboard</h2>
          <p data-testid="failed-comparisons">Failed comparisons: {analytics.failed_comparisons}</p>
          <p data-testid="alert-success-rate">Alert delivery success: {analytics.alert_delivery?.success_rate_percent ?? 0}%</p>
          <p data-testid="saved-scheme-count">Saved schemes: {analytics.saved_schemes?.total_saved ?? 0}</p>
        </section>
      ) : null}
      <ul data-testid="admin-rows">
        {rows.map((row) => <li key={row.source_name}>{row.source_name}: {row.total_schemes}</li>)}
      </ul>
    </main>
  );
}
