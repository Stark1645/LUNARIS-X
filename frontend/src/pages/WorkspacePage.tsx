import React, { useState } from 'react';
import { ImageUploader } from '../components/upload/ImageUploader';
import { ConfigPanel } from '../components/registration/ConfigPanel';
import { PipelineStepper } from '../components/pipeline/PipelineStepper';
import { ComparisonViewer } from '../components/comparison/ComparisonViewer';
import { ScientificMetricsPanel } from '../components/metrics/ScientificMetricsPanel';
import { ImageMetadata, RegistrationRequest, RegistrationResponseDTO, JobStatus } from '../types';
import { apiService, parseApiError } from '../services/api';
import { AlertCircle, ArrowLeftRight, ShieldCheck } from 'lucide-react';

export const WorkspacePage: React.FC = () => {
  const [sourceImage, setSourceImage] = useState<ImageMetadata | null>(null);
  const [referenceImage, setReferenceImage] = useState<ImageMetadata | null>(null);

  const [config, setConfig] = useState<RegistrationRequest>({
    sourceImageId: 0,
    referenceImageId: 0,
    algorithm: 'Proposed_Method',
    transformationModel: 'HOMOGRAPHY',
    ratioThreshold: 0.80,
    ransacThreshold: 3.0,
    enableSubpixel: true,
    enableSpatialFilter: true,
  });

  const [jobStatus, setJobStatus] = useState<JobStatus | 'IDLE'>('IDLE');
  const [registrationResult, setRegistrationResult] = useState<RegistrationResponseDTO | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSwapRoles = () => {
    const temp = sourceImage;
    setSourceImage(referenceImage);
    setReferenceImage(temp);
  };

  const handleExecuteRegistration = async () => {
    if (!sourceImage || !referenceImage) return;

    setJobStatus('PROCESSING');
    setErrorMessage(null);
    setRegistrationResult(null);

    try {
      const payload: RegistrationRequest = {
        ...config,
        sourceImageId: sourceImage.id,
        referenceImageId: referenceImage.id,
        dataCategory: (sourceImage.dataCategory === 'AUTHENTIC_CH2_PRADAN' || referenceImage.dataCategory === 'AUTHENTIC_CH2_PRADAN')
          ? 'AUTHENTIC_CH2_PRADAN'
          : 'SYNTHETIC_BENCHMARK'
      };

      const result = await apiService.submitRegistration(payload);
      setRegistrationResult(result);
      setJobStatus(result.status);
    } catch (err) {
      setJobStatus('FAILED');
      setErrorMessage(parseApiError(err));
    }
  };

  const isRealPradanPair =
    sourceImage?.dataCategory === 'AUTHENTIC_CH2_PRADAN' ||
    referenceImage?.dataCategory === 'AUTHENTIC_CH2_PRADAN';

  const canExecute = sourceImage !== null && referenceImage !== null && jobStatus !== 'PROCESSING';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner: PRADAN vs Synthetic Indication & Swap Tool */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {isRealPradanPair ? (
            <span
              className="badge"
              style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}
            >
              <ShieldCheck size={14} style={{ display: 'inline', marginRight: '5px' }} />
              REAL ISRO/ISSDC PRADAN MODE ACTIVE
            </span>
          ) : (
            <span
              className="badge"
              style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}
            >
              SYNTHETIC BENCHMARK MODE
            </span>
          )}
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            LUNARIS-X (SIH26166): Chandrayaan-2 Multi-Modal Lunar Image Correspondence and Registration
          </span>
        </div>

        {sourceImage && referenceImage && (
          <button
            className="btn btn-secondary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.78rem' }}
            onClick={handleSwapRoles}
            disabled={jobStatus === 'PROCESSING'}
            title="Swap Moving and Fixed Reference roles"
          >
            <ArrowLeftRight size={14} />
            <span>Swap Source & Reference Roles</span>
          </button>
        )}
      </div>

      {/* Dual Upload Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <ImageUploader
          role="SOURCE"
          label="Source (Moving) Image"
          subLabel="Chandrayaan-2 Acquired Optical Frame to be Geometrically Warped"
          image={sourceImage}
          onImageUploaded={(meta) => setSourceImage(meta)}
          disabled={jobStatus === 'PROCESSING'}
        />

        <ImageUploader
          role="REFERENCE"
          label="Reference (Fixed) Image"
          subLabel="Fixed Lunar Basemap / High-Resolution Orthorectified Target"
          image={referenceImage}
          onImageUploaded={(meta) => setReferenceImage(meta)}
          disabled={jobStatus === 'PROCESSING'}
        />
      </div>

      {/* Middle Section: Configuration & Execution Panel */}
      <ConfigPanel
        config={config}
        setConfig={setConfig}
        onExecute={handleExecuteRegistration}
        isExecuting={jobStatus === 'PROCESSING'}
        canExecute={canExecute}
      />

      {/* Pipeline Stepper */}
      <PipelineStepper status={jobStatus} />

      {/* Error Alert */}
      {errorMessage && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1.25rem',
            color: '#f87171',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <AlertCircle size={18} />
          <div>
            <strong>Registration Execution Error:</strong> {errorMessage}
          </div>
        </div>
      )}

      {/* Results Section */}
      {registrationResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <ComparisonViewer
            result={registrationResult}
            sourcePreviewUrl={sourceImage?.previewUrl}
            referencePreviewUrl={referenceImage?.previewUrl}
          />

          <ScientificMetricsPanel result={registrationResult} />
        </div>
      )}
    </div>
  );
};
