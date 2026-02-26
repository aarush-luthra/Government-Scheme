import { useEffect, useMemo, useState } from 'react';
import { fetchDashboard, saveScheme, unsaveScheme } from '../services/schemeService';
import { ChatUI } from './ChatUI';
import { Checklist } from './Checklist';
import { CompareModal } from './CompareModal';
import { NotificationCenter } from './NotificationCenter';
import { SchemeSearch } from './SchemeSearch';

export function Dashboard() {
  const [compareOpen, setCompareOpen] = useState(false);
  const [selectedScheme, setSelectedScheme] = useState('PM Kisan');
  const [notifications, setNotifications] = useState([]);
  const [savedSchemes, setSavedSchemes] = useState([]);
  const [pendingSaveMap, setPendingSaveMap] = useState({});

  const savedSchemeNames = useMemo(() => new Set(savedSchemes.map((s) => String(s.scheme_name).toLowerCase())), [savedSchemes]);

  useEffect(() => {
    async function load() {
      try {
        const payload = await fetchDashboard();
        const notifications = payload.notifications || [];
        setNotifications(
          notifications.map((n) => ({
            id: n.id,
            text: `${n.title}: ${n.body}`
          }))
        );
        setSavedSchemes(payload.saved_schemes || []);
      } catch {
        setNotifications([]);
        setSavedSchemes([]);
      }
    }
    load();
  }, []);

  function openCompare(name) {
    setSelectedScheme(name);
    setCompareOpen(true);
  }

  async function onToggleSave(schemeName, currentlySaved) {
    const key = String(schemeName).toLowerCase();
    const previous = savedSchemes;
    setPendingSaveMap((state) => ({ ...state, [key]: true }));

    if (currentlySaved) {
      setSavedSchemes((state) => state.filter((item) => String(item.scheme_name).toLowerCase() !== key));
    } else {
      setSavedSchemes((state) => [{ scheme_name: schemeName, saved_at: new Date().toISOString() }, ...state]);
    }

    try {
      const payload = currentlySaved ? await unsaveScheme(schemeName) : await saveScheme(schemeName);
      setSavedSchemes(payload.saved_schemes || []);
    } catch {
      setSavedSchemes(previous);
    } finally {
      setPendingSaveMap((state) => {
        const next = { ...state };
        delete next[key];
        return next;
      });
    }
  }

  return (
    <main className="layout">
      <h1>Dashboard</h1>
      <div className="grid two">
        <ChatUI />
        <NotificationCenter notifications={notifications} />
      </div>
      <div className="grid two">
        <SchemeSearch
          onOpenCompare={openCompare}
          savedSchemeNames={savedSchemeNames}
          onToggleSave={onToggleSave}
          pendingSaveMap={pendingSaveMap}
        />
        <Checklist activeSchemeHint={selectedScheme} />
      </div>
      <CompareModal open={compareOpen} onClose={() => setCompareOpen(false)} initialScheme={selectedScheme} />
    </main>
  );
}
