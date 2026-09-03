import axios, { AxiosError } from 'axios';
import {
  HealthStatusDTO,
  ImageMetadata,
  RegistrationRequest,
  RegistrationResponseDTO,
  JobStatusDTO,
  ExperimentDTO,
  ApiErrorResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 120000, // 2 minutes for heavy ML registration jobs
});

export const apiService = {
  // Health Status
  async getHealth(): Promise<HealthStatusDTO> {
    const resp = await apiClient.get<HealthStatusDTO>('/health');
    return resp.data;
  },

  // Image Management
  async uploadImage(
    file: File,
    sensorName: string = 'OPTICAL',
    missionName: string = 'CHANDRAYAAN-2',
    gsdMeters?: number,
    dataCategory: string = 'SYNTHETIC_BENCHMARK'
  ): Promise<ImageMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sensor_name', sensorName);
    formData.append('mission_name', missionName);
    formData.append('data_category', dataCategory);
    if (gsdMeters !== undefined && gsdMeters !== null) {
      formData.append('gsd_meters', gsdMeters.toString());
    }

    const resp = await apiClient.post<ImageMetadata>('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return resp.data;
  },

  async getImages(): Promise<ImageMetadata[]> {
    const resp = await apiClient.get<ImageMetadata[]>('/images');
    return resp.data;
  },

  async getImageById(id: number): Promise<ImageMetadata> {
    const resp = await apiClient.get<ImageMetadata>(`/images/${id}`);
    return resp.data;
  },

  // Registration Execution
  async submitRegistration(request: RegistrationRequest): Promise<RegistrationResponseDTO> {
    const resp = await apiClient.post<RegistrationResponseDTO>('/jobs/register', request);
    return resp.data;
  },

  async getAllJobs(): Promise<JobStatusDTO[]> {
    const resp = await apiClient.get<JobStatusDTO[]>('/jobs');
    return resp.data;
  },

  async getJobById(id: number): Promise<RegistrationResponseDTO> {
    const resp = await apiClient.get<RegistrationResponseDTO>(`/jobs/${id}`);
    return resp.data;
  },

  // Experiments & Benchmarks
  async getAllExperiments(): Promise<ExperimentDTO[]> {
    const resp = await apiClient.get<ExperimentDTO[]>('/experiments');
    return resp.data;
  },

  async getExperimentsBySuite(suiteName: string): Promise<ExperimentDTO[]> {
    const resp = await apiClient.get<ExperimentDTO[]>(`/experiments/suite/${encodeURIComponent(suiteName)}`);
    return resp.data;
  },
};

export function parseApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;
    if (axiosError.response?.data) {
      const data = axiosError.response.data;
      if (data.validationErrors && data.validationErrors.length > 0) {
        return data.validationErrors.join(', ');
      }
      return data.message || data.error || 'Server error occurred.';
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  return (error as Error)?.message || 'An unexpected error occurred.';
}
