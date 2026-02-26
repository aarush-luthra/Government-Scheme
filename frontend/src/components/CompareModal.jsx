import { useEffect, useState } from 'react';
import { autosuggestSchemes, compareSchemes } from '../services/schemeService';
import { useDebouncedValue } from '../hooks/useDebouncedValue';

export function CompareModal({ open, onClose, initialScheme }) {
  const [schemeA, setSchemeA] = useState('');
  const [schemeB, setSchemeB] = useState('');
  const [schemeC, setSchemeC] = useState('');
  const [comparison, setComparison] = useState([]);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [activeField, setActiveField] = useState('a');

  const debouncedA = useDebouncedValue(schemeA, 200);
  const debouncedB = useDebouncedValue(schemeB, 200);
  const debouncedC = useDebouncedValue(schemeC, 200);

  useEffect(() => {
    if (!open) return;
    setSchemeA(initialScheme || '');
    setSchemeB('');
    setSchemeC('');
    setComparison([]);
    setError('');
  }, [open, initialScheme]);

  useEffect(() => {
    async function loadSuggestions() {
      if (!open) return;
      const source = activeField === 'a' ? debouncedA : activeField === 'b' ? debouncedB : debouncedC;
      if (source.trim().length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const payload = await autosuggestSchemes(source);
        setSuggestions(payload.suggestions || []);
      } catch {
        setSuggestions([]);
      }
    }
    loadSuggestions();
  }, [open, debouncedA, debouncedB, debouncedC, activeField]);

  async function onCompare() {
    const selected = [schemeA, schemeB, schemeC].map((x) => x.trim()).filter(Boolean);
    if (selected.length < 2 || selected.length > 3) {
      setError('Pick 2 or 3 schemes to compare.');
      setComparison([]);
      return;
    }
    if (new Set(selected.map((x) => x.toLowerCase())).size !== selected.length) {
      setError('Comparison requires unique scheme names.');
      setComparison([]);
      return;
    }
    try {
      const payload = await compareSchemes(selected);
      setComparison(payload.comparison || []);
      setError('');
    } catch (err) {
      setError(err.message || 'Comparison failed');
      setComparison([]);
    }
  }

  function applySuggestion(name) {
    if (activeField === 'a') setSchemeA(name);
    if (activeField === 'b') setSchemeB(name);
    if (activeField === 'c') setSchemeC(name);
  }

  if (!open) return null;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal card compare-modal">
        <h2>Compare Schemes</h2>
        <div className="grid">
          <input data-testid="compare-a" value={schemeA} onFocus={() => setActiveField('a')} onChange={(e) => setSchemeA(e.target.value)} placeholder="Scheme 1" />
          <input data-testid="compare-b" value={schemeB} onFocus={() => setActiveField('b')} onChange={(e) => setSchemeB(e.target.value)} placeholder="Scheme 2" />
          <input data-testid="compare-c" value={schemeC} onFocus={() => setActiveField('c')} onChange={(e) => setSchemeC(e.target.value)} placeholder="Optional Scheme 3" />
        </div>
        <ul data-testid="compare-suggestions">
          {suggestions.length === 0 ? <li className="muted">No suggestions</li> : null}
          {suggestions.map((name) => (
            <li key={name}>
              <button className="suggestion-item" onClick={() => applySuggestion(name)}>{name}</button>
            </li>
          ))}
        </ul>
        <div className="row">
          <button data-testid="run-compare" onClick={onCompare}>Run Compare</button>
          <button onClick={onClose}>Close</button>
        </div>
        {error ? <p data-testid="compare-error" className="error">{error}</p> : null}

        {comparison.length > 0 ? (
          <div className="table-wrap" data-testid="compare-results">
            <table>
              <thead>
                <tr>
                  <th>Scheme</th>
                  <th>Eligibility</th>
                  <th>Benefits</th>
                  <th>Documents</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row) => (
                  <tr key={row.scheme_name}>
                    <td>{row.scheme_name}</td>
                    <td>{row.eligibility}</td>
                    <td>{row.benefits}</td>
                    <td>{row.documents}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </div>
  );
}
