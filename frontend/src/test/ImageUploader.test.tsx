import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ImageUploader } from '../components/upload/ImageUploader';
import { ImageMetadata } from '../types';

describe('ImageUploader Component', () => {
  it('correctly labels SOURCE as MOVING IMAGE and displays upload dropzone', () => {
    const handleUploaded = vi.fn();
    render(
      <ImageUploader
        role="SOURCE"
        label="Source Image"
        subLabel="Moving Frame"
        image={null}
        onImageUploaded={handleUploaded}
      />
    );

    expect(screen.getByText(/SOURCE \(MOVING IMAGE\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Select or Drop Lunar Image/i)).toBeInTheDocument();
    expect(screen.getByText(/TMC-2 \(5m Stereo\)/i)).toBeInTheDocument();
  });

  it('correctly labels REFERENCE as FIXED IMAGE', () => {
    const handleUploaded = vi.fn();
    render(
      <ImageUploader
        role="REFERENCE"
        label="Reference Image"
        subLabel="Fixed Basemap"
        image={null}
        onImageUploaded={handleUploaded}
      />
    );

    expect(screen.getByText(/REFERENCE \(FIXED IMAGE\)/i)).toBeInTheDocument();
    expect(screen.getByText(/OHRC \(0.25m High-Res\)/i)).toBeInTheDocument();
  });

  it('displays metadata and SHA-256 checksum when image is provided', () => {
    const mockImage: ImageMetadata = {
      id: 42,
      filename: 'ch2_tmc2_crater_01.png',
      fileType: 'PNG',
      fileSize: 2048500,
      sha256Checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      sensorName: 'TMC-2',
      missionName: 'CHANDRAYAAN-2',
      gsdMeters: 5.0,
      dataCategory: 'SYNTHETIC_BENCHMARK',
      uploadedAt: '2026-09-02T12:00:00',
    };

    render(
      <ImageUploader
        role="SOURCE"
        label="Source Image"
        subLabel="Moving Frame"
        image={mockImage}
        onImageUploaded={vi.fn()}
      />
    );

    expect(screen.getByText(/Ready \(ID: 42\)/i)).toBeInTheDocument();
    expect(screen.getByText('ch2_tmc2_crater_01.png')).toBeInTheDocument();
    expect(screen.getByText(/5 m\/px/i)).toBeInTheDocument();
    expect(screen.getByText(/SHA-256: e3b0c44298fc1c14.../i)).toBeInTheDocument();
  });
});
