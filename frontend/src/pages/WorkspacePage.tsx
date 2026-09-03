import React, { useState } from 'react';
import { ImageUploader } from '../components/upload/ImageUploader';
import { ConfigPanel } from '../components/registration/ConfigPanel';
import { PipelineStepper } from '../components/pipeline/PipelineStepper';
import { ComparisonViewer } from '../components/comparison/ComparisonViewer';
import { ScientificMetricsPanel } from '../components/metrics/ScientificMetricsPanel';
import { ImageMetadata, RegistrationRequest, RegistrationResponseDTO, JobStatus } from '../types';
import { apiService, parseApiError } from '../services/api';
import { AlertCircle } from 'lucide-react';

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
      };

      const result = await apiService.submitRegistration(payload);
      setRegistrationResult(result);
      setJobStatus(result.status);
    } catch (err) {
      setJobStatus('FAILED');
      setErrorMessage(parseApiError(err));
    }
  };

  const canExecute = sourceImage !== null && referenceImage !== null && jobStatus !== 'PROCESSING';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Section: Dual Upload Cards */}
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
