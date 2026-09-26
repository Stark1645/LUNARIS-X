import React, { useState, useRef, useCallback } from 'react';
import { Eye, Grid, Layers, Activity, Download, SplitSquareVertical, Maximize2, Sliders, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { RegistrationResponseDTO, ImageMetadata } from '../../types';
import { PointMatchingVisualizer } from './PointMatchingVisualizer';

interface ComparisonViewerProps {
  result: RegistrationResponseDTO;
  sourcePreviewUrl?: string;
  referencePreviewUrl?: string;
  sourceImage?: ImageMetadata | null;
  referenceImage?: ImageMetadata | null;
}

type ViewMode = 'SPLIT_CURTAIN' | 'OVERLAY' | 'PANORAMIC_MOSAIC' | 'CHECKERBOARD' | 'DIFFERENCE' | 'MATCHES' | 'SIDE_BY_SIDE';

export const ComparisonViewer: React.FC<ComparisonViewerProps> = ({
  result,
  sourcePreviewUrl,
  referencePreviewUrl,
  sourceImage,
  referenceImage,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('OVERLAY');
  const [opacity, setOpacity] = useState<number>(0.5);
  const [splitPos, setSplitPos] = useState<number>(50); // percentage 0-100
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [zoom, setZoom] = useState<number>(1.0);

  const containerRef = useRef<HTMLDivElement>(null);

  const downloadImage = (base64Data: string, filename: string) => {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = filename;
    link.click();
  };

  const handlePointerMove = useCallback((clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const clampedPct = Math.min(Math.max((x / rect.width) * 100, 0), 100);
    setSplitPos(clampedPct);
  }, []);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      handlePointerMove(e.clientX);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length > 0) {
      handlePointerMove(e.touches[0].clientX);
    }
  };

  const referenceImg = result.referenceImageBase64 || referencePreviewUrl;
  const warpedImg = result.warpedImageBase64;

  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      {/* Viewer Header & Segmented Mode Switcher */}
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.85rem' }}>
        <div className="card-title">
          <Eye size={16} style={{ color: 'var(--accent-blue)' }} />
          <span>Visual Verification</span>
        </div>

        {/* Apple-style Segmented View Mode Tabs */}
        <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap', background: 'var(--bg-surface-elevated)', padding: '0.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
          <button
            className={`btn ${viewMode === 'OVERLAY' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('OVERLAY')}
          >
            <Layers size={12} />
            <span>Cross-Fade</span>
          </button>

          <button
            className={`btn ${viewMode === 'SPLIT_CURTAIN' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('SPLIT_CURTAIN')}
          >
            <Sliders size={12} />
            <span>Split Curtain</span>
          </button>

          <button
            className={`btn ${viewMode === 'PANORAMIC_MOSAIC' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('PANORAMIC_MOSAIC')}
          >
            <Maximize2 size={12} />
            <span>Mosaic</span>
          </button>

          <button
            className={`btn ${viewMode === 'CHECKERBOARD' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('CHECKERBOARD')}
          >
            <Grid size={12} />
            <span>Checkerboard</span>
          </button>

          <button
            className={`btn ${viewMode === 'DIFFERENCE' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('DIFFERENCE')}
          >
            <Activity size={12} />
            <span>Difference</span>
          </button>

          <button
            className={`btn ${viewMode === 'MATCHES' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('MATCHES')}
          >
            <Eye size={12} />
            <span>Tie Points</span>
          </button>

          <button
            className={`btn ${viewMode === 'SIDE_BY_SIDE' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem', border: 'none' }}
            onClick={() => setViewMode('SIDE_BY_SIDE')}
          >
            <SplitSquareVertical size={12} />
            <span>Side-by-Side</span>
          </button>
        </div>
      </div>

      {/* Main Canvas Viewport */}
      <div className="viewer-canvas-wrapper" style={{ padding: '0.5rem' }}>

        {/* MODE 1: SPLIT CURTAIN */}
        {viewMode === 'SPLIT_CURTAIN' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            {referenceImg && warpedImg ? (
              <div
                ref={containerRef}
                className="curtain-viewer-container"
                onMouseDown={(e) => {
                  setIsDragging(true);
                  handlePointerMove(e.clientX);
                }}
                onMouseUp={() => setIsDragging(false)}
                onMouseLeave={() => setIsDragging(false)}
                onMouseMove={handleMouseMove}
                onTouchStart={(e) => {
                  setIsDragging(true);
                  if (e.touches.length > 0) handlePointerMove(e.touches[0].clientX);
                }}
                onTouchEnd={() => setIsDragging(false)}
                onTouchMove={handleTouchMove}
              >
                {/* Fixed Reference Layer */}
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    transform: `scale(${zoom})`,
                    transformOrigin: 'center center',
                    transition: 'transform 0.1s ease',
                  }}
                >
                  <img
                    src={referenceImg}
                    alt="Fixed Reference"
                    className="curtain-image"
                  />
                </div>

                {/* Clipped Warped Source Layer */}
                <div
                  className="curtain-image-clipped"
                  style={{
                    clipPath: `polygon(${splitPos}% 0, 100% 0, 100% 100%, ${splitPos}% 100%)`,
                    transform: `scale(${zoom})`,
                    transformOrigin: 'center center',
                    transition: 'transform 0.1s ease',
                  }}
                >
                  <img
                    src={warpedImg}
                    alt="Warped Source"
                    className="curtain-image"
                  />
                </div>

                {/* Hairline Divider & Handle */}
                <div
                  className="curtain-divider-line"
                  style={{ left: `${splitPos}%` }}
                >
                  <div className="curtain-handle-badge">
                    <span>◀▶</span>
                  </div>
                </div>

                {/* Clean Corner Labels */}
                <div className="curtain-label curtain-label-left">
                  Reference ({Math.round(splitPos)}%)
                </div>
                <div className="curtain-label curtain-label-right">
                  Warped Source ({Math.round(100 - splitPos)}%)
                </div>
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', padding: '3rem' }}>
                Both Reference and Warped Source images required for Split Curtain.
              </div>
            )}

            {/* Tactile Control Bar */}
            <div style={{ width: '100%', maxWidth: '600px', marginTop: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {Math.round(splitPos)}%
              </span>
              <input
                type="range"
                min="0"
                max="100"
                step="0.5"
                value={splitPos}
                onChange={(e) => setSplitPos(parseFloat(e.target.value))}
                style={{ flex: 1, cursor: 'ew-resize' }}
              />
              <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {Math.round(100 - splitPos)}%
              </span>

              {/* Zoom Buttons */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', borderLeft: '1px solid var(--border-subtle)', paddingLeft: '0.65rem' }}>
                <button
                  className="btn btn-secondary"
                  style={{ padding: '0.2rem 0.45rem', fontSize: '0.72rem' }}
                  onClick={() => setZoom((z) => Math.min(z + 0.25, 3.0))}
                  title="Zoom In"
                >
                  <ZoomIn size={12} />
                </button>
                <button
                  className="btn btn-secondary"
                  style={{ padding: '0.2rem 0.45rem', fontSize: '0.72rem' }}
                  onClick={() => setZoom((z) => Math.max(z - 0.25, 0.75))}
                  title="Zoom Out"
                >
                  <ZoomOut size={12} />
                </button>
                {zoom !== 1.0 && (
                  <button
                    className="btn btn-secondary"
                    style={{ padding: '0.2rem 0.45rem', fontSize: '0.72rem' }}
                    onClick={() => setZoom(1.0)}
                    title="Reset Zoom"
                  >
                    <RotateCcw size={11} />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* MODE 2: OVERLAY CROSS FADE */}
        {viewMode === 'OVERLAY' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            {referenceImg && warpedImg ? (
              <div style={{ position: 'relative', display: 'inline-block', maxWidth: '100%', borderRadius: 'var(--radius-sm)', overflow: 'hidden', background: '#000' }}>
                <img
                  src={referenceImg}
                  alt="Fixed Reference"
                  className="comparison-image"
                  style={{ display: 'block', maxHeight: '520px', width: 'auto', objectFit: 'contain' }}
                />
                <img
                  src={warpedImg}
                  alt="Warped Source"
                  className="comparison-image"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    opacity: opacity,
                    pointerEvents: 'none',
                    transition: 'opacity 0.05s ease-out',
                  }}
                />
              </div>
            ) : result.alphaOverlayBase64 ? (
              <img src={result.alphaOverlayBase64} alt="Alpha Blended Composite" className="comparison-image" />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Overlay product unavailable.</div>
            )}

            <div style={{ width: '80%', maxWidth: '420px', marginTop: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Reference</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.02"
                value={opacity}
                onChange={(e) => setOpacity(parseFloat(e.target.value))}
                style={{ flex: 1, cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Warped</span>
            </div>
          </div>
        )}

        {/* MODE 3: PANORAMIC MOSAIC */}
        {viewMode === 'PANORAMIC_MOSAIC' && (
          <div style={{ textAlign: 'center', width: '100%' }}>
            {result.panoramicMosaicBase64 ? (
              <img
                src={result.panoramicMosaicBase64}
                alt="Expanded Panoramic Mosaic"
                className="comparison-image"
                style={{ maxHeight: '540px', objectFit: 'contain' }}
              />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Mosaic unavailable.</div>
            )}
          </div>
        )}

        {/* MODE 4: CHECKERBOARD */}
        {viewMode === 'CHECKERBOARD' && (
          <div style={{ textAlign: 'center', width: '100%' }}>
            {result.checkerboardBase64 ? (
              <img src={result.checkerboardBase64} alt="8x8 Checkerboard" className="comparison-image" />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Checkerboard unavailable.</div>
            )}
          </div>
        )}

        {/* MODE 5: DIFFERENCE MAP */}
        {viewMode === 'DIFFERENCE' && (
          <div style={{ textAlign: 'center', width: '100%' }}>
            {result.differenceMapBase64 ? (
              <img src={result.differenceMapBase64} alt="Difference Heatmap" className="comparison-image" />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Difference map unavailable.</div>
            )}
          </div>
        )}

        {/* MODE 6: MATCH INLIERS */}
        {viewMode === 'MATCHES' && (
          <div style={{ textAlign: 'center', width: '100%' }}>
            {sourceImage && referenceImage ? (
              <PointMatchingVisualizer
                sourceImage={sourceImage}
                referenceImage={referenceImage}
                jobStatus={result.status}
                registrationResult={result}
              />
            ) : result.matchVisBase64 ? (
              <img src={result.matchVisBase64} alt="Tie Point Matches" className="comparison-image" />
            ) : (
              <div style={{ color: 'var(--text-muted)' }}>Match visualization unavailable.</div>
            )}
          </div>
        )}

        {/* MODE 7: SIDE BY SIDE */}
        {viewMode === 'SIDE_BY_SIDE' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', width: '100%' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>1. Source (Moving)</div>
              {sourcePreviewUrl ? (
                <img src={sourcePreviewUrl} alt="Source" style={{ width: '100%', maxHeight: '340px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Original Source</div>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>2. Reference (Fixed)</div>
              {referencePreviewUrl ? (
                <img src={referencePreviewUrl} alt="Reference" style={{ width: '100%', maxHeight: '340px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Fixed Reference</div>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>3. Warped Output</div>
              {result.warpedImageBase64 ? (
                <img src={result.warpedImageBase64} alt="Warped Source" style={{ width: '100%', maxHeight: '340px', objectFit: 'contain' }} />
              ) : (
                <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Warped Output</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Export Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.75rem', paddingTop: '0.65rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Aligned coordinate frame ready for scientific mosaic integration.
        </div>

        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          {result.panoramicMosaicBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.74rem' }}
              onClick={() => downloadImage(result.panoramicMosaicBase64!, `mosaic_job_${result.jobId}.png`)}
            >
              <Download size={11} />
              <span>Mosaic</span>
            </button>
          )}

          {result.warpedImageBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.74rem' }}
              onClick={() => downloadImage(result.warpedImageBase64!, `warped_job_${result.jobId}.png`)}
            >
              <Download size={11} />
              <span>Warped Image</span>
            </button>
          )}

          {result.alphaOverlayBase64 && (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.74rem' }}
              onClick={() => downloadImage(result.alphaOverlayBase64!, `overlay_job_${result.jobId}.png`)}
            >
              <Download size={11} />
              <span>Overlay</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
