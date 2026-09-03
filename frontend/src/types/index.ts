/**
 * Data Types and API DTOs matching Spring Boot 3 & Python ML Contracts
 */

export type AlgorithmType = 'Proposed_Method' | 'SIFT_Baseline' | 'RIFT_Baseline';
export type TransformationModelType = 'HOMOGRAPHY' | 'AFFINE' | 'SIMILARITY' | 'TRANSLATION';
export type DataCategory = 'SYNTHETIC_BENCHMARK' | 'AUTHENTIC_CH2_PRADAN' | 'DEMO';
export type JobStatus = 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'DEGRADED' | 'FAILED';
export type SpatialQuality = 'GOOD' | 'ACCEPTABLE' | 'POOR';

export interface ImageMetadata {
  id: number;
  filename: string;
  fileType: string;
  fileSize: number;
  sha256Checksum: string;
  width?: number;
  height?: number;
  gsdMeters?: number;
  sensorName?: string;
  missionName?: string;
  dataCategory: DataCategory;
  uploadedAt: string;
  previewUrl?: string;
}

export interface PradanProductRecord {
  product_id: string;
  instrument: string;
  acquisition_time?: string;
  image_path: string;
  metadata_path: string;
  gsd_m?: number;
  gsd_status: string;
  dimensions?: { lines: number; samples: number; bands?: number };
  geographic_footprint?: { min_lat?: number; max_lat?: number; min_lon?: number; max_lon?: number };
  has_geographic_footprint: boolean;
  projection?: string;
  modality: string;
  solar_azimuth_deg?: number;
  incidence_angle_deg?: number;
  metadata_confidence: number;
  data_category: DataCategory;
  is_synthetic: boolean;
  provenance_manifest_path?: string;
}

export interface OverlapResult {
  is_valid_pair: boolean;
  has_overlap: boolean;
  overlap_status: 'CONFIRMED_OVERLAP' | 'CONFIRMED_DISJOINT' | 'INDETERMINATE_MISSING_FOOTPRINT' | 'MANUAL_BENCHMARK_PAIR';
  overlap_percentage_ref?: number | null;
  overlap_percentage_mov?: number | null;
  intersection_bounds?: { min_lat: number; max_lat: number; min_lon: number; max_lon: number };
  intersection_area_deg2?: number | null;
  scale_disparity_ratio?: number | null;
  reason: string;
  reference_product_id: string;
  moving_product_id: string;
  reference_instrument: string;
  moving_instrument: string;
  reference_gsd_m?: number | null;
  moving_gsd_m?: number | null;
}

export interface SelectionDecision {
  reference_product_id: string;
  moving_product_id: string;
  decision_tier: string;
  rationale: string;
  reference_instrument: string;
  moving_instrument: string;
  reference_gsd_m?: number | null;
  moving_gsd_m?: number | null;
  criteria_summary: Record<string, any>;
}

export interface RegistrationRequest {
  sourceImageId: number;
  referenceImageId: number;
  algorithm: AlgorithmType;
  transformationModel: TransformationModelType;
  ratioThreshold?: number;
  ransacThreshold?: number;
  enableSubpixel?: boolean;
  enableSpatialFilter?: boolean;
  dataCategory?: DataCategory;
  isSynthetic?: boolean;
}

export interface MetricsDTO {
  candidateMatchesCount: number;
  inlierMatchesCount: number;
  inlierRatioPercent: number;
  rmseInliersPx: number | null;
  rmseGroundTruthPx: number | null;
  groundTruthStatus?: 'AVAILABLE' | 'NOT_AVAILABLE';
  meanSubpixelResidualPx: number | null;
  maeResidualsPx?: number | null;
  medianResidualPx?: number | null;
  maxResidualPx?: number | null;
  subpixelAccuracyRate05px: number | null;
  subpixelAccuracyRate10px?: number | null;
  spatialGiniCoefficient: number | null;
  spatialQualityStatus?: SpatialQuality;
  latencyMs: number | null;
  dataCategory: DataCategory;
}

export interface MatchPointDTO {
  sourceX: number;
  sourceY: number;
  referenceX: number;
  referenceY: number;
  isInlier: boolean;
}

export interface RegistrationResponseDTO {
  jobId: number;
  status: JobStatus;
  algorithm: AlgorithmType;
  selectedTransformationModel: string;
  transformationMatrixJson: string;
  failureReason?: string;
  sourceImageId: number;
  referenceImageId: number;
  sourceFilename: string;
  referenceFilename: string;
  metrics: MetricsDTO;
  matchPoints?: MatchPointDTO[];
  warpedImageBase64?: string;
  matchVisBase64?: string;
  alphaOverlayBase64?: string;
  checkerboardBase64?: string;
  differenceMapBase64?: string;
  createdAt: string;
  completedAt?: string;
  dataCategory?: DataCategory;
  isSynthetic?: boolean;
  provenance?: Record<string, any>;
}

export interface JobStatusDTO {
  jobId: number;
  status: JobStatus;
  algorithm: string;
  failureReason?: string;
  createdAt: string;
  completedAt?: string;
}

export interface ExperimentDTO {
  id: number;
  experimentId: string;
  suiteName: string;
  pairName: string;
  algorithm: string;
  configurationName?: string;
  dataCategory: DataCategory;
  scaleRatio?: number;
  deltaSunAzimuthDeg?: number;
  inlierCount: number;
  inlierRatioPercent: number;
  rmseInliersPx?: number;
  rmseGroundTruthPx?: number;
  spatialGini?: number;
  latencyMs: number;
  status: string;
  executedAt: string;
}
