import React, { useState } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle } from 'lucide-react';
import { GrammarIssue } from '../types';

interface IssuesPreviewProps {
  issues: GrammarIssue[];
  summary: {
    total_issues: number;
    categories: Record<string, number>;
    lines_with_issues: number;
    sentences_with_issues: number;
  };
}

export const IssuesPreview: React.FC<IssuesPreviewProps> = ({ issues, summary }) => {
  const [expandedIssues, setExpandedIssues] = useState<Set<number>>(new Set());
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const toggleIssue = (index: number) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIssues(newExpanded);
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'tense_consistency': 'bg-blue-100 text-blue-800',
      'subject_verb_agreement': 'bg-green-100 text-green-800',
      'punctuation': 'bg-yellow-100 text-yellow-800',
      'awkward_phrasing': 'bg-purple-100 text-purple-800',
      'redundancy': 'bg-red-100 text-red-800',
      'style': 'bg-indigo-100 text-indigo-800',
      'spelling': 'bg-pink-100 text-pink-800',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryDisplayName = (category: string) => {
    const names = {
      'tense_consistency': 'Tense Consistency',
      'subject_verb_agreement': 'Subject-Verb Agreement',
      'punctuation': 'Punctuation',
      'awkward_phrasing': 'Awkward Phrasing',
      'redundancy': 'Redundancy',
      'style': 'Style & Clarity',
      'spelling': 'Spelling',
    };
    return names[category as keyof typeof names] || category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const filteredIssues = selectedCategory === 'all' 
    ? issues 
    : issues.filter(issue => issue.category === selectedCategory);

  const categories = ['all', ...Object.keys(summary.categories)];

  if (issues.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <CheckCircle className="h-16 w-16 text-success-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Issues Found</h3>
          <p className="text-gray-600">
            Great! No grammar or style issues were detected in your document.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="card">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Analysis Summary</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">{summary.total_issues}</div>
            <div className="text-sm text-gray-600">Total Issues</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">{summary.lines_with_issues}</div>
            <div className="text-sm text-gray-600">Lines with Issues</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-error-600">{summary.sentences_with_issues}</div>
            <div className="text-sm text-gray-600">Sentences with Issues</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">{Object.keys(summary.categories).length}</div>
            <div className="text-sm text-gray-600">Issue Categories</div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Issues by Category</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(summary.categories).map(([category, count]) => (
              <span
                key={category}
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(category)}`}
              >
                {getCategoryDisplayName(category)}: {count}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Issues List */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900">Issues Found</h2>
          
          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="input-field w-auto"
          >
            <option value="all">All Categories</option>
            {Object.keys(summary.categories).map(category => (
              <option key={category} value={category}>
                {getCategoryDisplayName(category)}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-4">
          {filteredIssues.map((issue, index) => {
            const isExpanded = expandedIssues.has(index);
            
            return (
              <div key={index} className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => toggleIssue(index)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                      )}
                      <AlertTriangle className="h-5 w-5 text-warning-500" />
                      <div>
                        <div className="font-medium text-gray-900">
                          Line {issue.line_range || issue.line_number}, Sentence {issue.sentence_number}
                        </div>
                        <div className="text-sm text-gray-500">
                          {getCategoryDisplayName(issue.category)}
                        </div>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(issue.category)}`}>
                      {getCategoryDisplayName(issue.category)}
                    </span>
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-200 bg-gray-50">
                    <div className="pt-4 space-y-3">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">Original Text</h4>
                        <p className="text-sm text-gray-700 bg-white p-3 rounded border">
                          "{issue.original_text}"
                        </p>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">Problem</h4>
                        <p className="text-sm text-gray-700">
                          {issue.problem}
                        </p>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">Suggested Fix</h4>
                        <p className="text-sm text-gray-700 bg-success-50 p-3 rounded border border-success-200">
                          {issue.fix}
                        </p>
                      </div>
                      
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>Confidence: {Math.round(issue.confidence * 100)}%</span>
                        <span>Category: {getCategoryDisplayName(issue.category)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredIssues.length === 0 && selectedCategory !== 'all' && (
          <div className="text-center py-8">
            <p className="text-gray-500">No issues found in the selected category.</p>
          </div>
        )}
      </div>
    </div>
  );
};
