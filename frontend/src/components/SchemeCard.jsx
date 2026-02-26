export function SchemeCard({ scheme, onCompareSelect, onToggleSave, isSaved, isSaving }) {
  return (
    <article className="card scheme-card" data-testid={`scheme-card-${scheme.scheme_name}`}>
      <h3>{scheme.scheme_name}</h3>
      <p><strong>Eligibility:</strong> {scheme.eligibility || 'Not specified'}</p>
      <p><strong>Benefits:</strong> {scheme.benefits || 'Not specified'}</p>
      <div className="row">
        <button data-testid={`compare-${scheme.scheme_name}`} onClick={() => onCompareSelect(scheme.scheme_name)}>Compare</button>
        <button
          data-testid={`save-toggle-${scheme.scheme_name}`}
          onClick={() => onToggleSave(scheme.scheme_name, isSaved)}
          disabled={isSaving}
        >
          {isSaved ? 'Unsave' : 'Save'}
        </button>
      </div>
    </article>
  );
}
