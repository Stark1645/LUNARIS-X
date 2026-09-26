import React from 'react';
import { Sliders, Play, Cpu, Target, Loader2 } from 'lucide-react';
import { AlgorithmType, TransformationModelType, RegistrationRequest } from '../../types';

interface ConfigPanelProps {
  config: RegistrationRequest;
  setConfig: React.Dispatch<React.SetStateAction<RegistrationRequest>>;
  onExecute: () => void;
  isExecuting: boolean;
  canExecute: boolean;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  config,
  setConfig,
  onExecute,
  isExecuting,
  canExecute,
}) => {
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div className="card-header" style={{ marginBottom: '1rem', paddingBottom: '0.65rem' }}>
        <div className="card-title">
          <Sliders size={16} style={{ color: 'var(--accent-blue)' }} />
          <span>Alignment Parameters & Execution</span>
        </div>
        <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          Configure transformation model, feature ratio, and sub-pixel thresholds
        </div>
      </div>

      {/* Main Parameters Horizontal Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem', alignItems: 'end' }}>
        {/* Col 1: Algorithm */}
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Cpu size={13} />
              <span>Algorithm Pipeline</span>
            </span>
          </label>
          <select
            className="form-select"
            value={config.algorithm}
            onChange={(e) => setConfig({ ...config, algorithm: e.target.value as AlgorithmType })}
            disabled={isExecuting}
          >
            <option value="Proposed_Method">Proposed Method (AMSR)</option>
            <option value="SIFT_Baseline">SIFT Baseline (Scale-Space DoG)</option>
            <option value="RIFT_Baseline">RIFT Baseline (Phase Congruency)</option>
          </select>
        </div>

        {/* Col 2: Geometry Model */}
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Target size={13} />
              <span>Geometry Model</span>
            </span>
          </label>
          <select
            className="form-select"
            value={config.transformationModel}
            onChange={(e) => setConfig({ ...config, transformationModel: e.target.value as TransformationModelType })}
            disabled={isExecuting}
          >
            <option value="HOMOGRAPHY">Homography (8-DOF Projective)</option>
            <option value="AFFINE">Affine (6-DOF Affine)</option>
            <option value="SIMILARITY">Similarity (4-DOF Scale & Rotate)</option>
            <option value="TRANSLATION">Translation (2-DOF Translation)</option>
          </select>
        </div>

        {/* Col 3: Lowe's Ratio */}
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">
            <span>Lowe's Ratio</span>
            <span className="font-mono">{config.ratioThreshold?.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0.50"
            max="0.95"
            step="0.05"
            value={config.ratioThreshold}
            onChange={(e) => setConfig({ ...config, ratioThreshold: parseFloat(e.target.value) })}
            disabled={isExecuting}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>

        {/* Col 4: RANSAC */}
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">
            <span>RANSAC Inlier Tolerance</span>
            <span className="font-mono">{config.ransacThreshold?.toFixed(1)} px</span>
          </label>
          <input
            type="range"
            min="1.0"
            max="10.0"
            step="0.5"
            value={config.ransacThreshold}
            onChange={(e) => setConfig({ ...config, ransacThreshold: parseFloat(e.target.value) })}
            disabled={isExecuting}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>
      </div>

      {/* Row 2: Toggles on left + Prominent Run Registration Button on right */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: '1.1rem',
          paddingTop: '0.85rem',
          borderTop: '1px solid var(--border-subtle)',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', cursor: 'pointer', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            <input
              type="checkbox"
              checked={config.enableSubpixel}
              onChange={(e) => setConfig({ ...config, enableSubpixel: e.target.checked })}
              disabled={isExecuting}
              style={{ accentColor: 'var(--accent-blue)' }}
            />
            <span>Sub-pixel Hessian Parabolic Refinement</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', cursor: 'pointer', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            <input
              type="checkbox"
              checked={config.enableSpatialFilter}
              onChange={(e) => setConfig({ ...config, enableSpatialFilter: e.target.checked })}
              disabled={isExecuting}
              style={{ accentColor: 'var(--accent-blue)' }}
            />
            <span>Spatial Gini (G_k) Dispersion Constraint</span>
          </label>
        </div>

        {/* Primary Action Button */}
        <button
          className="btn btn-primary"
          onClick={onExecute}
          disabled={!canExecute || isExecuting}
          style={{
            padding: '0.65rem 1.75rem',
            fontSize: '0.88rem',
            fontWeight: 600,
            borderRadius: 'var(--radius-sm)',
            minWidth: '200px',
          }}
        >
          {isExecuting ? (
            <>
              <Loader2 size={16} className="spin" />
              <span>Aligning Planetary Frames...</span>
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              <span>Run Registration</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
