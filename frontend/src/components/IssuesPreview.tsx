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
  enhancement?: {
    llm_enabled: boolean;
    issues_enhanced: number;
    cost: number;
    warning?: string;
  };
}

export const IssuesPreview: React.FC<IssuesPreviewProps> = ({ issues, summary, enhancement }) => {
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
      'punctuation': 'bg-yellow-100 text-yellow-800',
      'awkward_phrasing': 'bg-purple-100 text-purple-800',
      'redundancy': 'bg-red-100 text-red-800',
      'grammar': 'bg-orange-100 text-orange-800',
      'dialogue': 'bg-teal-100 text-teal-800',
      'capitalisation': 'bg-cyan-100 text-cyan-800',
      'spelling': 'bg-pink-100 text-pink-800',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryDisplayName = (category: string) => {
    const names = {
      'tense_consistency': 'Tense Consistency',
      'punctuation': 'Punctuation',
      'awkward_phrasing': 'Awkward Phrasing',
      'redundancy': 'Redundancy',
      'grammar': 'Grammar',
      'dialogue': 'Dialogue',
      'capitalisation': 'Capitalisation',
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
      <div className="p-8 text-center border border-gray-200 rounded-lg">
        <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
        <p className="text-sm text-gray-600">No issues found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* AI Enhancement Status/Warning */}
      {enhancement && enhancement.warning && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-900">AI Enhancement Not Available</p>
            <p className="text-xs text-yellow-700 mt-1">{enhancement.warning}</p>
            <p className="text-xs text-yellow-600 mt-2">
              📖 Setup guide: <code className="bg-yellow-100 px-1 rounded">docs/QUICK_START_LLM.md</code>
            </p>
          </div>
        </div>
      )}
      
      {/* AI Enhancement Success */}
      {enhancement && enhancement.llm_enabled && !enhancement.warning && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-green-900">✨ AI-Enhanced Suggestions Applied</p>
            <div className="flex gap-4 mt-1 text-xs text-green-700">
              <span>Enhanced: {enhancement.issues_enhanced} issues</span>
              <span>Cost: ${enhancement.cost.toFixed(4)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex justify-between items-center text-sm mb-3">
          <span className="font-medium text-gray-900">{summary.total_issues} issues</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:border-gray-900"
          >
            <option value="all">All</option>
            {Object.keys(summary.categories).map(category => (
              <option key={category} value={category}>
                {getCategoryDisplayName(category)}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-wrap gap-1">
          {Object.entries(summary.categories).map(([category, count]) => (
            <span
              key={category}
              className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-white border border-gray-200 text-gray-700"
            >
              {getCategoryDisplayName(category)}: {count}
            </span>
          ))}
        </div>
      </div>

      {/* Issues List */}
      <div className="border border-gray-200 rounded-lg divide-y divide-gray-200">
        {filteredIssues.map((issue, index) => (
          <div key={index} className="p-4">
            <div className="text-xs text-gray-500 mb-2">
              Line {issue.line_range || issue.line_number}
            </div>
            
            <div className="mb-3 p-2 bg-gray-50 rounded text-sm font-mono text-gray-800">
              {issue.original_text}
            </div>

            <div className="space-y-1 text-sm">
              <div className="text-gray-600">
                <span className="font-medium">Problem:</span> {issue.problem}
              </div>
              <div className="text-gray-600">
                <span className="font-medium">Fix:</span> <span className="text-green-700">{issue.fix}</span>
              </div>
              {issue.corrected_sentence && issue.corrected_sentence !== issue.fix && (
                <div className="mt-2 p-2 bg-green-50 rounded">
                  <div className="text-xs text-green-700 font-medium mb-1">Corrected:</div>
                  <div className="text-sm font-mono text-green-900">{issue.corrected_sentence}</div>
                </div>
              )}
              <div className="mt-2">
                <span className="inline-block px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                  {getCategoryDisplayName(issue.category)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredIssues.length === 0 && selectedCategory !== 'all' && (
        <div className="text-center py-8 text-sm text-gray-500">
          No issues in this category
        </div>
      )}
    </div>
  );
};
