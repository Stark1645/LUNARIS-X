import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScientificMetricsPanel } from '../components/metrics/ScientificMetricsPanel';
import { RegistrationResponseDTO } from '../types';

describe('ScientificMetricsPanel Component', () => {
  const mockResult: RegistrationResponseDTO = {
    jobId: 101,
    status: 'SUCCESS',
    algorithm: 'Proposed_Method',
    selectedTransformationModel: 'HOMOGRAPHY',
    transformationMatrixJson: '[[1.002, -0.001, 5.23], [0.001, 0.998, -3.11], [0.0, 0.0, 1.0]]',
    sourceImageId: 1,
    referenceImageId: 2,
    sourceFilename: 'src.png',
    referenceFilename: 'ref.png',
    metrics: {
      candidateMatchesCount: 95,
      inlierMatchesCount: 87,
      inlierRatioPercent: 91.58,
      rmseInliersPx: 1.27,
      rmseGroundTruthPx: 0.41,
      meanSubpixelResidualPx: 0.22,
      subpixelAccuracyRate05px: 0.88,
      spatialGiniCoefficient: 0.32,
      latencyMs: 390.0,
      dataCategory: 'SYNTHETIC_BENCHMARK',
    },
    createdAt: '2026-09-02T12:00:00',
  };

  it('renders all measured numerical metrics accurately without substituting missing zero', () => {
    render(<ScientificMetricsPanel result={mockResult} />);

    expect(screen.getByText('87')).toBeInTheDocument(); // Verified Inliers
    expect(screen.getByText(/91.6%/i)).toBeInTheDocument(); // Inlier Ratio
    expect(screen.getByText(/1.27/i)).toBeInTheDocument(); // Inlier RMSE
    expect(screen.getByText(/0.41/i)).toBeInTheDocument(); // GT RMSE
    expect(screen.getByText(/0.220/i)).toBeInTheDocument(); // Subpixel residual
    expect(screen.getByText(/0.32/i)).toBeInTheDocument(); // Spatial Gini
    expect(screen.getByText(/390/i)).toBeInTheDocument(); // Latency
    expect(screen.getByText('HOMOGRAPHY')).toBeInTheDocument(); // Selected model
  });

  it('displays N/A when ground-truth RMSE is null on operational real flight data', () => {
    const flightResult: RegistrationResponseDTO = {
      ...mockResult,
      metrics: {
        ...mockResult.metrics,
        rmseGroundTruthPx: null,
        dataCategory: 'AUTHENTIC_CH2_PRADAN',
      },
    };

    render(<ScientificMetricsPanel result={flightResult} />);

    expect(screen.getByText('N/A')).toBeInTheDocument();
    expect(screen.getByText('AUTHENTIC_CH2_PRADAN')).toBeInTheDocument();
  });
});
