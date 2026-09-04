import React, { useRef, useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Hash } from 'lucide-react';
import { ImageMetadata, DataCategory } from '../../types';
import { apiService, parseApiError } from '../../services/api';

interface ImageUploaderProps {
  role: 'SOURCE' | 'REFERENCE';
  label?: string;
  subLabel: string;
  image: ImageMetadata | null;
  onImageUploaded: (metadata: ImageMetadata) => void;
  disabled?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  role,
  subLabel,
  image,
  onImageUploaded,
  disabled = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sensorName, setSensorName] = useState<string>(role === 'SOURCE' ? 'TMC-2' : 'OHRC');
  const [gsdMeters, setGsdMeters] = useState<string>(role === 'SOURCE' ? '5.0' : '0.25');
  const [dataCategory, setDataCategory] = useState<DataCategory>('SYNTHETIC_BENCHMARK');

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
      setDataCategory(detected.category);

      const gsdNum = detected.gsd ? parseFloat(detected.gsd) : undefined;
      const meta = await apiService.uploadImage(file, detected.sensor, detected.mission, gsdNum, detected.category);
      
      // Attach local preview URL for instant rendering
      meta.previewUrl = URL.createObjectURL(file);
      onImageUploaded(meta);
    } catch (err) {
      setErrorMsg(parseApiError(err));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="card-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              className="badge"
              style={{
                background: role === 'SOURCE' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(168, 85, 247, 0.15)',
                color: role === 'SOURCE' ? '#38bdf8' : '#c084fc',
                borderColor: role === 'SOURCE' ? 'rgba(56, 189, 248, 0.4)' : 'rgba(168, 85, 247, 0.4)',
              }}
            >
              {role === 'SOURCE' ? 'SOURCE (MOVING IMAGE)' : 'REFERENCE (FIXED IMAGE)'}
            </span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{subLabel}</div>
        </div>
        {image && (
          <span className="badge badge-success">
            <CheckCircle size={12} />
            <span>Ready (ID: {image.id})</span>
          </span>
        )}
      </div>

      {!image ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div
            className="dropzone"
            onClick={() => !disabled && fileInputRef.current?.click()}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".png,.jpg,.jpeg,.tif,.tiff,.raw"
              disabled={disabled || isUploading}
            />
            <Upload size={36} color="var(--accent-cyan)" style={{ marginBottom: '0.75rem' }} />
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.25rem' }}>
              {isUploading ? 'Uploading & Computing Checksum...' : 'Select or Drop Lunar Image'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Supports PNG, GeoTIFF, TIFF, RAW (Max 100MB)
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Sensor Payload</label>
              <select
                className="form-select"
                value={sensorName}
                onChange={(e) => setSensorName(e.target.value)}
                disabled={disabled || isUploading}
              >
                <option value="TMC-2">TMC-2 (5m Stereo)</option>
                <option value="OHRC">OHRC (0.25m High-Res)</option>
                <option value="IIRS">IIRS (SWIR Hyperspectral)</option>
                <option value="LRO_NAC">LRO NAC (0.5m)</option>
                <option value="SYNTHETIC">Synthetic Surface Simulator</option>
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Ground Sampling (m)</label>
              <input
                type="number"
                step="0.01"
                className="form-input"
                value={gsdMeters}
                onChange={(e) => setGsdMeters(e.target.value)}
                placeholder="e.g. 5.0"
                disabled={disabled || isUploading}
              />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Data Provenance Category</label>
            <select
              className="form-select"
              value={dataCategory}
              onChange={(e) => setDataCategory(e.target.value as DataCategory)}
              disabled={disabled || isUploading}
            >
              <option value="SYNTHETIC_BENCHMARK">SYNTHETIC_BENCHMARK (Controlled DEM Test)</option>
              <option value="AUTHENTIC_CH2_PRADAN">AUTHENTIC_CH2_PRADAN (ISRO Orbital Data)</option>
            </select>
          </div>

          {errorMsg && (
            <div style={{ color: 'var(--accent-rose)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <AlertCircle size={14} />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ textAlign: 'center', background: '#000', borderRadius: 'var(--radius-md)', padding: '0.5rem' }}>
            {image.previewUrl ? (
              <img src={image.previewUrl} alt={image.filename} className="dropzone-preview" />
            ) : (
              <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Image Uploaded (ID: {image.id})</div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.78rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Filename:</span>
              <span style={{ color: '#fff', fontWeight: 600 }}>{image.filename}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Sensor / Mission:</span>
              <span style={{ color: '#fff' }}>{image.sensorName} ({image.missionName})</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>GSD:</span>
              <span style={{ color: '#fff' }}>{image.gsdMeters ? `${image.gsdMeters} m/px` : 'N/A'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Category:</span>
              <span className="badge badge-category">{image.dataCategory}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)', fontSize: '0.7rem' }}>
              <Hash size={12} />
              <span className="font-mono" title={image.sha256Checksum}>
                SHA-256: {image.sha256Checksum.substring(0, 16)}...
              </span>
            </div>
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            style={{ marginTop: 'auto' }}
            disabled={disabled}
          >
            <Upload size={14} />
            <span>Replace Image</span>
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
