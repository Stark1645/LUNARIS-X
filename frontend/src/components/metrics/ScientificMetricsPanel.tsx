import React from 'react';
import { Activity, Compass, ShieldCheck, MapPin, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';
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

  const getCategoryBadge = (category?: string) => {
    if (category === 'AUTHENTIC_CH2_PRADAN') {
      return (
        <span
          className="badge"
          style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}
        >
          <ShieldCheck size={12} style={{ display: 'inline', marginRight: '4px' }} />
          AUTHENTIC_CH2_PRADAN
        </span>
      );
    }
    return (
      <span
        className="badge"
        style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}
      >
        SYNTHETIC_BENCHMARK
      </span>
    );
  };

  const getSpatialQualityBadge = (quality?: string) => {
    if (quality === 'GOOD') {
      return <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>GOOD DISTRIBUTION</span>;
    } else if (quality === 'ACCEPTABLE') {
      return <span className="badge badge-degraded" style={{ fontSize: '0.7rem' }}>ACCEPTABLE</span>;
    }
    return <span className="badge badge-failed" style={{ fontSize: '0.7rem' }}>POOR / CLUSTERED</span>;
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

  const isGroundTruthAvailable = m?.rmseGroundTruthPx !== null && m?.rmseGroundTruthPx !== undefined;

  return (
    <div className="card">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
        <div className="card-title">
          <Activity size={18} color="var(--accent-cyan)" />
          <span>Scientific Evaluation Metrics (Measured Values)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          {getCategoryBadge(result.dataCategory || m?.dataCategory)}
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
          <div className="metric-label">Reprojection RMSE</div>
          <div className="metric-value" style={{ color: '#38bdf8' }}>
            {formatNumber(m?.rmseInliersPx, 2)} <span style={{ fontSize: '0.8rem' }}>px</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Residual fit on verified inliers
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Ground-Truth RMSE</div>
          {isGroundTruthAvailable ? (
            <>
              <div className="metric-value" style={{ color: m.rmseGroundTruthPx! <= 5.0 ? '#34d399' : '#fbbf24' }}>
                {formatNumber(m.rmseGroundTruthPx, 2)} <span style={{ fontSize: '0.8rem' }}>px</span>
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                Analytical baseline error
              </div>
            </>
          ) : (
            <>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#94a3b8', marginTop: '0.4rem', marginBottom: '0.2rem' }}>
                GROUND TRUTH: NOT AVAILABLE (<span>N/A</span>)
              </div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                Real flight data (evaluated via inlier consistency)
              </div>
            </>
          )}
        </div>

        <div className="metric-box">
          <div className="metric-label">Sub-Pixel (&lt; 0.5 px)</div>
          <div className="metric-value" style={{ color: m && (m.subpixelAccuracyRate05px ?? 0) >= 70 ? '#34d399' : '#fbbf24' }}>
            {formatNumber(m?.subpixelAccuracyRate05px, 1)}%
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Residual magnitude &lt; 0.5 px
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-label">Spatial Dispersion G_k</div>
          <div className="metric-value" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>{formatNumber(m?.spatialGiniCoefficient, 3)}</span>
            {getSpatialQualityBadge(m?.spatialQualityStatus)}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Gini coefficient (0 = uniform, 1 = clumped)
          </div>
        </div>
      </div>

      {/* Residual Details and Provenance */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {/* Estimated Transformation Model */}
        <div style={{ background: 'rgba(15, 23, 42, 0.4)', borderRadius: '6px', padding: '0.85rem', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Compass size={14} />
            <span>ESTIMATED TRANSFORMATION MODEL: </span>
            <span style={{ color: '#38bdf8' }}>{result.selectedTransformationModel}</span>
          </div>
          <pre
            style={{
              fontFamily: 'monospace',
              fontSize: '0.72rem',
              color: '#38bdf8',
              background: 'rgba(0, 0, 0, 0.5)',
              padding: '0.6rem',
              borderRadius: '4px',
              overflowX: 'auto',
              lineHeight: 1.4,
              margin: 0
            }}
          >
            {formattedMatrix}
          </pre>
        </div>

        {/* Residual Statistics and Latency */}
        <div style={{ background: 'rgba(15, 23, 42, 0.4)', borderRadius: '6px', padding: '0.85rem', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Info size={14} />
            <span>ACCURACY RESIDUALS & RUNTIME</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.78rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Mean Sub-Pixel Residual: </span>
              <strong style={{ color: '#e2e8f0' }}>{formatNumber(m?.meanSubpixelResidualPx, 3)} px</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Total Pipeline Latency: </span>
              <strong style={{ color: '#e2e8f0' }}>{formatNumber(m?.latencyMs, 1)} ms</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Algorithm: </span>
              <strong style={{ color: '#38bdf8' }}>{result.algorithm}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Status: </span>
              <strong style={{ color: result.status === 'SUCCESS' ? '#34d399' : '#f87171' }}>{result.status}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
