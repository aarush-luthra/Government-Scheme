import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { SchemeSearch } from '../components/SchemeSearch';

vi.mock('../services/schemeService', () => ({
  autosuggestSchemes: vi.fn(async () => ({ suggestions: ['PM Kisan', 'PM Awas Yojana'] })),
  searchSchemes: vi.fn(async () => ({
    results: [
      { scheme_name: 'PM Kisan', eligibility: 'Any farmer', benefits: 'Income support' }
    ]
  }))
}));

describe('SchemeSearch', () => {
  const props = {
    onOpenCompare: vi.fn(),
    savedSchemeNames: new Set(),
    onToggleSave: vi.fn(),
    pendingSaveMap: {}
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders autosuggest and allows selecting suggestion', async () => {
    render(<SchemeSearch {...props} />);
    const input = screen.getByTestId('scheme-query');
    fireEvent.change(input, { target: { value: 'PM' } });

    await waitFor(() => {
      expect(screen.getByTestId('autosuggest-dropdown')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('autosuggest-item-PM Kisan'));
    expect(screen.getByTestId('scheme-query')).toHaveValue('PM Kisan');
  });

  it('runs search and renders scheme cards', async () => {
    render(<SchemeSearch {...props} />);
    fireEvent.click(screen.getByTestId('scheme-search'));

    await waitFor(() => {
      expect(screen.getByTestId('scheme-card-PM Kisan')).toBeInTheDocument();
    });
  });
});
