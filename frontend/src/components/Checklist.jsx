import { useEffect, useState } from 'react';
import { autosuggestSchemes, generateChecklist, getChecklist, updateChecklist } from '../services/schemeService';
import { useDebouncedValue } from '../hooks/useDebouncedValue';

const CHECKLIST_KEY = 'active_checklist_scheme';

export function Checklist({ activeSchemeHint }) {
  const [schemeName, setSchemeName] = useState(localStorage.getItem(CHECKLIST_KEY) || activeSchemeHint || 'PM Kisan');
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [pickerQuery, setPickerQuery] = useState('');
  const [pickerSuggestions, setPickerSuggestions] = useState([]);
  const debouncedPicker = useDebouncedValue(pickerQuery, 220);

  useEffect(() => {
    localStorage.setItem(CHECKLIST_KEY, schemeName);
  }, [schemeName]);

  useEffect(() => {
    async function load() {
      if (!schemeName) return;
      setLoading(true);
      setError('');
      try {
        const checklist = await getChecklist(schemeName);
        setItems(checklist.items || []);
      } catch {
        try {
          const generated = await generateChecklist(schemeName);
          setItems(generated.checklist?.items || []);
        } catch (err) {
          setError(err.message || 'Could not load checklist');
          setItems([]);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [schemeName]);

  useEffect(() => {
    async function loadSuggestions() {
      if (!isPickerOpen || debouncedPicker.trim().length < 2) {
        setPickerSuggestions([]);
        return;
      }
      try {
        const payload = await autosuggestSchemes(debouncedPicker);
        setPickerSuggestions(payload.suggestions || []);
      } catch {
        setPickerSuggestions([]);
      }
    }
    loadSuggestions();
  }, [debouncedPicker, isPickerOpen]);

  async function toggle(itemId) {
    const optimistic = items.map((item) => item.id === itemId ? { ...item, completed: !item.completed } : item);
    const previous = items;
    setItems(optimistic);
    try {
      await updateChecklist(schemeName, optimistic);
    } catch {
      setItems(previous);
      setError('Failed to save checklist update');
    }
  }

  return (
    <section className="card">
      <div className="row">
        <h2>Checklist</h2>
        <button data-testid="open-checklist-picker" onClick={() => setIsPickerOpen(true)}>Change Scheme</button>
      </div>
      <p data-testid="checklist-scheme">Scheme: {schemeName}</p>
      {loading ? <p>Loading checklist...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <ul data-testid="checklist-items">
        {items.map((item) => (
          <li key={item.id}>
            <label>
              <input
                data-testid={`check-${item.id}`}
                type="checkbox"
                checked={Boolean(item.completed)}
                onChange={() => toggle(item.id)}
              />
              {item.title}
            </label>
          </li>
        ))}
      </ul>

      {isPickerOpen ? (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal card">
            <h3>Select Scheme</h3>
            <input
              data-testid="checklist-picker-input"
              value={pickerQuery}
              onChange={(e) => setPickerQuery(e.target.value)}
              placeholder="Type to autosuggest"
            />
            <ul data-testid="checklist-picker-suggestions">
              {pickerSuggestions.length === 0 ? <li className="muted">No suggestions</li> : null}
              {pickerSuggestions.map((name) => (
                <li key={name}>
                  <button
                    className="suggestion-item"
                    onClick={() => {
                      setSchemeName(name);
                      setIsPickerOpen(false);
                      setPickerQuery('');
                    }}
                  >
                    {name}
                  </button>
                </li>
              ))}
            </ul>
            <div className="row">
              <button onClick={() => setIsPickerOpen(false)}>Close</button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
