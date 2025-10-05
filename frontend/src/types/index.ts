export interface ProposedFix {
  action: string;
  details: string;
  corrected_text: string;
}

export interface GrammarIssue {
  // New format fields
  lines: string;  // Line number or range (e.g., "31" or "31–32")
  sentences: string;  // Sentence number(s) within that line (e.g., "1", "2", or "1–2")
  text: string;  // The exact sentence text with the detected issue
  problem: string;  // Problem type (e.g., "Verb tense consistency")
  reason: string;  // Reason for the issue (e.g., "The tense shifts from past to present.")
  proposed_fix: ProposedFix;
  issue_type: 'verb_tense_consistency' | 'awkward_phrasing' | 'redundancy' | 'grammar_punctuation';
  confidence: number;
  // Legacy fields for backward compatibility
  line_number?: number;
  line_range?: string;
  sentence_number?: number;
  original_text?: string;
  fix?: string;
}

export interface ProcessingStatus {
  id: string;
  status: 'uploading' | 'parsing' | 'checking_grammar' | 'generating_report' | 'completed' | 'error';
  progress: number;
  message: string;
  filename: string;
  output_format: string;
  custom_filename?: string;
  issues: GrammarIssue[];
  summary?: {
    verb_tense_consistency: number;
    awkward_phrasing: number;
    redundancy: number;
    grammar_punctuation: number;
    total_issues: number;
  };
  download_path?: string;
  output_filename?: string;
  created_at?: string;
  completed_at?: string;
  // Progress tracking fields
  estimated_time_remaining?: number;  // seconds
  current_stage_progress?: number;  // 0-100 for current stage
  total_stages?: number;  // total number of processing stages
  current_stage?: number;  // current stage number (1-based)
  stage_name?: string;  // name of current stage
}

export interface UploadResponse {
  processing_id: string;
  message: string;
}

export type OutputFormat = 'docx' | 'pdf';
