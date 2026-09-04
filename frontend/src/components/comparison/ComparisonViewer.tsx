import React, { useState } from 'react';
import { Eye, Grid, Layers, Activity, Download, SplitSquareVertical, Maximize2 } from 'lucide-react';
import { RegistrationResponseDTO } from '../../types';

interface ComparisonViewerProps {
  result: RegistrationResponseDTO;
  sourcePreviewUrl?: string;
  referencePreviewUrl?: string;
}

type ViewMode = 'OVERLAY' | 'PANORAMIC_MOSAIC' | 'CHECKERBOARD' | 'DIFFERENCE' | 'MATCHES' | 'SIDE_BY_SIDE';

export const ComparisonViewer: React.FC<ComparisonViewerProps> = ({
  result,
  sourcePreviewUrl,
  referencePreviewUrl,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('OVERLAY');
  const [opacity, setOpacity] = useState<number>(0.5);

  const downloadImage = (base64Data: string, filename: string) => {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = filename;
    link.click();
  };

  return (
    <div className="card">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
        <div className="card-title">
          <Eye size={18} color="var(--accent-cyan)" />
          <span>Registration Visual Products & Verification</span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            className={`btn ${viewMode === 'OVERLAY' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('OVERLAY')}
          >
            <Layers size={14} />
            <span>Alpha Overlay</span>
          </button>

          <button
            className={`btn ${viewMode === 'PANORAMIC_MOSAIC' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('PANORAMIC_MOSAIC')}
          >
            <Maximize2 size={14} />
            <span>Panoramic Mosaic</span>
          </button>

          <button
            className={`btn ${viewMode === 'CHECKERBOARD' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('CHECKERBOARD')}
          >
            <Grid size={14} />
            <span>8x8 Checkerboard</span>
          </button>

          <button
            className={`btn ${viewMode === 'DIFFERENCE' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('DIFFERENCE')}
          >
            <Activity size={14} />
            <span>Difference Map</span>
          </button>

          <button
            className={`btn ${viewMode === 'MATCHES' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('MATCHES')}
          >
            <Eye size={14} />
            <span>Match Inliers</span>
          </button>

          <button
            className={`btn ${viewMode === 'SIDE_BY_SIDE' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => setViewMode('SIDE_BY_SIDE')}
          >
            <SplitSquareVertical size={14} />
            <span>Side-by-Side</span>
          </button>
        </div>
      </div>

      {/* Main Visual Display Canvas */}
      <div className="viewer-canvas-wrapper" style={{ padding: '1rem' }}>
        {viewMode === 'OVERLAY' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            {result.alphaOverlayBase64 ? (
              <img
                src={result.alphaOverlayBase64}
                alt="Alpha Blended Composite"
                className="comparison-image"
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Overlay product not returned by engine.</div>
            )}
            <div style={{ width: '80%', maxWidth: '400px', marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Fixed Ref</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={opacity}
                onChange={(e) => setOpacity(parseFloat(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Warped Src</span>
            </div>
          </div>
        )}

        {viewMode === 'PANORAMIC_MOSAIC' && (
          <div style={{ textAlign: 'center' }}>
            {result.panoramicMosaicBase64 ? (
              <img
                src={result.panoramicMosaicBase64}
                alt="Expanded Panoramic Mosaic"
                className="comparison-image"
                style={{ maxHeight: '550px', objectFit: 'contain' }}
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Panoramic mosaic product not available.</div>
            )}
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Full expanded composite preserving 100% spatial extent of both Source and Reference images with seamless blending across the overlap zone.
            </div>
          </div>
        )}

        {viewMode === 'CHECKERBOARD' && (
          <div style={{ textAlign: 'center' }}>
            {result.checkerboardBase64 ? (
              <img
                src={result.checkerboardBase64}
                alt="8x8 Checkerboard Alignment"
                className="comparison-image"
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Checkerboard product not available.</div>
            )}
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Continuity across grid boundaries confirms sub-pixel alignment of lunar topography.
            </div>
          </div>
        )}

        {viewMode === 'DIFFERENCE' && (
          <div style={{ textAlign: 'center' }}>
            {result.differenceMapBase64 ? (
              <img
                src={result.differenceMapBase64}
                alt="Radiometric Difference Heatmap"
                className="comparison-image"
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Difference heatmap not available.</div>
            )}
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Dark regions indicate exact structural agreement; bright fringes highlight shadow variations.
            </div>
          </div>
        )}

        {viewMode === 'MATCHES' && (
          <div style={{ textAlign: 'center' }}>
            {result.matchVisBase64 ? (
              <img
                src={result.matchVisBase64}
                alt="Tie Point Matches"
                className="comparison-image"
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Match visualization not available.</div>
            )}
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              <span style={{ color: '#34d399', fontWeight: 600 }}>Green lines</span> = Verified Inliers |{' '}
              <span style={{ color: '#f87171', fontWeight: 600 }}>Red lines</span> = Rejected Outliers
            </div>
          </div>
        )}

        {viewMode === 'SIDE_BY_SIDE' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', width: '100%' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                1. SOURCE (MOVING IMAGE)
              </div>
              {sourcePreviewUrl ? (
                <img src={sourcePreviewUrl} alt="Source" style={{ width: '100%', maxHeight: '350px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Original Source</div>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#c084fc', marginBottom: '0.35rem' }}>
                2. REFERENCE (FIXED IMAGE)
              </div>
              {referencePreviewUrl ? (
                <img src={referencePreviewUrl} alt="Reference" style={{ width: '100%', maxHeight: '350px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Fixed Reference</div>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', marginBottom: '0.35rem' }}>
                3. REGISTERED (WARPED SOURCE)
              </div>
              {result.warpedImageBase64 ? (
                <img src={result.warpedImageBase64} alt="Warped Source" style={{ width: '100%', maxHeight: '350px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Warped Output</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Export Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Registered Source coordinate frame is mathematically aligned with Fixed Reference.
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {result.panoramicMosaicBase64 && (
            <button
              className="btn btn-primary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => downloadImage(result.panoramicMosaicBase64!, `panoramic_mosaic_job_${result.jobId}.png`)}
            >
              <Download size={12} />
              <span>Export Panoramic Mosaic</span>
            </button>
          )}

          {result.alphaOverlayBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => downloadImage(result.alphaOverlayBase64!, `fused_lunar_mosaic_job_${result.jobId}.png`)}
            >
              <Download size={12} />
              <span>Export Fused Overlay</span>
            </button>
          )}

          {result.warpedImageBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => downloadImage(result.warpedImageBase64!, `registered_job_${result.jobId}.png`)}
            >
              <Download size={12} />
              <span>Export Warped Image</span>
            </button>
          )}

          {result.checkerboardBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => downloadImage(result.checkerboardBase64!, `checkerboard_job_${result.jobId}.png`)}
            >
              <Download size={12} />
              <span>Export Checkerboard</span>
            </button>
          )}

          {result.differenceMapBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => downloadImage(result.differenceMapBase64!, `difference_job_${result.jobId}.png`)}
            >
              <Download size={12} />
              <span>Export Difference</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
