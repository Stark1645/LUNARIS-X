/**
 * Data Types and API DTOs matching Spring Boot 3 & Python ML Contracts
 */

export type AlgorithmType = 'Proposed_Method' | 'SIFT_Baseline' | 'RIFT_Baseline';
export type TransformationModelType = 'HOMOGRAPHY' | 'AFFINE' | 'SIMILARITY' | 'TRANSLATION';
export type DataCategory = 'SYNTHETIC_BENCHMARK' | 'AUTHENTIC_CH2_PRADAN';
export type JobStatus = 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'DEGRADED' | 'FAILED';

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

export interface RegistrationRequest {
  sourceImageId: number;
  referenceImageId: number;
  algorithm: AlgorithmType;
  transformationModel: TransformationModelType;
  ratioThreshold?: number;
  ransacThreshold?: number;
  enableSubpixel?: boolean;
  enableSpatialFilter?: boolean;
}

export interface MetricsDTO {
  candidateMatchesCount: number;
  inlierMatchesCount: number;
  inlierRatioPercent: number;
  rmseInliersPx: number | null;
  rmseGroundTruthPx: number | null;
  meanSubpixelResidualPx: number | null;
  subpixelAccuracyRate05px: number | null;
  spatialGiniCoefficient: number | null;
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
  rmseInliersPx: number | null;
  rmseGroundTruthPx: number | null;
  spatialGini: number | null;
  latencyMs: number | null;
  status: JobStatus;
  executedAt: string;
}

export interface HealthStatusDTO {
  status: string;
  backendVersion: string;
  pythonServiceStatus: string;
  pythonServiceUrl: string;
  databaseStatus: string;
  supportedAlgorithms: string[];
}

export interface ApiErrorResponse {
  timestamp: string;
  status: number;
  error: string;
  message: string;
  path: string;
  validationErrors?: string[];
}
