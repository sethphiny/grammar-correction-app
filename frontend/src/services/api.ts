import axios from 'axios';
import { UploadResponse, ProcessingStatus, OutputFormat } from '../types';

// WebSocket types
export interface WebSocketMessage {
  type: 'line_completed' | 'processing_complete' | 'status_update' | 'error';
  line_number?: number;
  issues?: any[];
  progress?: number;
  processed_lines?: number;
  total_lines?: number;
  total_issues?: number;
  skipped_sentences?: number;
  status?: string;
  message?: string;
  error?: string;
  timestamp?: number;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 0, // No timeout for large file uploads
  maxContentLength: 50 * 1024 * 1024, // 50MB max content length
  maxBodyLength: 50 * 1024 * 1024, // 50MB max body length
});

export const uploadDocument = async (
  file: File,
  outputFormat: OutputFormat = 'docx',
  customFilename?: string,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('output_format', outputFormat);
  if (customFilename) {
    formData.append('custom_filename', customFilename);
  }

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 0, // No timeout for large file uploads
      maxContentLength: 50 * 1024 * 1024, // 50MB max content length
      maxBodyLength: 50 * 1024 * 1024, // 50MB max body length
      // Add upload progress tracking
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
          if (onProgress) {
            onProgress(percentCompleted);
          }
        }
      }
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        throw new Error(error.response.data.detail || `Upload failed: ${error.response.status}`);
      } else if (error.request) {
        // Network error
        throw new Error('Network error: Unable to connect to server');
      }
    }
    throw new Error('Upload failed: Please try again');
  }
};

export const getProcessingStatus = async (processingId: string): Promise<ProcessingStatus> => {
  const response = await api.get(`/status/${processingId}`);
  return response.data;
};

export const downloadReport = async (processingId: string): Promise<Blob> => {
  const response = await api.get(`/download/${processingId}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const cleanupProcessing = async (processingId: string): Promise<void> => {
  await api.delete(`/cleanup/${processingId}`);
};

export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  const response = await api.get('/health');
  return response.data;
};

// WebSocket connection for real-time streaming updates
export class WebSocketService {
  private ws: WebSocket | null = null;
  private processingId: string | null = null;
  private onMessage: ((message: WebSocketMessage) => void) | null = null;
  private onError: ((error: Event) => void) | null = null;
  private onClose: (() => void) | null = null;

  connect(processingId: string, onMessage: (message: WebSocketMessage) => void, onError?: (error: Event) => void, onClose?: () => void): void {
    this.processingId = processingId;
    this.onMessage = onMessage;
    this.onError = onError || null;
    this.onClose = onClose || null;

    const wsUrl = API_BASE_URL.replace('http', 'ws') + `/ws/${processingId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected for processing:', processingId);
    };

    this.ws.onmessage = (event) => {
      try {
        console.log('Raw WebSocket message received:', event.data);
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('Parsed WebSocket message:', message);
        if (this.onMessage) {
          this.onMessage(message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.onError) {
        this.onError(error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      if (this.onClose) {
        this.onClose();
      }
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.processingId = null;
    this.onMessage = null;
    this.onError = null;
    this.onClose = null;
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
