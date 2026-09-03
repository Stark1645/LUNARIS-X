import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ConfigPanel } from '../components/registration/ConfigPanel';
import { RegistrationRequest } from '../types';

describe('ConfigPanel Component', () => {
  const initialConfig: RegistrationRequest = {
    sourceImageId: 1,
    referenceImageId: 2,
    algorithm: 'Proposed_Method',
    transformationModel: 'HOMOGRAPHY',
    ratioThreshold: 0.80,
    ransacThreshold: 3.0,
    enableSubpixel: true,
    enableSpatialFilter: true,
  };

  it('renders algorithm selection and geometry model options', () => {
    const setConfig = vi.fn();
    const handleExecute = vi.fn();

    render(
      <ConfigPanel
        config={initialConfig}
        setConfig={setConfig}
        onExecute={handleExecute}
        isExecuting={false}
        canExecute={true}
      />
    );

    expect(screen.getByText(/Proposed Method \(AMSR - Adaptive Multi-Scale\)/i)).toBeInTheDocument();
    expect(screen.getByText(/SIFT Baseline \(Classical DoG \+ Gradients\)/i)).toBeInTheDocument();
    expect(screen.getByText(/RIFT Baseline \(Phase Congruency \+ MIM\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Homography \(8-DOF Projective Planar\)/i)).toBeInTheDocument();
  });

  it('triggers onExecute when Execute Registration button is clicked', () => {
    const handleExecute = vi.fn();

    render(
      <ConfigPanel
        config={initialConfig}
        setConfig={vi.fn()}
        onExecute={handleExecute}
        isExecuting={false}
        canExecute={true}
      />
    );

    const btn = screen.getByRole('button', { name: /Execute Registration/i });
    expect(btn).not.toBeDisabled();
    fireEvent.click(btn);
    expect(handleExecute).toHaveBeenCalledTimes(1);
  });
});
