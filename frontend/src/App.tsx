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

interface TimingStats {
  elapsedSeconds: number;
  estimatedRemainingSeconds: number;
  processingSpeed: number; // lines per second
}

interface AIMode {
  mode: 'free' | 'competitive' | 'premium';
  llmEnhancement: boolean;
  llmDetection: boolean;
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
  const [timingStats, setTimingStats] = useState<TimingStats | null>(null);
  const [aiMode, setAiMode] = useState<AIMode | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);

  const handleFileUpload = useCallback(async (
    file: File, 
    outputFilename: string, 
    outputFormat: OutputFormatEnum,
    categories: string[],
    useLLMEnhancement: boolean,
    useLLMDetection: boolean
  ) => {
    try {
      console.log('Starting file upload:', file.name);
      console.log('Selected categories:', categories);
      console.log('AI Enhancement:', useLLMEnhancement);
      console.log('AI Detection:', useLLMDetection);
      
      const mode = useLLMDetection && useLLMEnhancement ? 'Full AI' : 
                   useLLMEnhancement ? 'Enhancement Only' : 'Pattern-Only';
      console.log('Quality Mode:', mode);
      
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
      const uploadResponse = await uploadDocument(file, outputFilename, outputFormat, categories, useLLMEnhancement, useLLMDetection);
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
          console.log('📨 WebSocket data type:', data.type);
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
              // Set AI mode from backend
              if (data.ai_mode) {
                setAiMode({
                  mode: data.ai_mode,
                  llmEnhancement: data.llm_enhancement || false,
                  llmDetection: data.llm_detection || false
                });
              }
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
              
              // Update timing stats from backend
              if (data.timing) {
                setTimingStats({
                  elapsedSeconds: data.timing.elapsed_seconds || 0,
                  estimatedRemainingSeconds: data.timing.estimated_remaining_seconds || 0,
                  processingSpeed: data.timing.processing_speed || 0
                });
              }
              
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
              
            case 'enhancement_start':
              setLiveStats(prev => prev ? {
                ...prev,
                currentMessage: data.message || 'Starting AI enhancement...'
              } : null);
              break;
              
            case 'enhancement_progress':
              setLiveStats(prev => prev ? {
                ...prev,
                currentMessage: data.message || `Enhancing chunk ${data.chunk_number}/${data.total_chunks}...`
              } : null);
              break;
              
            case 'enhancement_complete':
              setLiveStats(prev => prev ? {
                ...prev,
                currentMessage: data.message || 'AI enhancement complete!'
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
              console.log('🎉 WebSocket received completed message!');
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
                  
                  console.log('📊 Results received:', results);
                  setIssues(results.issues || []);
                  setSummary(results.summary || {
                    total_issues: 0,
                    categories: {},
                    lines_with_issues: 0,
                    sentences_with_issues: 0
                  });
                  setEnhancement(results.enhancement || null);
                  
                  console.log('🎯 Setting showResults to true');
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
    setTimingStats(null);
    setAiMode(null);
  }, []);
  
  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Format time in human-readable format
  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}s`;
    } else if (seconds < 3600) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}m ${secs}s`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const mins = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${mins}m`;
    }
  };

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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        {/* Modern Header */}
        <div className="text-center mb-8">
          <div className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full mb-3">
            🏆 Premium Quality - Competitive with Grammarly
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI-Powered Grammar Checker
          </h1>
          <p className="text-sm text-gray-600 mb-1">
            470+ rules + GPT-4 intelligence • 95-98% accuracy
          </p>
          <p className="text-xs text-gray-500">
            50-75% cheaper than Grammarly Premium • Open source
          </p>
        </div>

        {/* Error Display */}
        {appState.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {appState.error}
          </div>
        )}

        {/* Processing Status */}
        {appState.isProcessing && (
          <div className="mb-6 p-5 bg-white rounded-xl border-2 border-blue-200 shadow-lg">
            {/* AI Mode Badge */}
            {aiMode && (
              <div className="mb-3 flex items-center justify-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                  aiMode.mode === 'premium' 
                    ? 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 border border-purple-200' 
                    : aiMode.mode === 'competitive'
                    ? 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border border-blue-200'
                    : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 border border-gray-300'
                }`}>
                  {aiMode.mode === 'premium' && '👑 Premium Mode'}
                  {aiMode.mode === 'competitive' && '🏆 Competitive Mode'}
                  {aiMode.mode === 'free' && '⚡ Free Mode'}
                  <span className="ml-2 text-xs opacity-75">
                    {aiMode.llmDetection && aiMode.llmEnhancement && '(AI Detection + Enhancement)'}
                    {aiMode.llmEnhancement && !aiMode.llmDetection && '(AI Enhancement)'}
                    {!aiMode.llmEnhancement && !aiMode.llmDetection && '(Pattern-Only)'}
                  </span>
                </div>
              </div>
            )}
            
            <div className="flex items-center mb-4">
              <div className="relative mr-4">
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-6 w-6 bg-blue-50 rounded-full"></div>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-900 mb-1">
                  {liveStats?.currentMessage || (appState.processingStatus ? getStatusMessage() : 'Processing...')}
                </h3>
                {appState.processingStatus && (
                  <div className="text-xs text-gray-600">
                    {appState.processingStatus.progress}% complete
                  </div>
                )}
              </div>
            </div>
            
            {/* Modern Progress Bar */}
            {appState.processingStatus && (
              <div className="w-full bg-gray-100 rounded-full h-2 mb-4 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${appState.processingStatus.progress}%` }}
                ></div>
              </div>
            )}
            
            {/* Timing Stats */}
            {timingStats && (
              <div className="mb-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div>
                    <div className="flex items-center justify-center mb-1">
                      <svg className="w-4 h-4 text-blue-600 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-xs font-medium text-gray-700">Elapsed</span>
                    </div>
                    <div className="text-lg font-bold text-blue-600">
                      {formatTime(timingStats.elapsedSeconds)}
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-center mb-1">
                      <svg className="w-4 h-4 text-indigo-600 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span className="text-xs font-medium text-gray-700">Speed</span>
                    </div>
                    <div className="text-lg font-bold text-indigo-600">
                      {timingStats.processingSpeed > 0 
                        ? `${timingStats.processingSpeed.toFixed(1)} l/s` 
                        : '-'}
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-center mb-1">
                      <svg className="w-4 h-4 text-green-600 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-xs font-medium text-gray-700">Remaining</span>
                    </div>
                    <div className="text-lg font-bold text-green-600">
                      {timingStats.estimatedRemainingSeconds > 0 
                        ? `~${formatTime(timingStats.estimatedRemainingSeconds)}` 
                        : 'Calculating...'}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Real-time Stats */}
            {liveStats && liveStats.totalLines > 0 && (
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <div className="text-lg font-bold text-gray-900">{liveStats.linesAnalyzed}</div>
                  <div className="text-xs text-gray-600">Lines Analyzed</div>
                </div>
                <div className="bg-blue-50 rounded-lg p-2 text-center">
                  <div className="text-lg font-bold text-blue-600">{liveStats.issuesFound}</div>
                  <div className="text-xs text-gray-600">Issues Found</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <div className="text-lg font-bold text-gray-900">{liveStats.totalLines}</div>
                  <div className="text-xs text-gray-600">Total Lines</div>
                </div>
              </div>
            )}
            
            {/* Cancel/New Document Button during processing */}
            <div className="mt-4 text-center">
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel & Start Over
              </button>
            </div>
          </div>
        )}

        {/* Main Content */}
        {!appState.isProcessing && !showResults ? (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <FileUpload 
              onFileUpload={handleFileUpload}
              disabled={appState.isProcessing}
            />
          </div>
        ) : showResults ? (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">Analysis Results</h2>
                {enhancement && enhancement.llm_detection_enabled && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">
                      ⭐ AI-Enhanced
                    </span>
                    {enhancement.issues_detected_by_llm > 0 && (
                      <span className="text-gray-600">
                        • {enhancement.issues_detected_by_llm} issues detected by AI
                      </span>
                    )}
                  </div>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleDownloadReport}
                  className="px-5 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
                >
                  Download Report
                </button>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
                >
                  New Document
                </button>
              </div>
            </div>
            {summary && (
              <IssuesPreview issues={issues} summary={summary} enhancement={enhancement} />
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default App;
