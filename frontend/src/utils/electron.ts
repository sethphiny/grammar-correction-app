/**
 * Electron-specific utilities for the frontend
 */

export interface ElectronAPI {
  getBackendUrl: () => Promise<string>;
  getAppVersion: () => Promise<string>;
  checkForUpdates: () => Promise<void>;
  onUpdateStatus: (callback: (data: UpdateStatus) => void) => void;
  onUpdateProgress: (callback: (data: UpdateProgress) => void) => void;
  isElectron: boolean;
  platform: string;
}

export interface UpdateStatus {
  status: 'checking' | 'available' | 'not-available' | 'downloaded' | 'error';
  version?: string;
  error?: string;
}

export interface UpdateProgress {
  percent: number;
  transferred: number;
  total: number;
}

/**
 * Check if the app is running in Electron
 */
export function isElectron(): boolean {
  return !!(window as any).electronAPI?.isElectron;
}

/**
 * Get the Electron API if available
 */
export function getElectronAPI(): ElectronAPI | null {
  if (isElectron()) {
    return (window as any).electronAPI;
  }
  return null;
}

/**
 * Get the app version
 */
export async function getAppVersion(): Promise<string> {
  const api = getElectronAPI();
  if (api) {
    try {
      return await api.getAppVersion();
    } catch (error) {
      console.error('Failed to get app version:', error);
    }
  }
  return 'Web Version';
}

/**
 * Check for updates
 */
export async function checkForUpdates(): Promise<void> {
  const api = getElectronAPI();
  if (api) {
    try {
      await api.checkForUpdates();
    } catch (error) {
      console.error('Failed to check for updates:', error);
    }
  } else {
    console.log('Auto-update is only available in the desktop app');
  }
}

/**
 * Subscribe to update status changes
 */
export function onUpdateStatus(callback: (status: UpdateStatus) => void): void {
  const api = getElectronAPI();
  if (api) {
    api.onUpdateStatus(callback);
  }
}

/**
 * Subscribe to update progress
 */
export function onUpdateProgress(callback: (progress: UpdateProgress) => void): void {
  const api = getElectronAPI();
  if (api) {
    api.onUpdateProgress(callback);
  }
}

/**
 * Get platform information
 */
export function getPlatform(): string {
  const api = getElectronAPI();
  return api?.platform || 'web';
}

