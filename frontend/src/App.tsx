import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FileUpload } from './components/FileUpload';
import { IssuesPreview } from './components/IssuesPreview';
import { uploadDocument, pollStatus, downloadReport, downloadFile, checkHealth, getProcessingResults, getProcessingStatus, connectWebSocket } from './services/api';
import { 
  AppState, 
  ProcessingStatus, 
  ProcessingResult, 
  OutputFormatEnum,
  GrammarIssue,
  IssuesSummary,
  ProcessingStatusEnum
} from './types';

interface LiveStats {
  totalLines: number;
  linesAnalyzed: number;
  issuesFound: number;
  currentMessage: string;
}

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    currentTask: null,
    processingStatus: null,
    isProcessing: false,
    error: null,
    uploadedFile: null,
    outputFilename: '',
    outputFormat: OutputFormatEnum.DOCX
  });

  const [issues, setIssues] = useState<GrammarIssue[]>([]);
  const [summary, setSummary] = useState<IssuesSummary | null>(null);
  const [enhancement, setEnhancement] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);
  const [liveStats, setLiveStats] = useState<LiveStats | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);

  const handleFileUpload = useCallback(async (
    file: File, 
    outputFilename: string, 
    outputFormat: OutputFormatEnum,
    categories: string[],
    useLLMEnhancement: boolean
  ) => {
    try {
      console.log('Starting file upload:', file.name);
      console.log('Selected categories:', categories);
      console.log('LLM Enhancement:', useLLMEnhancement);
      
      setAppState(prev => ({
        ...prev,
        isProcessing: true,
        error: null,
        uploadedFile: file,
        outputFilename,
        outputFormat
      }));

      // Upload the document
      console.log('Uploading document...');
      const uploadResponse = await uploadDocument(file, outputFilename, outputFormat, categories, useLLMEnhancement);
      console.log('Upload response:', uploadResponse);
      
      // Set task ID
      setAppState(prev => ({
        ...prev,
        currentTask: uploadResponse.task_id
      }));

      // Try to connect to WebSocket for real-time updates
      console.log('🔌 Attempting WebSocket connection...');
      let wsConnected = false;
      
      const ws = connectWebSocket(
        uploadResponse.task_id,
        (data) => {
          console.log('📨 WebSocket data:', data);
          wsConnected = true;
          
          // Handle different message types
          switch (data.type) {
            case 'starting':
              setLiveStats({
                totalLines: 0,
                linesAnalyzed: 0,
                issuesFound: 0,
                currentMessage: data.message || 'Starting analysis...'
              });
              break;
              
            case 'parsed':
              setLiveStats({
                totalLines: data.total_lines || 0,
                linesAnalyzed: 0,
                issuesFound: 0,
                currentMessage: data.message || `Analyzing ${data.total_lines} lines...`
              });
              setAppState(prev => ({
                ...prev,
                processingStatus: {
                  task_id: uploadResponse.task_id,
                  status: ProcessingStatusEnum.CHECKING,
                  progress: data.progress || 30,
                  message: data.message
                }
              }));
              break;
              
            case 'progress':
              setLiveStats({
                totalLines: data.total_lines || 0,
                linesAnalyzed: data.lines_analyzed || 0,
                issuesFound: data.issues_found || 0,
                currentMessage: data.message || 'Analyzing...'
              });
              setAppState(prev => ({
                ...prev,
                processingStatus: {
                  task_id: uploadResponse.task_id,
                  status: (data.status as ProcessingStatusEnum) || ProcessingStatusEnum.CHECKING,
                  progress: data.progress || 0,
                  message: data.message
                }
              }));
              break;
              
            case 'analysis_complete':
              setLiveStats(prev => prev ? {
                ...prev,
                currentMessage: data.message || 'Analysis complete!'
              } : null);
              break;
              
            case 'status':
              setAppState(prev => ({
                ...prev,
                processingStatus: {
                  task_id: uploadResponse.task_id,
                  status: (data.status as ProcessingStatusEnum) || ProcessingStatusEnum.UPLOADED,
                  progress: data.progress || 0,
                  message: data.message
                }
              }));
              break;
              
            case 'completed':
              setAppState(prev => ({
                ...prev,
                isProcessing: false,
                processingStatus: {
                  task_id: uploadResponse.task_id,
                  status: ProcessingStatusEnum.COMPLETED,
                  progress: 100,
                  message: data.message || 'Processing completed!'
                }
              }));
              
              // Fetch results (no auto-download)
              (async () => {
                try {
                  console.log('Fetching results...');
                  const results = await getProcessingResults(uploadResponse.task_id);
                  
                  setIssues(results.issues || []);
                  setSummary(results.summary || {
                    total_issues: 0,
                    categories: {},
                    lines_with_issues: 0,
                    sentences_with_issues: 0
                  });
                  setEnhancement(results.enhancement || null);
                  
                  setShowResults(true);
                  setLiveStats(null); // Clear live stats when done
                } catch (error) {
                  console.error('Error fetching results:', error);
                  setAppState(prev => ({
                    ...prev,
                    error: 'Failed to fetch results'
                  }));
                }
              })();
              break;
              
            case 'error':
              setAppState(prev => ({
                ...prev,
                isProcessing: false,
                error: data.message || 'Processing failed'
              }));
              setLiveStats(null);
              break;
          }
        },
        (error) => {
          console.error('❌ WebSocket error - falling back to polling:', error);
          wsConnected = false;
        },
        () => {
          console.log('🔌 WebSocket closed');
          wsRef.current = null;
        }
      );
      
      wsRef.current = ws;
      
      // Fallback to polling if WebSocket doesn't connect within 2 seconds
      setTimeout(() => {
        if (!wsConnected) {
          console.warn('⚠️ WebSocket not connected, falling back to polling');
          
          // Start polling as fallback
      pollStatus(
        uploadResponse.task_id,
        (status: ProcessingStatus) => {
              console.log('📊 Polling status update:', status);
          setAppState(prev => ({
            ...prev,
            processingStatus: status
          }));
        },
        async (status: ProcessingStatus) => {
          // Processing completed
              console.log('✅ Processing completed (via polling)!');
          
          setAppState(prev => ({
            ...prev,
            isProcessing: false,
            processingStatus: status
          }));

          // Fetch the results (no auto-download)
          try {
            console.log('Fetching results...');
            const results = await getProcessingResults(uploadResponse.task_id);
            
            setIssues(results.issues || []);
            setSummary(results.summary || {
              total_issues: 0,
              categories: {},
              lines_with_issues: 0,
              sentences_with_issues: 0
            });
            setEnhancement(results.enhancement || null);

            setShowResults(true);
                setLiveStats(null);
          } catch (error) {
            console.error('Error fetching results:', error);
            setAppState(prev => ({
              ...prev,
              error: 'Failed to fetch results'
            }));
          }
        },
        (error: string) => {
          console.error('Processing error:', error);
          setAppState(prev => ({
            ...prev,
            isProcessing: false,
            error: error
          }));
        }
      );
        }
      }, 2000);
    } catch (error: any) {
      setAppState(prev => ({
        ...prev,
        isProcessing: false,
        error: error.message || 'Upload failed'
      }));
    }
  }, []);

  const handleDownloadReport = useCallback(async () => {
    if (!appState.currentTask || !appState.outputFilename) return;
    
    try {
      console.log('Downloading report...');
      const blob = await downloadReport(appState.currentTask);
      const filename = `${appState.outputFilename}.${appState.outputFormat}`;
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Error downloading report:', error);
      setAppState(prev => ({
        ...prev,
        error: 'Failed to download report'
      }));
    }
  }, [appState.currentTask, appState.outputFilename, appState.outputFormat]);

  const handleReset = useCallback(() => {
    // Close WebSocket connection if exists
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setAppState({
      currentTask: null,
      processingStatus: null,
      isProcessing: false,
      error: null,
      uploadedFile: null,
      outputFilename: '',
      outputFormat: OutputFormatEnum.DOCX
    });
    setIssues([]);
    setSummary(null);
    setShowResults(false);
    setLiveStats(null);
  }, []);
  
  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getStatusMessage = () => {
    if (!appState.processingStatus) return '';
    
    const status = appState.processingStatus.status;
    const progress = appState.processingStatus.progress;
    
    switch (status) {
      case ProcessingStatusEnum.UPLOADED:
        return 'Document uploaded successfully';
      case ProcessingStatusEnum.PARSING:
        return `Parsing document... ${progress}%`;
      case ProcessingStatusEnum.CHECKING:
        return `Analyzing grammar and style... ${progress}%`;
      case ProcessingStatusEnum.GENERATING:
        return `Generating report... ${progress}%`;
      case ProcessingStatusEnum.COMPLETED:
        return 'Analysis completed successfully';
      case ProcessingStatusEnum.ERROR:
        return 'Analysis failed';
      default:
        return 'Processing...';
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Minimal Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">Grammar Checker</h1>
          <p className="text-sm text-gray-500">Upload a document to analyze</p>
        </div>

        {/* Error Display */}
        {appState.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {appState.error}
          </div>
        )}

        {/* Processing Status */}
        {appState.isProcessing && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center mb-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 mr-3"></div>
              <span className="text-sm text-gray-700">
                {liveStats?.currentMessage || (appState.processingStatus ? getStatusMessage() : 'Processing...')}
              </span>
            </div>
            
            {/* Progress Bar */}
            {appState.processingStatus && (
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div 
                  className="bg-gray-900 h-1 rounded-full transition-all"
                  style={{ width: `${appState.processingStatus.progress}%` }}
                ></div>
              </div>
            )}
            
            {/* Minimal Stats */}
            {liveStats && liveStats.totalLines > 0 && (
              <div className="flex gap-4 mt-3 text-xs text-gray-600">
                <span>Lines: {liveStats.linesAnalyzed}/{liveStats.totalLines}</span>
                <span>Issues: {liveStats.issuesFound}</span>
              </div>
            )}
          </div>
        )}

        {/* Main Content */}
        {!showResults ? (
          <FileUpload 
            onFileUpload={handleFileUpload}
            disabled={appState.isProcessing}
          />
        ) : (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-medium text-gray-900">Results</h2>
              <div className="flex gap-3">
                <button
                  onClick={handleDownloadReport}
                  className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition-colors"
                >
                  Download Report
                </button>
                <button
                  onClick={handleReset}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  New Document
                </button>
              </div>
            </div>
            {summary && (
              <IssuesPreview issues={issues} summary={summary} enhancement={enhancement} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
