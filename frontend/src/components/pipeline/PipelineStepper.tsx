import React from 'react';
import { Check, Loader2, AlertCircle, Circle } from 'lucide-react';
import { JobStatus } from '../../types';

interface PipelineStepperProps {
  status: JobStatus | 'IDLE';
}

const STAGES = [
  { id: 1, name: 'Validation & Masking' },
  { id: 2, name: 'Radiometric Stretch' },
  { id: 3, name: 'Condition Analysis' },
  { id: 4, name: 'Multi-Scale Pyramid' },
  { id: 5, name: 'Structural Detection' },
  { id: 6, name: 'k-NN Ratio Match' },
  { id: 7, name: 'Spatial RANSAC' },
  { id: 8, name: 'Inlier/Outlier Split' },
  { id: 9, name: 'Gini Distribution' },
  { id: 10, name: 'Dynamic Model Fit' },
  { id: 11, name: 'Sub-Pixel Hessian' },
  { id: 12, name: 'Backward Warping' },
  { id: 13, name: 'Scientific Metrics' },
];

export const PipelineStepper: React.FC<PipelineStepperProps> = ({ status }) => {
  return (
    <div className="card" style={{ padding: '0.85rem 1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Registration Engine Execution Pipeline (14 Logical Stages)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {status === 'PROCESSING' && (
            <span className="badge badge-processing">
              <Loader2 size={12} className="spin" />
              <span>Processing ML Microservice</span>
            </span>
          )}
          {status === 'SUCCESS' && (
            <span className="badge badge-success">
              <Check size={12} />
              <span>Pipeline Complete</span>
            </span>
          )}
          {status === 'DEGRADED' && (
            <span className="badge badge-degraded">
              <AlertCircle size={12} />
              <span>Completed with Warnings (Degraded)</span>
            </span>
          )}
          {status === 'FAILED' && (
            <span className="badge badge-failed">
              <AlertCircle size={12} />
              <span>Pipeline Failed</span>
            </span>
          )}
        </div>
      </div>

      <div className="pipeline-track">
        {STAGES.map((stage, idx) => {
          let nodeClass = 'pipeline-node';
          let icon = <Circle size={12} color="var(--text-muted)" />;

          if (status === 'SUCCESS' || status === 'DEGRADED') {
            nodeClass += ' completed';
            icon = <Check size={12} color="#34d399" />;
          } else if (status === 'PROCESSING') {
            if (idx <= 7) {
              nodeClass += ' active';
              icon = <Loader2 size={12} color="#38bdf8" className="spin" />;
            }
          } else if (status === 'FAILED') {
            nodeClass += ' failed';
            icon = <AlertCircle size={12} color="#f87171" />;
          }

          return (
            <div key={stage.id} className={nodeClass}>
              {icon}
              <span>{stage.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
