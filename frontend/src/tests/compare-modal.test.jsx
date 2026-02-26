import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { CompareModal } from '../components/CompareModal';

vi.mock('../services/schemeService', () => ({
  autosuggestSchemes: vi.fn(async () => ({ suggestions: ['Atal Pension Yojana'] })),
  compareSchemes: vi.fn(async (schemeNames) => ({
    comparison: schemeNames.map((name) => ({
      scheme_name: name,
      eligibility: 'Eligible',
      benefits: 'Benefit',
      documents: 'ID Proof'
    }))
  }))
}));

describe('CompareModal', () => {
  const onClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows validation error for invalid comparison', async () => {
    render(<CompareModal open={true} onClose={onClose} initialScheme="PM Kisan" />);
    fireEvent.click(screen.getByTestId('run-compare'));
    expect(await screen.findByTestId('compare-error')).toHaveTextContent('Pick 2 or 3 schemes');
  });

  it('renders table for valid comparison', async () => {
    render(<CompareModal open={true} onClose={onClose} initialScheme="PM Kisan" />);
    fireEvent.change(screen.getByTestId('compare-b'), { target: { value: 'Atal Pension Yojana' } });
    fireEvent.click(screen.getByTestId('run-compare'));

    await waitFor(() => {
      expect(screen.getByTestId('compare-results')).toBeInTheDocument();
    });
  });
});
