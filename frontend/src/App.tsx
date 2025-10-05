import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, AlertCircle, Moon, Sun, Settings, History, FileText, Zap, Sparkles, TrendingUp } from 'lucide-react';
import FileUploadComponent from './components/FileUpload';
import ProgressTracker from './components/ProgressTracker';
import IssuesPreview from './components/IssuesPreview';
import { uploadDocument, getProcessingStatus, downloadReport, cleanupProcessing, healthCheck, WebSocketService, WebSocketMessage } from './services/api';
import { ProcessingStatus, OutputFormat } from './types';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Switch } from './components/ui/switch';
import { Alert, AlertDescription, AlertTitle } from './components/ui/alert';
import { cn } from './lib/utils';

function App() {
  const [currentStatus, setCurrentStatus] = useState<ProcessingStatus | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState<'upload' | 'history' | 'settings'>('upload');
  
  // WebSocket state
  const [wsService, setWsService] = useState<WebSocketService | null>(null);
  const [streamingIssues, setStreamingIssues] = useState<any[]>([]);
  const [streamingProgress, setStreamingProgress] = useState(0);
  const [skippedSentences, setSkippedSentences] = useState(0);
  const [lastProcessedLine, setLastProcessedLine] = useState(0);
  const [totalLines, setTotalLines] = useState(0);

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setApiHealthy(true);
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealthy(false);
      }
    };
    checkHealth();
  }, []);

  // WebSocket message handler
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    console.log('🔌 WebSocket message received in App:', message);
    
    switch (message.type) {
      case 'line_completed':
        console.log('🔌 Line completed message:', message);
        if (message.issues) {
          console.log('🔌 Adding issues from line:', message.issues.length);
          setStreamingIssues(prev => {
            const newIssues = [...prev, ...message.issues!];
            console.log('🔌 Total streaming issues now:', newIssues.length);
            return newIssues;
          });
        }
        if (message.progress) {
          setStreamingProgress(message.progress);
        }
        if (message.skipped_sentences) {
          setSkippedSentences(message.skipped_sentences);
        }
        if (message.line_number) {
          setLastProcessedLine(message.line_number);
        }
        if (message.total_lines) {
          setTotalLines(message.total_lines);
        }
        break;
        
      case 'processing_complete':
        console.log('🔌 Streaming processing completed');
        console.log('🔌 Processing complete message:', message);
        console.log('🔌 Current streaming issues count:', streamingIssues.length);
        
        // Update final status to completed using functional update
        setCurrentStatus(prevStatus => {
          if (!prevStatus) return prevStatus;
          
          console.log('🔌 Updating status to completed with', streamingIssues.length, 'issues');
          
          const newStatus = {
            ...prevStatus,
            status: 'completed' as const,
            progress: 100,
            message: 'Processing completed successfully',
            issues: streamingIssues,
            summary: {
              total_issues: streamingIssues.length,
              verb_tense_consistency: streamingIssues.filter(i => i.issue_type === 'verb_tense_consistency').length,
              awkward_phrasing: streamingIssues.filter(i => i.issue_type === 'awkward_phrasing').length,
              redundancy: streamingIssues.filter(i => i.issue_type === 'redundancy').length,
              grammar_punctuation: streamingIssues.filter(i => i.issue_type === 'grammar_punctuation').length,
            }
          };
          
          console.log('🔌 New status with issues:', newStatus.issues?.length || 0);
          console.log('🔌 New status summary:', newStatus.summary);
          
          return newStatus;
        });
        
        // Set processing to false to trigger UI transition
        setIsProcessing(false);
        
        // Disconnect WebSocket
        if (wsService) {
          wsService.disconnect();
          setWsService(null);
        }
        break;
        
      case 'status_update':
        console.log('Status update:', message.message);
        break;
        
      case 'error':
        console.error('WebSocket error:', message.error);
        if (wsService) {
          wsService.disconnect();
          setWsService(null);
        }
        break;
    }
  };

  // Poll for status updates when processing (fallback for non-WebSocket updates)
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    
    // Poll if processing and either no WebSocket or WebSocket might have issues
    if (currentStatus && isProcessing && currentStatus.status !== 'completed' && currentStatus.status !== 'error') {
      interval = setInterval(async () => {
        try {
          console.log('Polling status for ID:', currentStatus.id);
          const updatedStatus = await getProcessingStatus(currentStatus.id);
          console.log('Status update:', updatedStatus);
          console.log('Status progress:', updatedStatus.progress);
          console.log('Status stage:', updatedStatus.stage_name);
          console.log('Status ETA:', updatedStatus.estimated_time_remaining);
          
          // Update status if it has changed
          if (updatedStatus.status !== currentStatus.status || updatedStatus.progress !== currentStatus.progress) {
            setCurrentStatus(updatedStatus);
          }
          
          // Check for completion
          if (updatedStatus.status === 'completed') {
            console.log('Processing finished with status:', updatedStatus.status);
            console.log('Final status issues:', updatedStatus.issues?.length || 0);
            console.log('Final status summary:', updatedStatus.summary);
            setCurrentStatus(updatedStatus);
            setIsProcessing(false);
            clearInterval(interval);
          } else if (updatedStatus.status === 'error') {
            console.log('Processing failed with status:', updatedStatus.status);
            setIsProcessing(false);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error polling status:', error);
          setIsProcessing(false);
          clearInterval(interval);
        }
      }, 3000); // Poll every 3 seconds (reduced frequency)
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [currentStatus, isProcessing]);

  // Cleanup WebSocket on component unmount
  useEffect(() => {
    return () => {
      if (wsService) {
        wsService.disconnect();
      }
    };
  }, [wsService]);

  const handleFileUpload = async (file: File, outputFormat: OutputFormat, customFilename?: string) => {
    try {
      setIsProcessing(true);
      setIsUploading(true);
      setUploadProgress(0);
      console.log('Starting upload for file:', file.name, 'Size:', (file.size / 1024 / 1024).toFixed(2), 'MB');
      
      // Add timeout handling for large files
      const uploadPromise = uploadDocument(file, outputFormat, customFilename, (progress: number) => {
        setUploadProgress(progress);
      });
      
      // Set a reasonable timeout for large files (15 minutes)
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Upload timeout: File is too large or connection is slow')), 15 * 60 * 1000);
      });
      
      const response = await Promise.race([uploadPromise, timeoutPromise]) as any;
      console.log('Upload response:', response);
      
      setIsUploading(false);
      
      // Get initial status after upload
      const status = await getProcessingStatus(response.processing_id);
      console.log('Initial status:', status);
      setCurrentStatus(status);
      
      // Reset streaming state
      setStreamingIssues([]);
      setStreamingProgress(0);
      setSkippedSentences(0);
      setLastProcessedLine(0);
      setTotalLines(0);
      
      // Establish WebSocket connection for real-time streaming updates
      console.log('🔌 Establishing WebSocket connection for:', response.processing_id);
      const ws = new WebSocketService();
      ws.connect(
        response.processing_id,
        handleWebSocketMessage,
        (error) => {
          console.error('❌ WebSocket error:', error);
          setWsService(null);
        },
        () => {
          console.log('🔌 WebSocket disconnected');
          setWsService(null);
        }
      );
      setWsService(ws);
      console.log('🔌 WebSocket service created and connected');
    } catch (error) {
      console.error('Upload failed:', error);
      setIsUploading(false);
      
      let errorMessage = 'Upload failed. Please try again.';
      if (error instanceof Error) {
        if (error.message.includes('timeout')) {
          errorMessage = 'Upload timeout: The file is too large or your connection is slow. Please try a smaller file or check your internet connection.';
        } else if (error.message.includes('Network error')) {
          errorMessage = 'Network error: Unable to connect to server. Please check your internet connection and try again.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setCurrentStatus({
        id: 'error',
        status: 'error',
        progress: 0,
        message: errorMessage,
        filename: file.name,
        output_format: outputFormat,
        custom_filename: customFilename,
        issues: [],
        summary: undefined,
      });
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!currentStatus) return;
    
    try {
      const blob = await downloadReport(currentStatus.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = currentStatus.output_filename || `grammar_report.${currentStatus.output_format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  const handleNewUpload = () => {
    setCurrentStatus(null);
    setIsProcessing(false);
    setIsUploading(false);
    setUploadProgress(0);
  };

  const handleCleanup = async () => {
    if (currentStatus && currentStatus.id !== 'error') {
      try {
        await cleanupProcessing(currentStatus.id);
      } catch (error) {
        console.error('Cleanup failed:', error);
      }
    }
    handleNewUpload();
  };

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className={cn("min-h-screen transition-colors duration-300", darkMode ? "bg-background" : "bg-gradient-to-br from-gray-50 via-white to-slate-50")}>
      {/* Header */}
      <header className={cn("border-b sticky top-0 z-50", darkMode ? "bg-card/80 backdrop-blur-sm border-border" : "bg-white/80 backdrop-blur-sm border-border")}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-gray-600 to-slate-700 rounded-lg">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-foreground">
                    GrammarAI Pro
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Professional Grammar & Style Correction
                  </p>
                </div>
              </div>
            </div>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              <Button
                variant={currentView === 'upload' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('upload')}
                className="gap-2"
              >
                <FileText className="h-4 w-4" />
                Upload
              </Button>
              <Button
                variant={currentView === 'history' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('history')}
                className="gap-2"
              >
                <History className="h-4 w-4" />
                History
              </Button>
            </nav>
            
            <div className="flex items-center space-x-4">
              {/* API Status */}
              <div className="flex items-center space-x-2">
                {apiHealthy === null ? (
                  <div className="h-2 w-2 bg-muted-foreground rounded-full animate-pulse"></div>
                ) : apiHealthy ? (
                  <CheckCircle className="h-5 w-5 text-gray-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-destructive" />
                )}
                <span className="text-sm text-muted-foreground">
                  {apiHealthy === null ? 'Checking...' : apiHealthy ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {/* Streaming Status */}
              {wsService && wsService.isConnected() && (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-600 font-medium">
                    Live Processing
                  </span>
                </div>
              )}
              
              {/* Dark Mode Toggle */}
              <div className="flex items-center space-x-2">
                <Sun className="h-4 w-4" />
                <Switch
                  checked={darkMode}
                  onCheckedChange={setDarkMode}
                />
                <Moon className="h-4 w-4" />
              </div>
              
              {/* Settings */}
              <Button
                variant={currentView === 'settings' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setCurrentView('settings')}
              >
                <Settings className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload View */}
        {currentView === 'upload' && (
          <>
            {!currentStatus && !isProcessing ? (
              <div className="space-y-8">
                <FileUploadComponent
                  onFileSelect={handleFileUpload}
                  disabled={isProcessing || apiHealthy === false}
                  darkMode={darkMode}
                />
              </div>
            ) : currentStatus?.status === 'completed' ? (
              <div className="space-y-6">
                <IssuesPreview
                  issues={currentStatus.issues}
                  summary={currentStatus.summary!}
                  onDownload={handleDownload}
                  darkMode={darkMode}
                />
                <div className="text-center">
                  <Button
                    onClick={handleCleanup}
                    size="lg"
                    className="gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Upload Another Document
                  </Button>
                </div>
              </div>
            ) : (currentStatus || isProcessing) ? (
              <div className="space-y-6">
                {isUploading ? (
                  <Card className="w-full max-w-2xl mx-auto">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Upload className="h-5 w-5" />
                        Uploading File
                      </CardTitle>
                      <CardDescription>
                        Please wait while your file is being uploaded...
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Upload Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Upload Progress</span>
                          <span className="font-medium">{uploadProgress}%</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-3">
                          <div
                            className="bg-primary h-3 rounded-full transition-all duration-300 ease-out"
                            style={{ width: `${uploadProgress}%` }}
                          />
                        </div>
                        <div className="text-xs text-muted-foreground text-center">
                          {uploadProgress < 10 ? 'Starting upload...' : 
                           uploadProgress < 50 ? 'Uploading file...' :
                           uploadProgress < 90 ? 'Almost done...' : 'Finalizing upload...'}
                        </div>
                      </div>
                      
                      {/* Large File Warning */}
                      {uploadProgress > 0 && uploadProgress < 10 && (
                        <Alert>
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>Large File Detected</AlertTitle>
                          <AlertDescription>
                            Large files may take several minutes to upload. Please keep this window open and don't refresh the page.
                          </AlertDescription>
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                ) : currentStatus ? (
                  <div className="space-y-4">
                    <ProgressTracker 
                      status={currentStatus} 
                      streamingProgress={wsService && wsService.isConnected() ? streamingProgress : undefined}
                      streamingIssues={wsService && wsService.isConnected() ? streamingIssues : undefined}
                      skippedSentences={wsService && wsService.isConnected() ? skippedSentences : undefined}
                    />
                    
                    {/* Streaming Progress Information */}
                    {((wsService && wsService.isConnected()) || (streamingProgress > 0 && streamingIssues.length > 0)) && (
                      <div className="space-y-4">
                        <Card className="w-full max-w-2xl mx-auto">
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                              <Zap className="h-5 w-5 text-blue-500" />
                              Real-time Processing
                            </CardTitle>
                            <CardDescription>
                              Processing sentences individually with streaming updates
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div className="flex justify-between items-center">
                                <span className="text-sm font-medium">Issues Found:</span>
                                <Badge variant="secondary" className="animate-pulse">{streamingIssues.length}</Badge>
                              </div>
                              {skippedSentences > 0 && (
                                <div className="flex justify-between items-center">
                                  <span className="text-sm font-medium">Skipped Sentences:</span>
                                  <Badge variant="outline">{skippedSentences}</Badge>
                                </div>
                              )}
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-blue-500 h-3 rounded-full transition-all duration-300" 
                                style={{ width: `${streamingProgress}%` }}
                              ></div>
                            </div>
                            <p className="text-sm text-muted-foreground text-center">
                              {streamingProgress}% complete
                            </p>
                          </CardContent>
                        </Card>

                        {/* Real-time Processing Status */}
                        <Card className="w-full max-w-2xl mx-auto">
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                              <Zap className="h-5 w-5 text-green-500" />
                              Live Processing Status
                            </CardTitle>
                            <CardDescription>
                              Real-time line processing updates
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                  <div className="text-lg font-semibold text-green-600">
                                    {streamingProgress}%
                                  </div>
                                  <div className="text-xs text-green-500">Complete</div>
                                </div>
                                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                  <div className="text-lg font-semibold text-blue-600">
                                    {streamingIssues.length}
                                  </div>
                                  <div className="text-xs text-blue-500">Issues Found</div>
                                </div>
                                {skippedSentences > 0 && (
                                  <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                    <div className="text-lg font-semibold text-orange-600">
                                      {skippedSentences}
                                    </div>
                                    <div className="text-xs text-orange-500">Skipped</div>
                                  </div>
                                )}
                              </div>
                              
                              <div className="text-center">
                                <p className="text-sm text-muted-foreground">
                                  Processing lines in real-time...
                                </p>
                                {lastProcessedLine > 0 && totalLines > 0 && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Line {lastProcessedLine} of {totalLines} processed
                                  </p>
                                )}
                                <div className="flex items-center justify-center gap-2 mt-2">
                                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-green-600">Active</span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        {/* Real-time Issues Display */}
                        {streamingIssues.length > 0 && (
                          <Card className="w-full max-w-2xl mx-auto">
                            <CardHeader>
                              <CardTitle className="flex items-center gap-2">
                                <AlertCircle className="h-5 w-5 text-orange-500" />
                                Issues Found (Real-time)
                              </CardTitle>
                              <CardDescription>
                                Issues discovered during processing
                              </CardDescription>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3 max-h-64 overflow-y-auto">
                                {streamingIssues.slice(-10).map((issue, index) => (
                                  <div key={index} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                    <div className="flex items-start justify-between">
                                      <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                          <Badge variant="outline" className="text-xs">
                                            Line {issue.line_number || issue.lines}
                                          </Badge>
                                          <Badge variant="secondary" className="text-xs">
                                            {issue.issue_type || 'Grammar'}
                                          </Badge>
                                        </div>
                                        <p className="text-sm font-medium text-gray-900 mb-1">
                                          {issue.original_text}
                                        </p>
                                        <p className="text-sm text-gray-600">
                                          <span className="font-medium">Suggestion:</span> {issue.suggested_text}
                                        </p>
                                        {issue.explanation && (
                                          <p className="text-xs text-gray-500 mt-1">
                                            {issue.explanation}
                                          </p>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                                {streamingIssues.length > 10 && (
                                  <p className="text-xs text-muted-foreground text-center">
                                    Showing latest 10 issues. Total: {streamingIssues.length}
                                  </p>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <Card className="w-full max-w-2xl mx-auto">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-muted-foreground">Starting document analysis...</p>
                      <p className="text-xs text-muted-foreground mt-2">
                        Please wait while we prepare your document for processing
                      </p>
                    </CardContent>
                  </Card>
                )}
                {currentStatus?.status === 'error' && (
                  <div className="text-center">
                    <Button
                      onClick={handleNewUpload}
                      variant="outline"
                      size="lg"
                    >
                      Try Again
                    </Button>
                  </div>
                )}
              </div>
            ) : null}
          </>
        )}


        {/* History View */}
        {currentView === 'history' && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-gray-600 to-slate-700 rounded-full">
                <History className="h-8 w-8 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-foreground">Processing History</h2>
                <p className="text-lg text-muted-foreground mt-2">
                  View your previous document processing sessions
                </p>
              </div>
            </div>
            
            {currentStatus ? (
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-foreground">
                        {currentStatus.filename}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Processed on {new Date().toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={currentStatus.status === 'completed' ? 'default' : 'secondary'}>
                        {currentStatus.status}
                      </Badge>
                      <Button
                        onClick={handleDownload}
                        size="sm"
                        className="gap-2"
                      >
                        <Upload className="h-4 w-4" />
                        Download
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-muted-foreground">No processing history available</p>
                  <p className="text-sm text-muted-foreground mt-2">Upload a document to get started</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Settings View */}
        {currentView === 'settings' && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-gray-600 to-slate-700 rounded-full">
                <Settings className="h-8 w-8 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-foreground">Settings</h2>
                <p className="text-lg text-muted-foreground mt-2">
                  Customize your grammar checking experience
                </p>
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Theme Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Appearance</CardTitle>
                  <CardDescription>
                    Customize the look and feel of the application
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-foreground">
                        Dark Mode
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Switch between light and dark themes
                      </p>
                    </div>
                    <Switch
                      checked={darkMode}
                      onCheckedChange={setDarkMode}
                    />
                  </div>
                </CardContent>
              </Card>
              
              {/* Processing Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Processing Options</CardTitle>
                  <CardDescription>
                    Configure how your documents are processed
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="autoDownload"
                      className="h-4 w-4 text-primary rounded"
                    />
                    <label htmlFor="autoDownload" className="text-sm text-foreground">
                      Auto-download reports when processing completes
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="emailNotifications"
                      className="h-4 w-4 text-primary rounded"
                    />
                    <label htmlFor="emailNotifications" className="text-sm text-foreground">
                      Email notifications for processing updates
                    </label>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-12 bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>
              GrammarAI Pro - Professional Grammar & Style Correction
            </p>
            <p className="mt-2">
              Supports .doc and .docx files up to 50MB • Powered by AI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
