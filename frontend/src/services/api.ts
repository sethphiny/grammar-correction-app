import axios, { AxiosResponse } from 'axios';
import {
  UploadResponse,
  ProcessingStatus,
  ProcessingResult,
  ErrorResponse,
  OutputFormatEnum
} from '../types';

// Detect if running in Electron and get backend URL
declare global {
  interface Window {
    electronAPI?: {
      getBackendUrl: () => Promise<string>;
      getAppVersion: () => Promise<string>;
      checkForUpdates: () => Promise<void>;
      onUpdateStatus: (callback: (data: any) => void) => void;
      onUpdateProgress: (callback: (data: any) => void) => void;
      isElectron: boolean;
      platform: string;
    };
  }
}

// Function to get the appropriate API base URL
async function getApiBaseUrl(): Promise<string> {
  // Check if running in Electron
  if (window.electronAPI?.isElectron) {
    try {
      const backendUrl = await window.electronAPI.getBackendUrl();
      console.log('Running in Electron, backend URL:', backendUrl);
      return backendUrl;
    } catch (error) {
      console.error('Failed to get backend URL from Electron:', error);
    }
  }
  
  // Fall back to environment variable or default
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
}

// Initialize API_BASE_URL - will be set asynchronously
let API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Set the correct URL when running in Electron
if (window.electronAPI?.isElectron) {
  getApiBaseUrl().then(url => {
    API_BASE_URL = url;
    // Update axios instances with new base URL
    api.defaults.baseURL = url;
    uploadApi.defaults.baseURL = url;
  });
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a separate axios instance for uploads with longer timeout
const uploadApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes for uploads (large files need time)
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor for regular API
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Request interceptor for upload API
uploadApi.interceptors.request.use(
  (config) => {
    console.log(`Making UPLOAD ${config.method?.toUpperCase()} request to ${config.url}`);
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
  outputFormat: OutputFormatEnum = OutputFormatEnum.DOCX,
  categories?: string[],
  useLLMEnhancement: boolean = true,
  useLLMDetection: boolean = false
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (outputFilename) {
    formData.append('output_filename', outputFilename);
  }
  
  formData.append('output_format', outputFormat);
  
  // Add categories as comma-separated string if provided
  if (categories && categories.length > 0) {
    formData.append('categories', categories.join(','));
  }
  
  // Add LLM feature flags
  formData.append('use_llm_enhancement', useLLMEnhancement ? 'true' : 'false');
  formData.append('use_llm_detection', useLLMDetection ? 'true' : 'false');

  try {
    const response: AxiosResponse<UploadResponse> = await uploadApi.post('/upload', formData);
    
    return response.data;
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      throw new Error('Upload timeout - file may be too large. Please try a smaller file.');
    }
    throw new Error(error.response?.data?.detail || 'Failed to upload document');
  }
};

export const getProcessingStatus = async (taskId: string): Promise<ProcessingStatus> => {
  try {
    console.log(`Getting status for task: ${taskId}`);
    const response: AxiosResponse<ProcessingStatus> = await api.get(`/status/${taskId}`);
    console.log(`Status response:`, response.data);
    return response.data;
  } catch (error: any) {
    console.error(`Status check failed for task ${taskId}:`, error);
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
      console.log(`🔄 Polling status for task ${taskId}...`);
      const status = await getProcessingStatus(taskId);
      console.log(`📊 Status received:`, {
        task_id: status.task_id,
        status: status.status,
        progress: status.progress,
        message: status.message
      });
      
      onUpdate(status);
      
      if (status.status === 'completed') {
        console.log('✅ Processing completed!');
        onComplete(status);
        return;
      }
      
      if (status.status === 'error') {
        console.error('❌ Processing error:', status.error);
        onError(status.error || 'Processing failed');
        return;
      }
      
      // Continue polling
      console.log(`⏳ Continuing to poll in ${interval}ms... (Current: ${status.status} - ${status.progress}%)`);
      setTimeout(poll, interval);
    } catch (error: any) {
      console.error('Error polling status:', error);
      onError(error.message);
    }
  };
  
  console.log(`Starting status polling for task ${taskId}`);
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

// WebSocket connection for real-time progress updates
export const connectWebSocket = (
  taskId: string,
  onMessage: (data: any) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket => {
  // Use the current API_BASE_URL which may have been updated for Electron
  const baseUrl = api.defaults.baseURL || API_BASE_URL;
  const wsUrl = baseUrl.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/ws/${taskId}`);
  
  ws.onopen = () => {
    console.log(`🔌 WebSocket connected for task ${taskId}`);
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('📨 WebSocket message:', data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('🔌 WebSocket disconnected');
    if (onClose) onClose();
  };
  
  return ws;
};

export const apiClient = api;
export default api;
