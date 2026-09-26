import React from 'react';
import { Camera, Clock, Cpu, CheckCircle2, AlertCircle, Satellite, Layers } from 'lucide-react';
import { ImageMetadata, JobStatus } from '../../types';

interface ImageSensorInfoPanelProps {
  sourceImage: ImageMetadata | null;
  referenceImage: ImageMetadata | null;
  jobStatus: JobStatus | 'IDLE';
  horizontal?: boolean; // when true, render cards side-by-side
}

function formatDate(raw: string | null | undefined): string {
  if (!raw) return 'N/A';
  try {
    const normalized = /[Zz]|[+-]\d{2}:\d{2}$/.test(raw) ? raw : raw + 'Z';
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return raw;
    return d.toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
    });
  } catch { return raw; }
}

function formatBytes(bytes: number | undefined | null): string {
  if (!bytes) return '—';
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

const SENSOR_META: Record<string, { band: string; swath: string }> = {
  'OHRC':  { band: 'Panchromatic', swath: '1.6 km' },
  'TMC-2': { band: 'Panchromatic', swath: '20 km'  },
  'IIRS':  { band: 'SWIR / TIR',   swath: '29 km'  },
  'SAR':   { band: 'L-Band SAR',   swath: '10 km'  },
};
function getSensor(name?: string) {
  return SENSOR_META[name ?? ''] ?? { band: 'Panchromatic', swath: '—' };
}

interface CardProps {
  image: ImageMetadata;
  role: 'source' | 'reference';
  label: string;
  accentColor: string;
  gradientFrom: string;
  gradientTo: string;
}

const ImageCard: React.FC<CardProps> = ({ image, label, accentColor, gradientFrom, gradientTo }) => {
  const spec = getSensor(image.sensorName);

  const stats = [
    { label: 'GSD',     value: `${image.gsdMeters ?? 0.25} m/px` },
    { label: 'Band',    value: spec.band },
    { label: 'Swath',   value: spec.swath },
    { label: 'File',    value: formatBytes(image.fileSize) },
    ...(image.width && image.height ? [{ label: 'Pixels', value: `${image.width}×${image.height}` }] : []),
    { label: 'Mission', value: image.missionName ?? 'Chandrayaan-2' },
  ];

  return (
    <div style={{
      borderRadius: 'var(--radius-sm)',
      overflow: 'hidden',
      border: `1px solid ${accentColor}30`,
      background: 'var(--bg-surface-elevated)',
      position: 'relative',
    }}>
      {/* Banner: image preview + gradient overlay */}
      <div style={{ position: 'relative', height: 96, overflow: 'hidden', background: '#050810' }}>
        {image.previewUrl && (
          <img
            src={image.previewUrl}
            alt={label}
            style={{
              position: 'absolute', inset: 0,
              width: '100%', height: '100%',
              objectFit: 'cover', objectPosition: 'center 30%',
              opacity: 0.55,
            }}
          />
        )}
        {/* Gradient overlay for text readability */}
        <div style={{
          position: 'absolute', inset: 0,
          background: `linear-gradient(135deg, ${gradientFrom}55 0%, transparent 60%, ${gradientTo}22 100%)`,
        }} />
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0,
          background: 'linear-gradient(transparent, rgba(8,10,20,0.95))',
          height: 40,
        }} />

        {/* Role badge — top left */}
        <div style={{
          position: 'absolute', top: 10, left: 10,
          display: 'flex', alignItems: 'center', gap: '0.35rem',
          background: `${accentColor}22`,
          border: `1px solid ${accentColor}55`,
          backdropFilter: 'blur(6px)',
          borderRadius: '6px',
          padding: '0.2rem 0.55rem',
        }}>
          <Camera size={11} style={{ color: accentColor }} />
          <span style={{ fontSize: '0.63rem', fontWeight: 800, color: accentColor, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            {label}
          </span>
        </div>

        {/* Sensor badge — top right */}
        <div style={{
          position: 'absolute', top: 10, right: 10,
          background: 'rgba(0,0,0,0.65)',
          border: `1px solid ${accentColor}40`,
          backdropFilter: 'blur(6px)',
          borderRadius: '5px',
          padding: '0.18rem 0.45rem',
          fontSize: '0.65rem', fontWeight: 700, color: accentColor,
          letterSpacing: '0.04em',
        }}>
          {image.sensorName ?? 'OHRC'}
        </div>

        {/* Filename — bottom of banner */}
        <div style={{
          position: 'absolute', bottom: 7, left: 10, right: 10,
          fontSize: '0.67rem', fontWeight: 600, color: 'rgba(255,255,255,0.88)',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }} title={image.filename}>
          {image.filename}
        </div>
      </div>

      {/* Stats grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '0px',
        borderTop: `1px solid ${accentColor}18`,
      }}>
        {stats.slice(0, 6).map(({ label: l, value }, i) => (
          <div key={l} style={{
            padding: '0.42rem 0.6rem',
            borderRight: i % 3 !== 2 ? `1px solid ${accentColor}12` : 'none',
            borderBottom: i < 3 ? `1px solid ${accentColor}12` : 'none',
          }}>
            <div style={{ fontSize: '0.59rem', color: 'var(--text-muted)', marginBottom: '0.1rem', letterSpacing: '0.02em' }}>
              {l}
            </div>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {value}
            </div>
          </div>
        ))}
      </div>

      {/* Footer: timestamp */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.3rem',
        padding: '0.3rem 0.65rem',
        borderTop: `1px solid ${accentColor}12`,
        background: `${accentColor}06`,
      }}>
        <Clock size={9} style={{ color: accentColor, opacity: 0.7 }} />
        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>
          Uploaded: {formatDate(image.uploadedAt)}
        </span>
        <span style={{
          marginLeft: 'auto', fontSize: '0.59rem', fontWeight: 600,
          color: image.dataCategory === 'AUTHENTIC_CH2_PRADAN' ? '#34d399' : '#fbbf24',
        }}>
          {image.dataCategory === 'AUTHENTIC_CH2_PRADAN' ? '● PRADAN' : '● Synthetic'}
        </span>
      </div>
    </div>
  );
};

export const ImageSensorInfoPanel: React.FC<ImageSensorInfoPanelProps> = ({
  sourceImage, referenceImage, jobStatus, horizontal = false,
}) => {
  if (!sourceImage && !referenceImage) return null;

  const crossModal = sourceImage && referenceImage && sourceImage.sensorName !== referenceImage.sensorName;
  const sameSensor = sourceImage && referenceImage && sourceImage.sensorName === referenceImage.sensorName;

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <Satellite size={14} style={{ color: 'var(--accent-blue)' }} />
          <span>Image & Sensor Info</span>
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.3rem',
          fontSize: '0.62rem', color: 'var(--text-muted)',
          background: 'var(--bg-surface-elevated)',
          padding: '0.15rem 0.45rem', borderRadius: '4px',
          border: '1px solid var(--border-subtle)',
        }}>
          <Layers size={9} />
          Chandrayaan-2 / ISRO
        </div>
      </div>

      <div style={{
        display: horizontal ? 'grid' : 'flex',
        gridTemplateColumns: horizontal ? '1fr 1fr' : undefined,
        flexDirection: horizontal ? undefined : 'column',
        gap: '0.55rem',
        padding: '0.6rem',
      }}>
        {sourceImage && (
          <ImageCard image={sourceImage} role="source" label="Moving Source"
            accentColor="#38bdf8" gradientFrom="#0ea5e9" gradientTo="#0284c7" />
        )}
        {referenceImage && (
          <ImageCard image={referenceImage} role="reference" label="Fixed Reference"
            accentColor="#34d399" gradientFrom="#10b981" gradientTo="#059669" />
        )}
      </div>

      {/* Intelligence notes — only shown in vertical (sidebar) mode */}
      {!horizontal && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', padding: '0 0.6rem 0.6rem' }}>
          {crossModal && (
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: '0.4rem',
              padding: '0.4rem 0.6rem',
              background: 'rgba(251,191,36,0.07)',
              border: '1px solid rgba(251,191,36,0.2)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '0.66rem', color: '#fbbf24',
            }}>
              <AlertCircle size={11} style={{ flexShrink: 0, marginTop: 1 }} />
              <span>Cross-modal pair ({sourceImage?.sensorName} ↔ {referenceImage?.sensorName}) — expect reduced inlier ratio</span>
            </div>
          )}
          {sameSensor && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              padding: '0.35rem 0.6rem',
              background: 'rgba(52,211,153,0.06)',
              border: '1px solid rgba(52,211,153,0.15)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '0.66rem', color: '#34d399',
            }}>
              <CheckCircle2 size={11} style={{ flexShrink: 0 }} />
              <span>Mono-modal pair ({sourceImage?.sensorName}) — optimal for Phase Congruency alignment</span>
            </div>
          )}
          {jobStatus === 'PROCESSING' && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              padding: '0.35rem 0.6rem',
              background: 'rgba(96,165,250,0.07)',
              border: '1px solid rgba(96,165,250,0.2)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '0.66rem', color: '#60a5fa',
            }}>
              <Cpu size={11} style={{ flexShrink: 0 }} />
              <span>Sub-pixel alignment in progress...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
