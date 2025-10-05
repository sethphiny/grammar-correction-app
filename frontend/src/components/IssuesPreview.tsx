import React from 'react';
import { AlertTriangle, CheckCircle, Download } from 'lucide-react';
import { GrammarIssue } from '../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { cn } from '../lib/utils';

interface IssuesPreviewProps {
  issues: GrammarIssue[];
  summary: {
    verb_tense_consistency: number;
    awkward_phrasing: number;
    redundancy: number;
    grammar_punctuation: number;
    total_issues: number;
  };
  onDownload: () => void;
  darkMode?: boolean;
}

const IssuesPreview: React.FC<IssuesPreviewProps> = ({ issues, summary, onDownload, darkMode = false }) => {
  const getIssueTypeVariant = (type: string) => {
    switch (type) {
      case 'verb_tense_consistency':
        return 'default';
      case 'awkward_phrasing':
        return 'secondary';
      case 'redundancy':
        return 'outline';
      case 'grammar_punctuation':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getIssueTypeLabel = (type: string) => {
    switch (type) {
      case 'verb_tense_consistency':
        return 'Tense';
      case 'awkward_phrasing':
        return 'Phrasing';
      case 'redundancy':
        return 'Redundancy';
      case 'grammar_punctuation':
        return 'Grammar';
      default:
        return type;
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Analysis Results</CardTitle>
            <CardDescription>
              Found {summary.total_issues} issue{summary.total_issues !== 1 ? 's' : ''} in your document
            </CardDescription>
          </div>
          <Button
            onClick={onDownload}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Download Report
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">

        {/* Summary */}
        <div className="p-4 rounded-lg bg-muted">
          <h4 className="text-sm font-medium mb-3 text-foreground">
            Summary
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{summary.verb_tense_consistency}</div>
              <div className="text-xs text-muted-foreground">Tense Issues</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{summary.awkward_phrasing}</div>
              <div className="text-xs text-muted-foreground">Awkward Phrasing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{summary.redundancy}</div>
              <div className="text-xs text-muted-foreground">Redundancy</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">{summary.grammar_punctuation}</div>
              <div className="text-xs text-muted-foreground">Grammar/Punctuation</div>
            </div>
          </div>
        </div>

        {/* Issues List */}
        {issues.length > 0 ? (
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-foreground">
              Issues Found
            </h4>
            {issues.map((issue, index) => (
              <Card key={index} className="transition-colors hover:bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-4 w-4 text-gray-600" />
                      <span className="text-sm font-medium text-foreground">
                        Line {issue.lines || issue.line_range || issue.line_number}, Sentence {issue.sentences || issue.sentence_number}
                      </span>
                      <Badge variant={getIssueTypeVariant(issue.issue_type) as any}>
                        {getIssueTypeLabel(issue.issue_type)}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      Confidence: {Math.round(issue.confidence * 100)}%
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium text-foreground mb-1">Original Text:</p>
                      <p className="text-sm text-foreground italic bg-muted p-2 rounded">
                        "{issue.text || issue.original_text}"
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-destructive mb-1">Problem:</p>
                      <div className="text-sm text-foreground">
                        <div className="font-medium mb-1">{issue.problem}</div>
                        <div className="text-muted-foreground">{issue.reason}</div>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-blue-600 mb-1">Suggested Fix:</p>
                      <div className="text-sm text-foreground bg-blue-50 p-2 rounded border-l-4 border-blue-400">
                        <div className="font-medium mb-1">{issue.proposed_fix.action}</div>
                        <div className="mb-2">{issue.proposed_fix.details}</div>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-green-600 mb-1">Corrected Text:</p>
                      <p className="text-sm text-foreground bg-green-50 p-2 rounded border-l-4 border-green-400">
                        "{issue.proposed_fix.corrected_text}"
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <CheckCircle className="mx-auto h-12 w-12 text-gray-600 mb-4" />
            <h4 className="text-lg font-medium text-foreground mb-2">No Issues Found!</h4>
            <p className="text-muted-foreground">
              Your document looks great! No grammar or style issues were detected.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default IssuesPreview;
