import React from 'react';
import { CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';
import { ProcessingStatus } from '../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { cn } from '../lib/utils';

interface ProgressTrackerProps {
  status: ProcessingStatus;
  streamingProgress?: number;
  streamingIssues?: any[];
  skippedSentences?: number;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ status, streamingProgress, streamingIssues, skippedSentences }) => {
  const formatETA = (seconds: number | undefined): string => {
    if (!seconds || seconds <= 0) return "Almost done";
    
    if (seconds < 60) {
      return `${seconds} seconds`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      if (remainingSeconds === 0) {
        return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
      } else {
        return `${minutes}m ${remainingSeconds}s`;
      }
    } else {
      const hours = Math.floor(seconds / 3600);
      const remainingMinutes = Math.floor((seconds % 3600) / 60);
      if (remainingMinutes === 0) {
        return `${hours} hour${hours !== 1 ? 's' : ''}`;
      } else {
        return `${hours}h ${remainingMinutes}m`;
      }
    }
  };

  const getStatusIcon = (currentStatus: string, targetStatus: string) => {
    if (currentStatus === 'error') {
      return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
    
    if (currentStatus === 'completed') {
      return <CheckCircle className="h-5 w-5 text-gray-600" />;
    }
    
    if (currentStatus === targetStatus) {
      return <Clock className="h-5 w-5 text-primary-500 animate-spin" />;
    }
    
    if (isStatusCompleted(currentStatus, targetStatus)) {
      return <CheckCircle className="h-5 w-5 text-gray-600" />;
    }
    
    return <div className="h-5 w-5 border-2 border-gray-300 rounded-full" />;
  };

  const isStatusCompleted = (current: string, target: string) => {
    const statusOrder = ['uploading', 'parsing', 'checking_grammar', 'generating_report', 'completed'];
    const currentIndex = statusOrder.indexOf(current);
    const targetIndex = statusOrder.indexOf(target);
    return currentIndex > targetIndex;
  };

  const getStatusText = (statusName: string) => {
    switch (statusName) {
      case 'uploading':
        return 'Uploading File';
      case 'parsing':
        return 'Parsing Document';
      case 'checking_grammar':
        return 'Checking Grammar';
      case 'generating_report':
        return 'Generating Report';
      case 'completed':
        return 'Completed';
      case 'error':
        return 'Error';
      default:
        return statusName;
    }
  };

  const getStatusColor = (statusName: string) => {
    if (statusName === 'error') return 'text-gray-600';
    if (statusName === 'completed') return 'text-gray-600';
    if (status.status === statusName) return 'text-primary-600 font-medium';
    if (isStatusCompleted(status.status, statusName)) return 'text-gray-600';
    return 'text-gray-500';
  };

  const steps = ['uploading', 'parsing', 'checking_grammar', 'generating_report', 'completed'];

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Processing Status</CardTitle>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
              <span className="text-sm text-muted-foreground">Processing...</span>
            </div>
          </div>
        </div>
        <CardDescription>
          {status.message || `Processing ${status.filename}...`}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">

        {/* Progress Bar */}
        <div className="space-y-4">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <div className="flex items-center space-x-4">
              <span className="font-medium">
                {streamingProgress !== undefined ? streamingProgress : status.progress}%
              </span>
              {status.estimated_time_remaining !== undefined && status.estimated_time_remaining > 0 && (
                <span className="text-xs text-muted-foreground">
                  ETA: {formatETA(status.estimated_time_remaining)}
                </span>
              )}
            </div>
          </div>
          <Progress 
            value={streamingProgress !== undefined ? streamingProgress : status.progress} 
            className="h-3" 
          />
          
          {/* Streaming Stats */}
          {streamingProgress !== undefined && (
            <div className="grid grid-cols-2 gap-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-center">
                <div className="text-lg font-semibold text-blue-600">
                  {streamingIssues?.length || 0}
                </div>
                <div className="text-xs text-blue-500">Issues Found</div>
              </div>
              {skippedSentences !== undefined && skippedSentences > 0 && (
                <div className="text-center">
                  <div className="text-lg font-semibold text-orange-600">
                    {skippedSentences}
                  </div>
                  <div className="text-xs text-orange-500">Skipped</div>
                </div>
              )}
            </div>
          )}
          
          {/* Stage Progress */}
          {status.current_stage && status.total_stages && status.stage_name && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Stage {status.current_stage} of {status.total_stages}: {status.stage_name}</span>
                {status.current_stage_progress !== undefined && (
                  <span>{status.current_stage_progress}%</span>
                )}
              </div>
              <Progress value={status.current_stage_progress || 0} className="h-2" />
            </div>
          )}
          
          <div className="text-xs text-muted-foreground text-center">
            {status.message || `Processing ${status.filename}...`}
          </div>
        </div>

        {/* Current Step Highlight */}
        <Alert>
          {getStatusIcon(status.status, status.status)}
          <AlertTitle>Current Step: {getStatusText(status.status)}</AlertTitle>
          <AlertDescription>
            <div className="space-y-1">
              <p>{status.message || `Processing ${status.filename}...`}</p>
              {status.estimated_time_remaining !== undefined && status.estimated_time_remaining > 0 && (
                <p className="text-xs">
                  Estimated time remaining: {formatETA(status.estimated_time_remaining)}
                </p>
              )}
            </div>
          </AlertDescription>
        </Alert>

        {/* Status Steps */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-foreground">Processing Steps</h4>
          {steps.map((step, index) => (
            <div key={step} className="flex items-center space-x-3">
              {getStatusIcon(status.status, step)}
              <div className="flex-1">
                <p className={cn("text-sm", getStatusColor(step))}>
                  {getStatusText(step)}
                </p>
                {status.status === step && step !== 'completed' && step !== 'error' && (
                  <p className="text-xs text-muted-foreground mt-1">{status.message}</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* File Info */}
        <div className="p-4 bg-muted rounded-md">
          <div className="flex items-center space-x-3">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-foreground">{status.filename}</p>
              <p className="text-sm text-muted-foreground">
                Output format: {status.output_format.toUpperCase()}
                {status.custom_filename && ` • Custom name: ${status.custom_filename}`}
              </p>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {status.status === 'error' && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Processing Error</AlertTitle>
            <AlertDescription>
              <div className="space-y-2">
                <p>{status.message}</p>
                <div className="text-xs">
                  <p className="font-medium">Common solutions:</p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>Check your internet connection</li>
                    <li>Ensure the file is not corrupted</li>
                    <li>Try uploading a smaller file</li>
                    <li>Verify the file format (.doc or .docx)</li>
                  </ul>
                </div>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Results Preview */}
        {status.status === 'completed' && status.issues && status.summary && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertTitle>Analysis Complete</AlertTitle>
            <AlertDescription>
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Total Issues:</span>
                    <span className="ml-2 font-medium">{status.summary.total_issues}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Lines Processed:</span>
                    <span className="ml-2 font-medium">
                      {status.issues.length > 0 
                        ? Math.max(...status.issues.map(i => {
                            // Use new lines field if available, fallback to line_number
                            if (i.lines && !isNaN(parseInt(i.lines))) {
                              return parseInt(i.lines);
                            }
                            return i.line_number || 0;
                          }))
                        : 0
                      }
                    </span>
                  </div>
                </div>
                {status.summary.total_issues > 0 && (
                  <div className="text-xs text-muted-foreground">
                    <p>• Verb tense issues: {status.summary.verb_tense_consistency}</p>
                    <p>• Awkward phrasing: {status.summary.awkward_phrasing}</p>
                    <p>• Redundancy: {status.summary.redundancy}</p>
                    <p>• Grammar/punctuation: {status.summary.grammar_punctuation}</p>
                  </div>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressTracker;
