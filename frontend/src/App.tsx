import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { FileUpload } from './components/FileUpload';
import { IssuesPreview } from './components/IssuesPreview';
import { uploadDocument, pollStatus, downloadReport, downloadFile, checkHealth, getProcessingResults } from './services/api';
import { 
  AppState, 
  ProcessingStatus, 
  ProcessingResult, 
  OutputFormatEnum,
  GrammarIssue,
  IssuesSummary,
  ProcessingStatusEnum
} from './types';

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
  const [showResults, setShowResults] = useState(false);

  const handleFileUpload = useCallback(async (
    file: File, 
    outputFilename: string, 
    outputFormat: OutputFormatEnum
  ) => {
    try {
      setAppState(prev => ({
        ...prev,
        isProcessing: true,
        error: null,
        uploadedFile: file,
        outputFilename,
        outputFormat
      }));

      // Upload the document
      const uploadResponse = await uploadDocument(file, outputFilename, outputFormat);
      
      setAppState(prev => ({
        ...prev,
        currentTask: uploadResponse.task_id
      }));

      // Start polling for status updates
      pollStatus(
        uploadResponse.task_id,
        (status: ProcessingStatus) => {
          setAppState(prev => ({
            ...prev,
            processingStatus: status
          }));
        },
        async (status: ProcessingStatus) => {
          // Processing completed
          setAppState(prev => ({
            ...prev,
            isProcessing: false,
            processingStatus: status
          }));

          // Download and process the results
          try {
            // Download the report file
            const blob = await downloadReport(uploadResponse.task_id);
            const filename = `${outputFilename}.${outputFormat}`;
            downloadFile(blob, filename);
            
            // Fetch the actual issues and summary data
            const results = await getProcessingResults(uploadResponse.task_id);
            
            // Set the real issues data
            setIssues(results.issues || []);
            setSummary(results.summary || {
              total_issues: 0,
              categories: {},
              lines_with_issues: 0,
              sentences_with_issues: 0
            });

            setShowResults(true);
          } catch (error) {
            setAppState(prev => ({
              ...prev,
              error: 'Failed to download results'
            }));
          }
        },
        (error: string) => {
          setAppState(prev => ({
            ...prev,
            isProcessing: false,
            error: error
          }));
        }
      );
    } catch (error: any) {
      setAppState(prev => ({
        ...prev,
        isProcessing: false,
        error: error.message || 'Upload failed'
      }));
    }
  }, []);

  const handleReset = useCallback(() => {
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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI-Powered Grammar Correction
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Upload your Word document and get comprehensive grammar and style analysis
            </p>
          </div>

          {/* Error Display */}
          {appState.error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{appState.error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Status Display */}
          {appState.isProcessing && appState.processingStatus && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">Processing</h3>
                  <p className="text-sm text-blue-700 mt-1">{getStatusMessage()}</p>
                </div>
              </div>
            </div>
          )}

          {/* Main Content */}
          {!showResults ? (
            <FileUpload 
              onFileUpload={handleFileUpload}
              disabled={appState.isProcessing}
            />
          ) : (
            <div className="space-y-6">
              {/* Results Header */}
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
                <button
                  onClick={handleReset}
                  className="btn-secondary"
                >
                  Upload New Document
                </button>
              </div>

              {/* Issues Preview */}
              {summary && (
                <IssuesPreview issues={issues} summary={summary} />
              )}
            </div>
          )}

          {/* Features Section */}
          <div id="features" className="mt-16">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              Features
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Document Upload</h3>
                <p className="text-gray-600">
                  Upload Word documents (.doc/.docx) up to 10MB for comprehensive analysis.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Analysis</h3>
                <p className="text-gray-600">
                  Hybrid NLP technology combining spaCy and LanguageTool for enhanced accuracy.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Multiple Formats</h3>
                <p className="text-gray-600">
                  Download your corrected document in DOCX or PDF format with detailed reports.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default App;
