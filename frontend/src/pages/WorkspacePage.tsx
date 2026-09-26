import React, { useState } from 'react';
import { ImageUploader } from '../components/upload/ImageUploader';
import { ConfigPanel } from '../components/registration/ConfigPanel';
import { PipelineStepper } from '../components/pipeline/PipelineStepper';
import { ComparisonViewer } from '../components/comparison/ComparisonViewer';
import { ScientificMetricsPanel } from '../components/metrics/ScientificMetricsPanel';
import { FeatureTelemetryPanel } from '../components/registration/FeatureTelemetryPanel';
import { TransformationExportPanel } from '../components/registration/TransformationExportPanel';
import { PointMatchingVisualizer } from '../components/comparison/PointMatchingVisualizer';
import { ImageSensorInfoPanel } from '../components/panels/ImageSensorInfoPanel';
import { RegistrationSummaryPanel } from '../components/panels/RegistrationSummaryPanel';
import { SubpixelResidualsPanel } from '../components/metrics/SubpixelResidualsPanel';

import { ImageMetadata, RegistrationRequest, RegistrationResponseDTO, JobStatus } from '../types';
import { apiService, parseApiError } from '../services/api';
import { AlertCircle, ArrowLeftRight, Sparkles, Loader2, Image as ImageIcon, Play } from 'lucide-react';

interface PresetPair {
  id: string;
  name: string;
  sourceUrl: string;
  referenceUrl: string;
  sourceSensor: string;
  refSensor: string;
  sourceGsd: number;
  refGsd: number;
  sourceName: string;
  refName: string;
  solarAzimuth?: number;
  sunElevation?: number;
}

const PRESET_PAIRS: PresetPair[] = [
  {
    id: 'pair_01',
    name: 'Pair 01: Baseline Crater',
    sourceUrl: '/samples/pair_01/source.png',
    referenceUrl: '/samples/pair_01/reference.png',
    sourceSensor: 'TMC-2',
    refSensor: 'TMC-2',
    sourceGsd: 5.0,
    refGsd: 5.0,
    sourceName: 'ch2_tmc_pair01_source.png',
    refName: 'ch2_tmc_pair01_reference.png',
    solarAzimuth: 45.0,
    sunElevation: 50.0,
  },
  {
    id: 'pair_03',
    name: 'Pair 03: Shadow Flip',
    sourceUrl: '/samples/pair_03/source.png',
    referenceUrl: '/samples/pair_03/reference.png',
    sourceSensor: 'TMC-2',
    refSensor: 'TMC-2',
    sourceGsd: 5.0,
    refGsd: 5.0,
    sourceName: 'ch2_tmc_pair03_shadow_src.png',
    refName: 'ch2_tmc_pair03_shadow_ref.png',
    solarAzimuth: 30.0,
    sunElevation: 25.0,
  },
  {
    id: 'pair_07',
    name: 'Pair 07: Cross-Modal SWIR',
    sourceUrl: '/samples/pair_07/source.png',
    referenceUrl: '/samples/pair_07/reference.png',
    sourceSensor: 'IIRS',
    refSensor: 'TMC-2',
    sourceGsd: 5.0,
    refGsd: 5.0,
    sourceName: 'ch2_iirs_pair07_src.png',
    refName: 'ch2_tmc_pair07_ref.png',
    solarAzimuth: 62.5,
    sunElevation: 44.0,
  },
  {
    id: 'pair_08',
    name: 'Pair 08: Maria Plain',
    sourceUrl: '/samples/pair_08/source.png',
    referenceUrl: '/samples/pair_08/reference.png',
    sourceSensor: 'TMC-2',
    refSensor: 'TMC-2',
    sourceGsd: 5.0,
    refGsd: 5.0,
    sourceName: 'ch2_tmc_pair08_maria_src.png',
    refName: 'ch2_tmc_pair08_maria_ref.png',
    solarAzimuth: 88.0,
    sunElevation: 55.0,
  },
];

export const WorkspacePage: React.FC = () => {
  const [sourceImage, setSourceImage] = useState<ImageMetadata | null>(null);
  const [referenceImage, setReferenceImage] = useState<ImageMetadata | null>(null);
  const [activePreset, setActivePreset] = useState<PresetPair | null>(null);
  const [loadingPreset, setLoadingPreset] = useState<string | null>(null);

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

  const handleLoadPreset = async (preset: PresetPair) => {
    setLoadingPreset(preset.id);
    setErrorMessage(null);

    try {
      const [srcResp, refResp] = await Promise.all([
        fetch(preset.sourceUrl),
        fetch(preset.referenceUrl),
      ]);

      if (!srcResp.ok || !refResp.ok) {
        throw new Error(`Failed to load preset images: HTTP ${srcResp.status}/${refResp.status}`);
      }

      const [srcBlob, refBlob] = await Promise.all([
        srcResp.blob(),
        refResp.blob(),
      ]);

      const srcFile = new File([srcBlob], preset.sourceName, { type: 'image/png' });
      const refFile = new File([refBlob], preset.refName, { type: 'image/png' });

      const [srcMeta, refMeta] = await Promise.all([
        apiService.uploadImage(srcFile, preset.sourceSensor, 'CHANDRAYAAN-2', preset.sourceGsd, 'SYNTHETIC_BENCHMARK'),
        apiService.uploadImage(refFile, preset.refSensor, 'CHANDRAYAAN-2', preset.refGsd, 'SYNTHETIC_BENCHMARK'),
      ]);

      srcMeta.previewUrl = URL.createObjectURL(srcBlob);
      refMeta.previewUrl = URL.createObjectURL(refBlob);

      setSourceImage(srcMeta);
      setReferenceImage(refMeta);
      setActivePreset(preset);
    } catch (err) {
      setErrorMessage(parseApiError(err));
    } finally {
      setLoadingPreset(null);
    }
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

  const canExecute = sourceImage !== null && referenceImage !== null && jobStatus !== 'PROCESSING';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* Sleek Minimalist Studio Toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem',
          paddingBottom: '0.5rem',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div>
          <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            Planetary Registration Studio
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
            Chandrayaan-2 sub-pixel multi-modal alignment
          </div>
        </div>

        {/* Quick Sample Presets & Tools */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Sparkles size={12} style={{ color: 'var(--accent-blue)' }} />
            <span>Samples:</span>
          </span>

          {PRESET_PAIRS.map((p) => (
            <button
              key={p.id}
              className="btn btn-secondary"
              style={{
                padding: '0.25rem 0.6rem',
                fontSize: '0.74rem',
                borderRadius: '9999px',
                background: loadingPreset === p.id ? 'var(--bg-surface-subtle)' : undefined,
              }}
              onClick={() => handleLoadPreset(p)}
              disabled={loadingPreset !== null || jobStatus === 'PROCESSING'}
            >
              {loadingPreset === p.id && <Loader2 size={11} className="spin" />}
              <span>{p.name}</span>
            </button>
          ))}

          {sourceImage && referenceImage && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.74rem', borderRadius: '9999px', marginLeft: '0.25rem' }}
              onClick={handleSwapRoles}
              disabled={jobStatus === 'PROCESSING'}
              title="Swap Moving and Fixed Reference roles"
            >
              <ArrowLeftRight size={12} />
              <span>Swap Roles</span>
            </button>
          )}

          {/* Primary Top Run Registration Action */}
          <button
            className="btn btn-primary"
            onClick={handleExecuteRegistration}
            disabled={!canExecute}
            style={{
              padding: '0.35rem 0.95rem',
              fontSize: '0.78rem',
              fontWeight: 600,
              borderRadius: '9999px',
              marginLeft: '0.35rem',
            }}
          >
            {jobStatus === 'PROCESSING' ? (
              <>
                <Loader2 size={12} className="spin" />
                <span>Aligning...</span>
              </>
            ) : (
              <>
                <Play size={12} fill="currentColor" />
                <span>Run Registration</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div
          style={{
            background: 'var(--accent-rose-subtle)',
            border: '1px solid rgba(244, 63, 94, 0.25)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.65rem 1rem',
            color: '#f87171',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.82rem',
          }}
        >
          <AlertCircle size={15} />
          <div>
            <strong>Registration Error:</strong> {errorMessage}
          </div>
        </div>
      )}

      {/* ============================================================
          3-COLUMN PLANETARY REGISTRATION CONSOLE
          Left: Moving Source & Stages 1–5
          Center: Viewport Preview / Comparison, Parameters, & Metrics
          Right: Fixed Reference & Stages 6–10
          ============================================================ */}
      <div className="studio-layout-3col">

        {/* Left Column: Moving Source, Extraction Stages 1–5, & Feature Telemetry */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <ImageUploader
            role="SOURCE"
            image={sourceImage}
            onImageUploaded={(meta) => {
              setSourceImage(meta);
              setActivePreset(null);
            }}
            disabled={jobStatus === 'PROCESSING'}
          />

          <PipelineStepper status={jobStatus} segment="FIRST_HALF" />

          {/* Feature & Radiometric Telemetry (Visual Histogram, Sun Compass, & Presets) */}
          <FeatureTelemetryPanel
            image={sourceImage}
            result={registrationResult}
            presets={PRESET_PAIRS}
            onSelectPreset={handleLoadPreset}
            loadingPresetId={loadingPreset}
            solarAzimuth={activePreset?.solarAzimuth}
            sunElevation={activePreset?.sunElevation}
          />

          {/* Sub-Pixel Residuals & Dispersion Inspector */}
          {registrationResult && (
            <SubpixelResidualsPanel
              result={registrationResult}
              image={sourceImage}
              referenceImage={referenceImage}
            />
          )}
        </div>

        {/* Center Column: Viewport Stage, Alignment Parameters UNDER it, & Metrics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Main Visual Stage (Comparison Viewer or Standby Viewport) */}
          {registrationResult ? (
            <ComparisonViewer
              result={registrationResult}
              sourcePreviewUrl={sourceImage?.previewUrl}
              referencePreviewUrl={referenceImage?.previewUrl}
              sourceImage={sourceImage}
              referenceImage={referenceImage}
            />
          ) : (
            /* Standby Pre-Registration Viewport */
            <div className="card" style={{ minHeight: '520px', display: 'flex', flexDirection: 'column' }}>
              <div className="card-header">
                <div className="card-title">
                  <ImageIcon size={16} style={{ color: 'var(--accent-blue)' }} />
                  <span>Viewport Preview</span>
                </div>
                {jobStatus === 'PROCESSING' ? (
                  <span className="badge badge-processing">
                    <Loader2 size={11} className="spin" />
                    <span>Aligning...</span>
                  </span>
                ) : (
                  <span className="badge badge-neutral">Standby</span>
                )}
              </div>

              {sourceImage && referenceImage ? (
                /* Interactive Point Matching & Vector Visualization */
                <PointMatchingVisualizer
                  sourceImage={sourceImage}
                  referenceImage={referenceImage}
                  jobStatus={jobStatus}
                  registrationResult={registrationResult}
                />
              ) : (
                /* Empty State Guidance */
                <div
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '3rem 2rem',
                    textAlign: 'center',
                  }}
                >
                  <div
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: 'var(--radius-md)',
                      background: 'var(--bg-surface-elevated)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--accent-blue)',
                      marginBottom: '1rem',
                    }}
                  >
                    <ImageIcon size={22} />
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                    No Lunar Frames Selected
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '360px', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                    Load Moving Source on the left and Fixed Reference on the right, or pick one of the curated demonstration sample pairs above.
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleLoadPreset(PRESET_PAIRS[0])}
                      disabled={loadingPreset !== null}
                    >
                      <Sparkles size={12} style={{ color: 'var(--accent-blue)' }} />
                      <span>Load Pair 01 (Baseline Crater)</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Alignment Parameters & Execution Panel PLACED DIRECTLY UNDER THE VIEWPORT */}
          <ConfigPanel
            config={config}
            setConfig={setConfig}
            onExecute={handleExecuteRegistration}
            isExecuting={jobStatus === 'PROCESSING'}
            canExecute={canExecute}
          />

          {/* Scientific Metrics (Rendered when registration results are ready) */}
          {registrationResult && (
            <ScientificMetricsPanel result={registrationResult} />
          )}

          {/* Image & Sensor Info — 2-column horizontal layout below metrics */}
          {registrationResult && sourceImage && referenceImage && (
            <ImageSensorInfoPanel
              sourceImage={sourceImage}
              referenceImage={referenceImage}
              jobStatus={jobStatus}
              horizontal
            />
          )}
        </div>

        {/* Right Column: Fixed Reference, Geometric Consensus Stages 6–10, & Transformation/Export */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <ImageUploader
            role="REFERENCE"
            image={referenceImage}
            onImageUploaded={(meta) => setReferenceImage(meta)}
            disabled={jobStatus === 'PROCESSING'}
          />

          <PipelineStepper status={jobStatus} segment="SECOND_HALF" />

          {/* Projective Geometry & Mission Products */}
          <TransformationExportPanel image={referenceImage} result={registrationResult} />

          {/* Registration Quality & Summary */}
          {registrationResult && (
            <RegistrationSummaryPanel result={registrationResult} />
          )}
        </div>
      </div>
    </div>
  );
};
