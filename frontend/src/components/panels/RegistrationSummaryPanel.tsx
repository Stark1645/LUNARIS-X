import React from 'react';
import {
  CheckCircle2, AlertTriangle, XCircle, Clock, Target,
  Crosshair, BarChart2, Zap, Layers, GitMerge, TrendingUp, Info,
} from 'lucide-react';
import { RegistrationResponseDTO } from '../../types';

interface RegistrationSummaryPanelProps {
  result: RegistrationResponseDTO | null;
}

function fmt(val: number | null | undefined, decimals = 3, unit = ''): string {
  if (val === null || val === undefined) return '—';
  return `${val.toFixed(decimals)}${unit ? ' ' + unit : ''}`;
}

/** Intelligent quality assessment based on metric thresholds used in ISRO evaluation */
function assess(rmse: number | null, subpx: number | null, inlierRatio: number | null): {
  level: 'excellent' | 'good' | 'acceptable' | 'poor';
  color: string;
  label: string;
  note: string;
} {
  const r = rmse ?? 999;
  const s = subpx ?? 0;
  const ir = inlierRatio ?? 0;

  if (r <= 0.5 && s >= 80 && ir >= 50)
    return { level: 'excellent', color: '#34d399', label: 'Excellent', note: 'Sub-pixel alignment verified — publication quality' };
  if (r <= 1.0 && s >= 50 && ir >= 35)
    return { level: 'good', color: '#60a5fa', label: 'Good', note: 'Reliable alignment — acceptable for mapping use' };
  if (r <= 2.0 && ir >= 20)
    return { level: 'acceptable', color: '#fbbf24', label: 'Acceptable', note: 'Moderate quality — RMSE exceeds 1 px, consider RANSAC tuning' };
  return { level: 'poor', color: '#f87171', label: 'Poor', note: 'High residuals or low inlier count — check image overlap or parameters' };
}

function qColor(val: number | null | undefined, goodBelow: number, warnBelow: number, lowerIsBetter = true): string {
  if (val === null || val === undefined) return 'var(--text-muted)';
  if (lowerIsBetter) {
    if (val <= goodBelow) return '#34d399';
    if (val <= warnBelow) return '#fbbf24';
    return '#f87171';
  } else {
    if (val >= goodBelow) return '#34d399';
    if (val >= warnBelow) return '#fbbf24';
    return '#f87171';
  }
}

function StatusBadge({ status }: { status: string }) {
  const cfg =
    status === 'SUCCESS'    ? { icon: <CheckCircle2 size={12} />, color: '#34d399', bg: 'rgba(52,211,153,0.12)',  label: 'Aligned Successfully' } :
    status === 'DEGRADED'   ? { icon: <AlertTriangle size={12} />, color: '#fbbf24', bg: 'rgba(251,191,36,0.12)', label: 'Degraded Quality' } :
    status === 'FAILED'     ? { icon: <XCircle size={12} />,       color: '#f87171', bg: 'rgba(248,113,113,0.12)', label: 'Registration Failed' } :
    status === 'PROCESSING' ? { icon: <Zap size={12} />,           color: '#60a5fa', bg: 'rgba(96,165,250,0.12)', label: 'Processing...' } :
                              { icon: <Clock size={12} />,          color: 'var(--text-muted)', bg: 'var(--bg-surface-elevated)', label: 'Pending' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '0.35rem',
      padding: '0.2rem 0.55rem',
      background: cfg.bg, border: `1px solid ${cfg.color}40`,
      borderRadius: '99px', fontSize: '0.67rem', fontWeight: 600, color: cfg.color,
    }}>
      {cfg.icon} {cfg.label}
    </div>
  );
}

export const RegistrationSummaryPanel: React.FC<RegistrationSummaryPanelProps> = ({ result }) => {
  if (!result) return null;

  const m = result.metrics;
  const inlierRatio = m?.inlierRatioPercent ?? null;
  const rmse = m?.rmseInliersPx ?? null;
  const subpixelRate = m?.subpixelAccuracyRate05px ?? null;
  const candidates = m?.candidateMatchesCount ?? 0;
  const inliers = m?.inlierMatchesCount ?? 0;
  const latencyMs = m?.latencyMs ?? null;
  const outliers = candidates - inliers;

  const quality = assess(rmse, subpixelRate, inlierRatio);

  // Parse homography matrix
  let matrixRows: number[][] | null = null;
  try {
    if (result.transformationMatrixJson) {
      const raw = JSON.parse(result.transformationMatrixJson);
      if (Array.isArray(raw) && Array.isArray(raw[0])) matrixRows = raw;
    }
  } catch { /* ignore */ }

  // Compute homography det and condition number for insight
  let detH: number | null = null;
  let condNote: string | null = null;
  if (matrixRows && matrixRows.length === 3) {
    const h = matrixRows;
    detH = h[0][0]*(h[1][1]*h[2][2]-h[1][2]*h[2][1])
          -h[0][1]*(h[1][0]*h[2][2]-h[1][2]*h[2][0])
          +h[0][2]*(h[1][0]*h[2][1]-h[1][1]*h[2][0]);
    if (Math.abs(detH - 1) < 0.05) condNote = 'Near-isometric — minimal distortion';
    else if (Math.abs(detH) > 0.5 && Math.abs(detH) < 2.0) condNote = 'Well-conditioned transform';
    else condNote = 'Significant perspective distortion detected';
  }

  return (
    <div className="card">
      <div className="card-header" style={{ alignItems: 'center', gap: '0.4rem' }}>
        <div className="card-title" style={{ fontSize: '0.8rem', whiteSpace: 'nowrap', minWidth: 0 }}>
          <Target size={14} style={{ color: 'var(--accent-blue)', flexShrink: 0 }} />
          <span>Registration Results</span>
        </div>
        <StatusBadge status={result.status} />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', padding: '0.6rem' }}>

        {/* Overall quality assessment — the key intelligence */}
        <div style={{
          padding: '0.5rem 0.65rem',
          background: `${quality.color}10`,
          border: `1px solid ${quality.color}35`,
          borderRadius: 'var(--radius-xs)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Overall Quality
            </span>
            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: quality.color }}>
              {quality.label}
            </span>
          </div>
          <div style={{ fontSize: '0.67rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '0.3rem' }}>
            <Info size={10} style={{ color: quality.color, marginTop: 1, flexShrink: 0 }} />
            <span>{quality.note}</span>
          </div>
        </div>

        {/* Algorithm + model row */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem',
        }}>
          {[
            { label: 'Algorithm', value: result.algorithm === 'Proposed_Method' ? 'LUNARIS-X Proposed' : result.algorithm.replace(/_/g, ' '), color: '#60a5fa' },
            { label: 'Transform', value: result.selectedTransformationModel ?? 'HOMOGRAPHY', color: 'var(--text-primary)' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              padding: '0.4rem 0.55rem',
              background: 'var(--bg-surface-elevated)',
              borderRadius: 'var(--radius-xs)',
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>{label}</div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color }}>{value}</div>
            </div>
          ))}
        </div>

        {/* Inlier bar */}
        <div style={{
          padding: '0.5rem 0.65rem',
          background: 'var(--bg-surface-elevated)',
          borderRadius: 'var(--radius-xs)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.67rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <GitMerge size={10} /> Inlier / Total Matches
            </span>
            <span style={{ fontSize: '0.78rem', fontWeight: 700, color: qColor(inlierRatio, 50, 30, false) }}>
              {inliers} / {candidates}
            </span>
          </div>
          <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden', display: 'flex' }}>
            <div style={{
              width: `${Math.min((inliers / Math.max(candidates, 1)) * 100, 100)}%`,
              background: 'linear-gradient(90deg, #38bdf8, #34d399)',
              transition: 'width 0.8s ease',
            }} />
            <div style={{
              width: `${Math.min((outliers / Math.max(candidates, 1)) * 100, 100)}%`,
              background: 'rgba(248,113,113,0.35)',
            }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
            <span style={{ fontSize: '0.61rem', color: '#f87171' }}>{outliers} outliers rejected</span>
            <span style={{ fontSize: '0.66rem', fontWeight: 700, color: qColor(inlierRatio, 50, 30, false) }}>
              {inlierRatio !== null ? `${inlierRatio.toFixed(1)}%` : '—'} inlier ratio
            </span>
          </div>
        </div>

        {/* Accuracy metrics */}
        <div style={{
          display: 'flex', flexDirection: 'column', gap: '0.4rem',
          padding: '0.5rem 0.65rem',
          background: 'var(--bg-surface-elevated)',
          borderRadius: 'var(--radius-xs)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '0.61rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Accuracy
          </div>

          {[
            {
              icon: <Crosshair size={11} />,
              label: 'RMSE (Inliers)',
              value: fmt(rmse, 3, 'px'),
              color: qColor(rmse, 0.5, 1.0),
              bar: rmse !== null ? Math.max(0, 1 - rmse / 3) : undefined,
              barColor: qColor(rmse, 0.5, 1.0),
              hint: rmse !== null ? (rmse <= 0.5 ? 'Sub-pixel ✓' : rmse <= 1.0 ? 'Near sub-pixel' : 'Above 1px — review params') : '',
            },
            {
              icon: <TrendingUp size={11} />,
              label: 'Sub-pixel Rate ≤0.5px',
              value: subpixelRate !== null ? `${subpixelRate.toFixed(1)}%` : '—',
              color: qColor(subpixelRate, 80, 50, false),
              bar: subpixelRate !== null ? subpixelRate / 100 : undefined,
              barColor: qColor(subpixelRate, 80, 50, false),
              hint: '',
            },
            {
              icon: <BarChart2 size={11} />,
              label: 'Mean Residual',
              value: fmt(m?.meanSubpixelResidualPx, 3, 'px'),
              color: qColor(m?.meanSubpixelResidualPx, 0.4, 0.8),
              bar: undefined,
              barColor: undefined,
              hint: '',
            },
            {
              icon: <Clock size={11} />,
              label: 'Processing Time',
              value: latencyMs !== null
                ? latencyMs >= 1000 ? `${(latencyMs / 1000).toFixed(2)} s` : `${latencyMs.toFixed(0)} ms`
                : '—',
              color: 'var(--text-primary)',
              bar: undefined,
              barColor: undefined,
              hint: '',
            },
          ].map(({ icon, label, value, color, bar, barColor, hint }) => (
            <div key={label}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{icon}</span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{label}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  {hint && <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{hint}</span>}
                  <span style={{ fontSize: '0.76rem', fontWeight: 700, color }}>{value}</span>
                </div>
              </div>
              {bar !== undefined && (
                <div style={{ height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden', marginTop: '0.18rem' }}>
                  <div style={{ width: `${Math.min(bar * 100, 100)}%`, height: '100%', background: barColor, borderRadius: 2, transition: 'width 0.6s ease' }} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Homography matrix + det insight */}
        {matrixRows && matrixRows.length >= 2 && (
          <div style={{
            padding: '0.5rem 0.65rem',
            background: 'var(--bg-surface-elevated)',
            borderRadius: 'var(--radius-xs)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.61rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Layers size={10} /> Transformation Matrix H
              {detH !== null && (
                <span style={{ marginLeft: 'auto', fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>
                  det(H) = {detH.toFixed(4)}
                </span>
              )}
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.64rem', lineHeight: 1.75, color: 'var(--text-secondary)', overflowX: 'auto' }}>
              {matrixRows.map((row, ri) => (
                <div key={ri} style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: 'var(--text-muted)', userSelect: 'none' }}>[</span>
                  {row.map((v, ci) => (
                    <span key={ci} style={{ color: Math.abs(v) > 0.001 ? 'var(--text-primary)' : 'var(--text-muted)', minWidth: '6ch', textAlign: 'right' }}>
                      {v.toFixed(5)}
                    </span>
                  ))}
                  <span style={{ color: 'var(--text-muted)', userSelect: 'none' }}>]</span>
                </div>
              ))}
            </div>
            {condNote && (
              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Info size={9} /> {condNote}
              </div>
            )}
          </div>
        )}

        {/* Spatial quality pill */}
        {m?.spatialQualityStatus && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            padding: '0.3rem 0.65rem',
            background: m.spatialQualityStatus === 'GOOD' ? 'rgba(52,211,153,0.07)' : m.spatialQualityStatus === 'ACCEPTABLE' ? 'rgba(251,191,36,0.07)' : 'rgba(248,113,113,0.07)',
            border: '1px solid ' + (m.spatialQualityStatus === 'GOOD' ? 'rgba(52,211,153,0.2)' : m.spatialQualityStatus === 'ACCEPTABLE' ? 'rgba(251,191,36,0.2)' : 'rgba(248,113,113,0.2)'),
            borderRadius: 'var(--radius-xs)', fontSize: '0.67rem',
          }}>
            <CheckCircle2 size={11} style={{ color: m.spatialQualityStatus === 'GOOD' ? '#34d399' : m.spatialQualityStatus === 'ACCEPTABLE' ? '#fbbf24' : '#f87171', flexShrink: 0 }} />
            <span style={{ color: 'var(--text-secondary)' }}>
              Spatial coverage: <strong style={{ color: m.spatialQualityStatus === 'GOOD' ? '#34d399' : m.spatialQualityStatus === 'ACCEPTABLE' ? '#fbbf24' : '#f87171' }}>
                {m.spatialQualityStatus}
              </strong>
            </span>
            {m.spatialGiniCoefficient != null && (
              <span style={{ marginLeft: 'auto', fontSize: '0.61rem', color: 'var(--text-muted)' }}>
                Gini: {m.spatialGiniCoefficient.toFixed(3)}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
