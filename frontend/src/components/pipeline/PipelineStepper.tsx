import React from 'react';
import { Check, Loader2, AlertCircle, Circle } from 'lucide-react';
import { JobStatus } from '../../types';

interface PipelineStepperProps {
  status: JobStatus | 'IDLE';
  segment?: 'FIRST_HALF' | 'SECOND_HALF' | 'ALL';
}

const ALL_STAGES = [
  { id: 1, name: 'Validation', fullName: 'Input Frame Telemetry Validation' },
  { id: 2, name: 'Radiometric Stretch', fullName: 'Radiometric Intensity Equalization' },
  { id: 3, name: 'Scale Pyramid', fullName: 'Multi-scale Gaussian Feature Pyramid' },
  { id: 4, name: 'Phase Congruency', fullName: 'Frequency Domain Phase Congruency Saliency' },
  { id: 5, name: 'Feature Matching', fullName: 'Sub-Pixel Feature Descriptor Matching' },
  { id: 6, name: 'Spatial RANSAC', fullName: 'Spatial Dispersion RANSAC Rejection' },
  { id: 7, name: 'Inlier Consensus', fullName: 'Geometric Inlier Consensus Estimation' },
  { id: 8, name: 'Hessian Refinement', fullName: 'Sub-Pixel Parabolic Hessian Refinement' },
  { id: 9, name: 'Backward Warping', fullName: 'Projective Backward Image Warping' },
  { id: 10, name: 'Scientific Metrics', fullName: 'Scientific RMSE & Spatial Gk Dispersion' },
];

export const PipelineStepper: React.FC<PipelineStepperProps> = ({ status, segment = 'ALL' }) => {
  const isSegmented = segment === 'FIRST_HALF' || segment === 'SECOND_HALF';

  const stages = segment === 'FIRST_HALF'
    ? ALL_STAGES.slice(0, 5)
    : segment === 'SECOND_HALF'
    ? ALL_STAGES.slice(5, 10)
    : ALL_STAGES;

  const title = segment === 'FIRST_HALF'
    ? 'Extraction Pipeline'
    : segment === 'SECOND_HALF'
    ? 'Geometric Consensus'
    : 'Execution Stages';

  const subtitle = segment === 'FIRST_HALF'
    ? 'Stages 1–5 • Detection'
    : segment === 'SECOND_HALF'
    ? 'Stages 6–10 • Warp & QA'
    : '(10-Stage Pipeline)';

  const isComplete = status === 'SUCCESS' || status === 'DEGRADED';

  if (isSegmented) {
    return (
      <div className="pipeline-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {title}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              {subtitle}
            </div>
          </div>

          <div>
            {status === 'IDLE' && (
              <span className="badge badge-neutral" style={{ fontSize: '0.64rem', padding: '0.12rem 0.4rem' }}>
                Standby
              </span>
            )}
            {status === 'PROCESSING' && (
              <span className="badge badge-processing" style={{ fontSize: '0.64rem', padding: '0.12rem 0.4rem' }}>
                <Loader2 size={10} className="spin" />
                <span>Running</span>
              </span>
            )}
            {isComplete && (
              <span className="badge badge-success" style={{ fontSize: '0.64rem', padding: '0.12rem 0.4rem' }}>
                <Check size={10} />
                <span>Ready</span>
              </span>
            )}
            {status === 'FAILED' && (
              <span className="badge badge-failed" style={{ fontSize: '0.64rem', padding: '0.12rem 0.4rem' }}>
                <AlertCircle size={10} />
                <span>Halted</span>
              </span>
            )}
          </div>
        </div>

        {/* Vertical Rail for 5 Stages */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
          {stages.map((stage) => {
            let itemClass = 'pipeline-rail-item pending';
            let icon = <Circle size={8} style={{ opacity: 0.4 }} />;

            if (isComplete) {
              itemClass = 'pipeline-rail-item completed';
              icon = <Check size={11} style={{ color: '#34d399' }} />;
            } else if (status === 'PROCESSING') {
              if (segment === 'FIRST_HALF' || (segment === 'SECOND_HALF' && stage.id <= 7)) {
                itemClass = 'pipeline-rail-item active';
                icon = <Loader2 size={10} className="spin" style={{ color: '#60a5fa' }} />;
              }
            }

            return (
              <div
                key={stage.id}
                className={itemClass}
                title={`Stage ${stage.id}: ${stage.fullName}`}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', minWidth: 0 }}>
                  {icon}
                  <span style={{ fontSize: '0.72rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {stage.id}. {stage.name}
                  </span>
                </div>
                <span style={{ fontSize: '0.65rem', color: isComplete ? '#34d399' : 'var(--text-muted)', flexShrink: 0 }}>
                  {isComplete ? 'OK' : status === 'PROCESSING' ? '...' : 'Queue'}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Fallback / Standard 10-stage horizontal layout
  return (
    <div className="pipeline-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Execution Stages
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            (10-Stage Deterministic Alignment Pipeline)
          </span>
        </div>

        <div>
          {status === 'IDLE' && (
            <span className="badge badge-neutral" style={{ fontSize: '0.68rem' }}>
              Standby
            </span>
          )}
          {status === 'PROCESSING' && (
            <span className="badge badge-processing" style={{ fontSize: '0.68rem' }}>
              <Loader2 size={11} className="spin" />
              <span>Processing ML Pipeline...</span>
            </span>
          )}
          {isComplete && (
            <span className="badge badge-success" style={{ fontSize: '0.68rem' }}>
              <Check size={11} />
              <span>All 10 Stages Complete</span>
            </span>
          )}
          {status === 'FAILED' && (
            <span className="badge badge-failed" style={{ fontSize: '0.68rem' }}>
              <AlertCircle size={11} />
              <span>Pipeline Halted</span>
            </span>
          )}
        </div>
      </div>

      <div className="pipeline-stages-grid">
        {ALL_STAGES.map((stage) => {
          let chipClass = 'pipeline-stage-chip pending';
          let icon = <Circle size={8} style={{ opacity: 0.4 }} />;

          if (isComplete) {
            chipClass = 'pipeline-stage-chip completed';
            icon = <Check size={11} style={{ color: '#34d399' }} />;
          } else if (status === 'PROCESSING') {
            if (stage.id <= 5) {
              chipClass = 'pipeline-stage-chip active';
              icon = <Loader2 size={11} className="spin" style={{ color: '#60a5fa' }} />;
            }
          }

          return (
            <div
              key={stage.id}
              className={chipClass}
              title={`Stage ${stage.id}: ${stage.fullName}`}
            >
              {icon}
              <span>{stage.id}. {stage.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
