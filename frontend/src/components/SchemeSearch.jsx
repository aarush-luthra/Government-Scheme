import { useEffect, useState } from 'react';
import { autosuggestSchemes, searchSchemes } from '../services/schemeService';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { SchemeCard } from './SchemeCard';

export function SchemeSearch({ onOpenCompare, savedSchemeNames, onToggleSave, pendingSaveMap }) {
  const [query, setQuery] = useState('PM Kisan');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebouncedValue(query, 250);

  useEffect(() => {
    async function loadSuggestions() {
      if (debouncedQuery.trim().length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const payload = await autosuggestSchemes(debouncedQuery);
        setSuggestions(payload.suggestions || []);
      } catch {
        setSuggestions([]);
      }
    }
    loadSuggestions();
  }, [debouncedQuery]);

  async function onSearch() {
    setError('');
    setShowSuggestions(false);
    try {
      const payload = await searchSchemes(query);
      setResults(payload.results || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
    }
  }

  return (
    <section className="card">
      <h2>Scheme Search + Q&A</h2>
      <div className="search-wrap">
        <div className="row">
          <input
            data-testid="scheme-query"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Search in natural language (e.g. farmer pension schemes in Haryana)"
          />
          <button data-testid="scheme-search" onClick={onSearch}>Search</button>
        </div>
        {showSuggestions ? (
          <ul className="suggestions" data-testid="autosuggest-dropdown">
            {suggestions.length === 0 ? <li className="muted">No suggestions</li> : null}
            {suggestions.map((item) => (
              <li key={item}>
                <button
                  type="button"
                  className="suggestion-item"
                  data-testid={`autosuggest-item-${item}`}
                  onClick={() => {
                    setQuery(item);
                    setShowSuggestions(false);
                  }}
                >
                  {item}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
      {error ? <p className="error">{error}</p> : null}
      {results.length === 0 ? <p className="muted">No schemes yet. Try a search.</p> : null}
      <div className="grid">
        {results.map((scheme) => (
          <SchemeCard
            key={scheme.scheme_name}
            scheme={scheme}
            onCompareSelect={onOpenCompare}
            onToggleSave={onToggleSave}
            isSaved={savedSchemeNames.has(scheme.scheme_name.toLowerCase())}
            isSaving={Boolean(pendingSaveMap[scheme.scheme_name.toLowerCase()])}
          />
        ))}
      </div>
    </section>
  );
}
