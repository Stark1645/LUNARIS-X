import React from 'react';
import { Activity, Compass } from 'lucide-react';
import { RegistrationResponseDTO } from '../../types';

interface ScientificMetricsPanelProps {
  result: RegistrationResponseDTO;
}

export const ScientificMetricsPanel: React.FC<ScientificMetricsPanelProps> = ({ result }) => {
  const m = result.metrics;

  const formatNumber = (val: number | null | undefined, digits: number = 2): string => {
    if (val === null || val === undefined || isNaN(val) || val === Infinity || val === -Infinity) {
      return 'N/A';
    }
    return val.toFixed(digits);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <span className="badge badge-success">SUCCESS</span>;
      case 'DEGRADED':
        return <span className="badge badge-degraded">DEGRADED</span>;
      case 'FAILED':
        return <span className="badge badge-failed">FAILED</span>;
      default:
        return <span className="badge badge-processing">{status}</span>;
    }
  };

  // Matrix formatter
  let formattedMatrix: string = 'N/A';
  try {
    if (result.transformationMatrixJson) {
      const parsed = JSON.parse(result.transformationMatrixJson);
      if (Array.isArray(parsed)) {
        formattedMatrix = parsed.map((row: number[]) =>
          `[ ${row.map((val) => typeof val === 'number' ? val.toFixed(6).padStart(11, ' ') : val).join(', ')} ]`
        ).join('\n');
      }
    }
  } catch (e) {
    formattedMatrix = result.transformationMatrixJson || 'N/A';
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Activity size={18} color="var(--accent-cyan)" />
          <span>Scientific Evaluation Metrics (Measured Values)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-category">{m?.dataCategory || 'SYNTHETIC_BENCHMARK'}</span>
          {getStatusBadge(result.status)}
        </div>
      </div>

      {/* Grid of Key Numerical Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        <div className="metric-box">
          <div className="metric-label">Verified Inliers</div>
          <div className="metric-value" style={{ color: '#34d399' }}>
            {m ? m.inlierMatchesCount : 'N/A'}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            of {m ? m.candidateMatchesCount : 'N/A'} candidate matches
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Inlier Ratio</div>
          <div className="metric-value">
            {formatNumber(m?.inlierRatioPercent, 1)}%
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Consensus match percentage
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Inlier RMSE</div>
          <div className="metric-value" style={{ color: '#38bdf8' }}>
            {formatNumber(m?.rmseInliersPx, 2)} <span style={{ fontSize: '0.8rem' }}>px</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Algebraic fit on verified inliers
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Ground-Truth RMSE</div>
          <div className="metric-value" style={{ color: m?.rmseGroundTruthPx && m.rmseGroundTruthPx <= 5.0 ? '#34d399' : '#fbbf24' }}>
            {formatNumber(m?.rmseGroundTruthPx, 2)} <span style={{ fontSize: '0.8rem' }}>px</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Independent global displacement
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Sub-Pixel Residual</div>
          <div className="metric-value" style={{ color: '#a78bfa' }}>
            {formatNumber(m?.meanSubpixelResidualPx, 3)} <span style={{ fontSize: '0.8rem' }}>px</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Continuous Taylor surface fit
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Spatial Gini (G_k)</div>
          <div className="metric-value" style={{ color: m?.spatialGiniCoefficient && m.spatialGiniCoefficient <= 0.65 ? '#34d399' : '#fbbf24' }}>
            {formatNumber(m?.spatialGiniCoefficient, 2)}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            0.0 = Uniform | 1.0 = Clumped
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Processing Latency</div>
          <div className="metric-value">
            {formatNumber(m?.latencyMs, 0)} <span style={{ fontSize: '0.8rem' }}>ms</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            End-to-end ML pipeline time
          </div>
        </div>
      </div>

      {/* Geometry & Transformation Model Info */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem', alignItems: 'start' }}>
        <div style={{ background: 'var(--bg-surface-2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Transformation Model
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
            {result.selectedTransformationModel || 'HOMOGRAPHY'}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
            Dynamic model selection evaluated sample dispersion (G_k) and correspondence count to maintain planar stability.
          </div>
        </div>

        <div style={{ background: 'var(--bg-surface-2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Transformation Matrix H (3x3)
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Top-Left Coordinate Frame</span>
          </div>
          <pre
            className="font-mono"
            style={{
              background: '#07090e',
              padding: '0.65rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.75rem',
              color: '#38bdf8',
              overflowX: 'auto',
            }}
          >
            {formattedMatrix}
          </pre>
        </div>
      </div>

      {/* Target vs Experimental Diagnostic Threshold Comparison Notice */}
      <div style={{ marginTop: '1rem', padding: '0.65rem 0.85rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(59, 130, 246, 0.2)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <Compass size={14} color="#60a5fa" />
        <div style={{ fontSize: '0.72rem', color: '#93c5fd' }}>
          <strong>Scientific Note:</strong> Master specification target is Gini G_k &lt; 0.35. The internal experimental classification criterion uses Gini G_k &le; 0.65 to detect localized clustering on individual crater rims.
        </div>
      </div>
    </div>
  );
};
