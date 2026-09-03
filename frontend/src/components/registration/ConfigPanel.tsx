import React from 'react';
import { Sliders, Play, Cpu, Target } from 'lucide-react';
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
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Sliders size={18} color="var(--accent-cyan)" />
          <span>Registration Configuration</span>
        </div>
        <span className="badge badge-category">Spring Boot / ML Engine API</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        {/* Algorithm Selection */}
        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Cpu size={14} />
            <span>Algorithm Backend</span>
          </label>
          <select
            className="form-select"
            value={config.algorithm}
            onChange={(e) => setConfig({ ...config, algorithm: e.target.value as AlgorithmType })}
            disabled={isExecuting}
          >
            <option value="Proposed_Method">Proposed Method (AMSR - Adaptive Multi-Scale)</option>
            <option value="SIFT_Baseline">SIFT Baseline (Classical DoG + Gradients)</option>
            <option value="RIFT_Baseline">RIFT Baseline (Phase Congruency + MIM)</option>
          </select>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            {config.algorithm === 'Proposed_Method' && 'Adaptive Scale Bridge + Shadow-Boundary Suppression + Sub-pixel Refinement.'}
            {config.algorithm === 'SIFT_Baseline' && 'Standard Scale-space DoG extrema. Degrades under shadow reversals.'}
            {config.algorithm === 'RIFT_Baseline' && 'Log-Gabor structural energy. Fails under >4x scale disparity without pyramid.'}
          </div>
        </div>

        {/* Transformation Model */}
        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Target size={14} />
            <span>Target Geometry Model</span>
          </label>
          <select
            className="form-select"
            value={config.transformationModel}
            onChange={(e) => setConfig({ ...config, transformationModel: e.target.value as TransformationModelType })}
            disabled={isExecuting}
          >
            <option value="HOMOGRAPHY">Homography (8-DOF Projective Planar)</option>
            <option value="AFFINE">Affine (6-DOF Translation, Rotation, Scale, Shear)</option>
            <option value="SIMILARITY">Similarity (4-DOF Translation, Rotation, Scale)</option>
            <option value="TRANSLATION">Translation (2-DOF Translation Only)</option>
          </select>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Dynamic model selector will automatically stabilize minimal sample sets.
          </div>
        </div>

        {/* Matching Ratio Threshold */}
        <div className="form-group">
          <label className="form-label">
            Lowe's Ratio: <span style={{ color: '#fff', fontFamily: 'var(--font-mono)' }}>{config.ratioThreshold?.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0.50"
            max="0.95"
            step="0.05"
            className="form-input"
            style={{ padding: 0 }}
            value={config.ratioThreshold}
            onChange={(e) => setConfig({ ...config, ratioThreshold: parseFloat(e.target.value) })}
            disabled={isExecuting}
          />
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Default 0.80 for bidirectional mutual consistency.
          </div>
        </div>

        {/* RANSAC Inlier Threshold */}
        <div className="form-group">
          <label className="form-label">
            RANSAC Threshold: <span style={{ color: '#fff', fontFamily: 'var(--font-mono)' }}>{config.ransacThreshold?.toFixed(1)} px</span>
          </label>
          <input
            type="range"
            min="1.0"
            max="10.0"
            step="0.5"
            className="form-input"
            style={{ padding: 0 }}
            value={config.ransacThreshold}
            onChange={(e) => setConfig({ ...config, ransacThreshold: parseFloat(e.target.value) })}
            disabled={isExecuting}
          />
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Maximum reprojection tolerance for inlier consensus.
          </div>
        </div>
      </div>

      {/* Toggles & Execution Action */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
            <input
              type="checkbox"
              checked={config.enableSubpixel}
              onChange={(e) => setConfig({ ...config, enableSubpixel: e.target.checked })}
              disabled={isExecuting}
            />
            <span>2D Parabolic Hessian Sub-Pixel Refinement</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
            <input
              type="checkbox"
              checked={config.enableSpatialFilter}
              onChange={(e) => setConfig({ ...config, enableSpatialFilter: e.target.checked })}
              disabled={isExecuting}
            />
            <span>Spatial Gini (G_k) Dispersion Constraint</span>
          </label>
        </div>

        <button
          className="btn btn-primary"
          onClick={onExecute}
          disabled={!canExecute || isExecuting}
          style={{ minWidth: '220px' }}
        >
          {isExecuting ? (
            <>
              <div className="badge badge-processing" style={{ padding: '0.1rem 0.4rem' }}>Running</div>
              <span>Processing ML Pipeline...</span>
            </>
          ) : (
            <>
              <Play size={16} />
              <span>Execute Registration</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
