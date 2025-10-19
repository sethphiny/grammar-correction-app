import React, { useState } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle, CreditCard, AlertCircle } from 'lucide-react';
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
    llm_detection_enabled?: boolean;
    issues_enhanced: number;
    issues_detected_by_llm?: number;
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
      'parallelism_concision': 'bg-indigo-100 text-indigo-800',
      'article_specificity': 'bg-green-100 text-green-800',
      'agreement': 'bg-rose-100 text-rose-800',
      'ambiguous_pronouns': 'bg-violet-100 text-violet-800',
      'dangling_clause': 'bg-amber-100 text-amber-800',
      'fragment': 'bg-fuchsia-100 text-fuchsia-800',
      'run_on': 'bg-lime-100 text-lime-800',
      'split_line': 'bg-emerald-100 text-emerald-800',
      'word_order': 'bg-sky-100 text-sky-800',
      'contrast': 'bg-slate-100 text-slate-800',
      'clarity': 'bg-stone-100 text-stone-800',
      'preposition': 'bg-neutral-100 text-neutral-800',
      'register': 'bg-zinc-100 text-zinc-800',
      'repetition': 'bg-gray-100 text-gray-800',
      'comma_splice': 'bg-red-200 text-red-900',
      'coordination': 'bg-yellow-200 text-yellow-900',
      'ellipsis': 'bg-purple-200 text-purple-900',
      'hyphenation': 'bg-blue-200 text-blue-900',
      'missing_period': 'bg-green-200 text-green-900',
      'number_style': 'bg-indigo-200 text-indigo-900',
      'possessive': 'bg-pink-200 text-pink-900',
      'broken_quote': 'bg-orange-200 text-orange-900',
      'compounds': 'bg-teal-200 text-teal-900',
      'pronoun_reference': 'bg-cyan-200 text-cyan-900',
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
      'parallelism_concision': 'Parallelism/Concision',
      'article_specificity': 'Article Usage',
      'agreement': 'Subject-Verb Agreement',
      'ambiguous_pronouns': 'Ambiguous Pronouns',
      'dangling_clause': 'Dangling Modifiers',
      'fragment': 'Sentence Fragments',
      'run_on': 'Run-on Sentences',
      'split_line': 'Split Line / Broken Dialogue',
      'word_order': 'Word Order',
      'contrast': 'Contrast',
      'clarity': 'Clarity',
      'preposition': 'Preposition / Diction',
      'register': 'Register / Formality',
      'repetition': 'Repetition',
      'comma_splice': 'Comma Splice',
      'coordination': 'Coordination',
      'ellipsis': 'Ellipsis',
      'hyphenation': 'Hyphenation',
      'missing_period': 'Missing Period',
      'number_style': 'Number Style',
      'possessive': 'Possessive',
      'broken_quote': 'Broken Quote',
      'compounds': 'Compounds',
      'pronoun_reference': 'Pronoun Reference',
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
      {enhancement && (enhancement.llm_enabled || enhancement.llm_detection_enabled) && !enhancement.warning && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900 mb-2">🤖 AI Analysis Complete</p>
              <div className="grid grid-cols-2 gap-3 text-xs">
                {enhancement.llm_detection_enabled && (
                  <div className="bg-white/50 rounded p-2">
                    <div className="font-medium text-blue-700">AI Detection</div>
                    <div className="text-gray-600 mt-1">
                      {enhancement.issues_detected_by_llm || 0} additional issues found
                    </div>
                  </div>
                )}
                {enhancement.llm_enabled && (
                  <div className="bg-white/50 rounded p-2">
                    <div className="font-medium text-purple-700">AI Enhancement</div>
                    <div className="text-gray-600 mt-1">
                      {enhancement.issues_enhanced || 0} fixes improved
                    </div>
                  </div>
                )}
              </div>
              {enhancement.cost > 0 && (
                <div className="mt-2 text-xs text-gray-600">
                  💰 Cost: ${enhancement.cost.toFixed(4)}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Enhancement Credit Warning */}
      {enhancement && enhancement.warning && (
        <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-orange-900">⚠️ AI Enhancement Unavailable</p>
            <p className="text-xs text-orange-700 mt-1">
              {enhancement.warning.includes('API key') 
                ? 'Please check your OpenAI API key configuration'
                : enhancement.warning.includes('package')
                ? 'AI enhancement requires additional setup'
                : enhancement.warning.includes('budget') || enhancement.warning.includes('credit')
                ? 'AI enhancement temporarily unavailable due to credit limits'
                : enhancement.warning
              }
            </p>
            {enhancement.warning.includes('budget') || enhancement.warning.includes('credit') && (
              <div className="mt-2 flex items-center gap-1 text-xs text-orange-600">
                <CreditCard className="h-3 w-3" />
                <span>Check your OpenAI account billing and credits</span>
              </div>
            )}
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
      <div className="border border-gray-200 rounded-lg divide-y divide-gray-200 bg-white shadow-sm">
        {filteredIssues.map((issue, index) => {
          const isAIDetected = issue.problem.startsWith('[AI]');
          
          return (
            <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs text-gray-500">
                  Line {issue.line_range || issue.line_number}
                </div>
                <div className="flex items-center gap-2">
                  {isAIDetected && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                      🤖 AI
                    </span>
                  )}
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(issue.category)}`}>
                    {getCategoryDisplayName(issue.category)}
                  </span>
                </div>
              </div>
              
              <div className="mb-3 p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm font-mono text-gray-800">
                {issue.original_text}
              </div>

              <div className="space-y-2 text-sm">
                <div className="text-gray-700">
                  <span className="font-semibold text-gray-900">Problem:</span> {issue.problem.replace('[AI] ', '')}
                </div>
                <div className="text-gray-700">
                  <span className="font-semibold text-gray-900">Fix:</span> <span className="text-green-700 font-medium">{issue.fix}</span>
                </div>
                {issue.corrected_sentence && issue.corrected_sentence !== issue.fix && (
                  <div className="mt-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                    <div className="text-xs text-green-700 font-semibold mb-1.5">✓ Corrected Version:</div>
                    <div className="text-sm font-mono text-green-900">{issue.corrected_sentence}</div>
                  </div>
                )}
                <div className="flex items-center gap-2 mt-3 text-xs text-gray-500">
                  <span>Confidence: {(issue.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredIssues.length === 0 && selectedCategory !== 'all' && (
        <div className="text-center py-8 text-sm text-gray-500">
          No issues in this category
        </div>
      )}
    </div>
  );
};
