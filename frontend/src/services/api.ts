import axios, { AxiosResponse } from 'axios';
import {
  UploadResponse,
  ProcessingStatus,
  ProcessingResult,
  ErrorResponse,
  OutputFormatEnum
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const uploadDocument = async (
  file: File,
  outputFilename?: string,
  outputFormat: OutputFormatEnum = OutputFormatEnum.DOCX
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (outputFilename) {
    formData.append('output_filename', outputFilename);
  }
  
  formData.append('output_format', outputFormat);

  try {
    const response: AxiosResponse<UploadResponse> = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to upload document');
  }
};

export const getProcessingStatus = async (taskId: string): Promise<ProcessingStatus> => {
  try {
    const response: AxiosResponse<ProcessingStatus> = await api.get(`/status/${taskId}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to get processing status');
  }
};

export const downloadReport = async (taskId: string): Promise<Blob> => {
  try {
    const response = await api.get(`/download/${taskId}`, {
      responseType: 'blob',
    });
    
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to download report');
  }
};

export const getProcessingResults = async (taskId: string): Promise<any> => {
  try {
    const response = await api.get(`/results/${taskId}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to get processing results');
  }
};

export const checkHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error: any) {
    throw new Error('Service is not available');
  }
};

// Utility function to poll for status updates
export const pollStatus = async (
  taskId: string,
  onUpdate: (status: ProcessingStatus) => void,
  onComplete: (status: ProcessingStatus) => void,
  onError: (error: string) => void,
  interval: number = 2000
): Promise<void> => {
  const poll = async () => {
    try {
      const status = await getProcessingStatus(taskId);
      onUpdate(status);
      
      if (status.status === 'completed') {
        onComplete(status);
        return;
      }
      
      if (status.status === 'error') {
        onError(status.error || 'Processing failed');
        return;
      }
      
      // Continue polling
      setTimeout(poll, interval);
    } catch (error: any) {
      onError(error.message);
    }
  };
  
  poll();
};

// Utility function to download file
export const downloadFile = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api;
