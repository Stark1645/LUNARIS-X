import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock API service to avoid network calls during unit testing
vi.mock('../services/api', () => ({
  apiService: {
    getHealth: vi.fn().mockResolvedValue({
      status: 'UP',
      backendVersion: '1.0.0',
      pythonServiceStatus: 'UP',
      pythonServiceUrl: 'http://localhost:8000',
      databaseStatus: 'UP',
      supportedAlgorithms: ['Proposed_Method', 'SIFT_Baseline', 'RIFT_Baseline'],
    }),
    getAllExperiments: vi.fn().mockResolvedValue([]),
    getImages: vi.fn().mockResolvedValue([]),
  },
  parseApiError: vi.fn(() => 'Error message'),
}));

describe('App Root Component', () => {
  it('renders the header with project title and navigation tabs', () => {
    render(<App />);

    expect(screen.getByText(/SIH26166 — Lunar Image Registration Engine/i)).toBeInTheDocument();
    expect(screen.getByText(/Registration Workspace/i)).toBeInTheDocument();
    expect(screen.getByText(/Benchmark Registry/i)).toBeInTheDocument();
    expect(screen.getByText(/System Health/i)).toBeInTheDocument();
  });

  it('renders Source (Moving) and Reference (Fixed) upload sections by default', () => {
    render(<App />);

    expect(screen.getByText(/SOURCE \(MOVING IMAGE\)/i)).toBeInTheDocument();
    expect(screen.getByText(/REFERENCE \(FIXED IMAGE\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Execute Registration/i)).toBeInTheDocument();
  });
});
