const { app, BrowserWindow, ipcMain, Tray, Menu, dialog } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow = null;
let backendProcess = null;
let tray = null;
const BACKEND_PORT = 8000;
const isDev = process.env.NODE_ENV === 'development';

// Configure auto-updater
autoUpdater.autoDownload = false;
autoUpdater.autoInstallOnAppQuit = true;

// Logging for auto-updater
autoUpdater.logger = require('electron-log');
autoUpdater.logger.transports.file.level = 'info';

// Get the correct paths for resources
function getResourcePath(filename) {
  if (isDev) {
    return path.join(__dirname, 'resources', filename);
  }
  // In production, resources are in the app.asar or extraResources
  return path.join(process.resourcesPath, filename);
}

// Check if backend is running
function checkBackendHealth(retries = 30, interval = 1000) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    
    const check = () => {
      attempts++;
      
      http.get(`http://localhost:${BACKEND_PORT}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('Backend is healthy!');
          resolve(true);
        } else if (attempts < retries) {
          setTimeout(check, interval);
        } else {
          reject(new Error('Backend health check failed'));
        }
      }).on('error', (err) => {
        if (attempts < retries) {
          console.log(`Backend not ready yet (attempt ${attempts}/${retries})...`);
          setTimeout(check, interval);
        } else {
          reject(new Error(`Backend failed to start: ${err.message}`));
        }
      });
    };
    
    check();
  });
}

// Start the Python backend process
async function startBackend() {
  return new Promise((resolve, reject) => {
    try {
      let backendPath;
      
      if (isDev) {
        // In development, run the Python script directly
        backendPath = path.join(__dirname, '..', 'backend', 'main.py');
        console.log('Starting backend in dev mode:', backendPath);
        
        // Use python3 command in development
        backendProcess = spawn('python3', [backendPath], {
          cwd: path.join(__dirname, '..', 'backend'),
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1'
          }
        });
      } else {
        // In production, run the bundled executable
        // Try both .exe (Windows) and no extension (Unix)
        let possiblePaths = [
          getResourcePath('backend.exe'),
          getResourcePath('backend')
        ];
        
        backendPath = null;
        for (let p of possiblePaths) {
          console.log('Checking for backend at:', p);
          if (fs.existsSync(p)) {
            backendPath = p;
            console.log('✓ Found backend at:', backendPath);
            break;
          }
        }
        
        if (!backendPath) {
          // Show detailed error with all checked paths and resource directory contents
          const resourceDir = path.join(process.resourcesPath);
          let errorMsg = `Backend executable not found!\n\n`;
          errorMsg += `Checked paths:\n`;
          possiblePaths.forEach(p => errorMsg += `  - ${p}\n`);
          errorMsg += `\nResource directory: ${resourceDir}\n`;
          errorMsg += `Contents:\n`;
          try {
            const files = fs.readdirSync(resourceDir);
            files.forEach(f => errorMsg += `  - ${f}\n`);
          } catch (e) {
            errorMsg += `  (Could not read directory: ${e.message})\n`;
          }
          console.error(errorMsg);
          reject(new Error(errorMsg));
          return;
        }
        
        console.log('Starting backend executable:', backendPath);
      }
        
        backendProcess = spawn(backendPath, [], {
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1'
          }
        });
      }
      
      backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data.toString()}`);
      });
      
      backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data.toString()}`);
      });
      
      backendProcess.on('error', (error) => {
        console.error('Failed to start backend:', error);
        reject(error);
      });
      
      backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
        if (code !== 0 && code !== null) {
          // Backend crashed, show error dialog
          if (mainWindow && !mainWindow.isDestroyed()) {
            dialog.showErrorBox(
              'Backend Error',
              'The backend process crashed unexpectedly. The application will now close.'
            );
            app.quit();
          }
        }
      });
      
      // Wait for backend to be ready
      console.log('Waiting for backend to be ready...');
      checkBackendHealth()
        .then(() => {
          console.log('Backend started successfully!');
          resolve();
        })
        .catch((error) => {
          console.error('Backend health check failed:', error);
          reject(error);
        });
      
    } catch (error) {
      console.error('Error starting backend:', error);
      reject(error);
    }
  });
}

// Stop the Python backend process
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend process...');
    backendProcess.kill();
    backendProcess = null;
  }
}

// Create the main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false
    },
    show: false, // Don't show until ready
    backgroundColor: '#ffffff'
  });

  // Load the React app
  if (isDev) {
    // In development, load from dev server
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load the built files
    const frontendPath = getResourcePath('frontend/index.html');
    mainWindow.loadFile(frontendPath);
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create system tray
function createTray() {
  const iconPath = path.join(__dirname, 'icon.png');
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
        }
      }
    },
    {
      label: 'Check for Updates',
      click: () => {
        checkForUpdates();
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('Grammar Correction App');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.show();
    }
  });
}

// Check for updates
function checkForUpdates() {
  if (isDev) {
    console.log('Skipping update check in development mode');
    return;
  }
  
  autoUpdater.checkForUpdates();
}

// Auto-updater event handlers
autoUpdater.on('checking-for-update', () => {
  console.log('Checking for updates...');
  if (mainWindow) {
    mainWindow.webContents.send('update-status', { status: 'checking' });
  }
});

autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info);
  if (mainWindow) {
    mainWindow.webContents.send('update-status', { 
      status: 'available', 
      version: info.version 
    });
  }
  
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Update Available',
    message: `A new version (${info.version}) is available. Do you want to download it now?`,
    buttons: ['Download', 'Later']
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.downloadUpdate();
    }
  });
});

autoUpdater.on('update-not-available', (info) => {
  console.log('Update not available');
  if (mainWindow) {
    mainWindow.webContents.send('update-status', { status: 'not-available' });
  }
});

autoUpdater.on('error', (err) => {
  console.error('Update error:', err);
  if (mainWindow) {
    mainWindow.webContents.send('update-status', { 
      status: 'error', 
      error: err.message 
    });
  }
});

autoUpdater.on('download-progress', (progressObj) => {
  console.log(`Download progress: ${progressObj.percent}%`);
  if (mainWindow) {
    mainWindow.webContents.send('update-progress', {
      percent: progressObj.percent,
      transferred: progressObj.transferred,
      total: progressObj.total
    });
  }
});

autoUpdater.on('update-downloaded', (info) => {
  console.log('Update downloaded');
  if (mainWindow) {
    mainWindow.webContents.send('update-status', { status: 'downloaded' });
  }
  
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Update Ready',
    message: 'Update downloaded. The application will restart to install the update.',
    buttons: ['Restart Now', 'Later']
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall(false, true);
    }
  });
});

// IPC handlers
ipcMain.handle('get-backend-url', () => {
  return `http://localhost:${BACKEND_PORT}`;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('check-for-updates', () => {
  checkForUpdates();
});

// App event handlers
app.on('ready', async () => {
  try {
    console.log('App is ready, starting backend...');
    
    // Start backend first
    await startBackend();
    
    // Create the main window
    createWindow();
    
    // Create system tray
    createTray();
    
    // Check for updates after 3 seconds
    setTimeout(() => {
      checkForUpdates();
    }, 3000);
    
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start the application: ${error.message}\n\nPlease make sure all dependencies are installed.`
    );
    app.quit();
  }
});

app.on('window-all-closed', () => {
  // On macOS, keep app running when windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});

app.on('will-quit', () => {
  stopBackend();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});

