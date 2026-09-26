import React, { useRef, useState } from 'react';
import { Upload, CheckCircle2, AlertCircle, Hash, RefreshCw } from 'lucide-react';
import { ImageMetadata, DataCategory } from '../../types';
import { apiService, parseApiError } from '../../services/api';

interface ImageUploaderProps {
  role: 'SOURCE' | 'REFERENCE';
  label?: string;
  subLabel?: string;
  image: ImageMetadata | null;
  onImageUploaded: (metadata: ImageMetadata) => void;
  disabled?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  role,
  image,
  onImageUploaded,
  disabled = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sensorName, setSensorName] = useState<string>(role === 'SOURCE' ? 'TMC-2' : 'OHRC');
  const [gsdMeters, setGsdMeters] = useState<string>(role === 'SOURCE' ? '5.0' : '0.25');

  const detectMetadataFromFilename = (filename: string) => {
    const lower = filename.toLowerCase();
    let sensor = role === 'SOURCE' ? 'TMC-2' : 'OHRC';
    let gsd = role === 'SOURCE' ? '5.0' : '0.25';
    let mission = 'CHANDRAYAAN-2';
    let category: DataCategory = 'SYNTHETIC_BENCHMARK';

    if (lower.includes('ohr')) {
      sensor = 'OHRC';
      gsd = '0.25';
      mission = 'CHANDRAYAAN-2';
    } else if (lower.includes('tmc')) {
      sensor = 'TMC-2';
      gsd = '5.0';
      mission = 'CHANDRAYAAN-2';
    } else if (lower.includes('iirs')) {
      sensor = 'IIRS';
      gsd = '5.0';
      mission = 'CHANDRAYAAN-2';
    } else if (lower.includes('lro') || lower.includes('nac')) {
      sensor = 'LRO_NAC';
      gsd = '0.5';
      mission = 'LUNAR RECONNAISSANCE ORBITER';
    }

    if (lower.startsWith('ch2_') || lower.includes('pradan') || lower.includes('_b_brw_') || lower.includes('_d_img_')) {
      category = 'AUTHENTIC_CH2_PRADAN';
    } else if (lower.includes('synthetic') || lower.includes('pair_')) {
      category = 'SYNTHETIC_BENCHMARK';
    }

    return { sensor, gsd, mission, category };
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setErrorMsg(null);

    try {
      const detected = detectMetadataFromFilename(file.name);
      setSensorName(detected.sensor);
      setGsdMeters(detected.gsd);

      const gsdNum = detected.gsd ? parseFloat(detected.gsd) : undefined;
      const meta = await apiService.uploadImage(file, detected.sensor, detected.mission, gsdNum, detected.category);

      meta.sensorName = detected.sensor;
      meta.missionName = detected.mission;
      if (gsdNum !== undefined) {
        meta.gsdMeters = gsdNum;
      }
      meta.dataCategory = detected.category;

      meta.previewUrl = URL.createObjectURL(file);
      onImageUploaded(meta);
    } catch (err) {
      setErrorMsg(parseApiError(err));
    } finally {
      setIsUploading(false);
    }
  };

  const roleTitle = role === 'SOURCE' ? 'Moving Source' : 'Fixed Reference';

  return (
    <div className="card" style={{ padding: '1rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {roleTitle}
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '0.66rem' }}>
            {role === 'SOURCE' ? 'TO BE WARPED' : 'BASE TARGET'}
          </span>
        </div>

        {image && (
          <span className="badge badge-success" style={{ fontSize: '0.68rem' }}>
            <CheckCircle2 size={11} />
            <span>Loaded</span>
          </span>
        )}
      </div>

      {!image ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div
            className="dropzone"
            onClick={() => !disabled && fileInputRef.current?.click()}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '140px' }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".png,.jpg,.jpeg,.tif,.tiff,.raw"
              disabled={disabled || isUploading}
            />
            <Upload size={24} style={{ color: 'var(--accent-blue)', marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.2rem' }}>
              {isUploading ? 'Uploading...' : `Upload ${roleTitle}`}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              PNG, TIFF, GeoTIFF, RAW
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: '0.7rem' }}>Sensor</label>
              <select
                className="form-select"
                style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem' }}
                value={sensorName}
                onChange={(e) => setSensorName(e.target.value)}
                disabled={disabled || isUploading}
              >
                <option value="TMC-2">TMC-2 (5m)</option>
                <option value="OHRC">OHRC (0.25m)</option>
                <option value="IIRS">IIRS (SWIR)</option>
                <option value="LRO_NAC">LRO NAC (0.5m)</option>
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ fontSize: '0.7rem' }}>GSD (m)</label>
              <input
                type="number"
                step="0.01"
                className="form-input"
                style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem' }}
                value={gsdMeters}
                onChange={(e) => setGsdMeters(e.target.value)}
                placeholder="5.0"
                disabled={disabled || isUploading}
              />
            </div>
          </div>

          {errorMsg && (
            <div style={{ color: 'var(--accent-rose)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <AlertCircle size={13} />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ textAlign: 'center', background: '#000', borderRadius: 'var(--radius-sm)', padding: '0.35rem', overflow: 'hidden' }}>
            <img src={image.previewUrl} alt={image.filename} className="dropzone-preview" style={{ maxHeight: '140px' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>File:</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={image.filename}>
                {image.filename}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Sensor:</span>
              <span style={{ color: 'var(--text-primary)' }}>{image.sensorName}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Resolution:</span>
              <span style={{ color: 'var(--text-primary)' }}>{image.gsdMeters ? `${image.gsdMeters} m/px` : 'N/A'}</span>
            </div>
            {image.width && image.height && (
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Dimensions:</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                  {image.width} × {image.height}
                </span>
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-dim)', fontSize: '0.68rem', marginTop: '0.15rem' }}>
              <Hash size={11} />
              <span className="font-mono">{image.sha256Checksum.substring(0, 16)}...</span>
            </div>
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            style={{ marginTop: 'auto', padding: '0.35rem 0.75rem', fontSize: '0.74rem' }}
            disabled={disabled}
          >
            <RefreshCw size={12} />
            <span>Change Image</span>
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            accept=".png,.jpg,.jpeg,.tif,.tiff,.raw"
          />
        </div>
      )}
    </div>
  );
};
