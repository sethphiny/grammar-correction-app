export interface GrammarIssue {
  line_number: number;
  line_range?: string;
  sentence_number: number;
  original_text: string;
  problem: string;
  fix: string;
  category: string;
  confidence: number;
  corrected_sentence?: string;
}

export interface DocumentData {
  filename: string;
  lines: DocumentLine[];
  total_lines: number;
  total_sentences: number;
  metadata: Record<string, any>;
}

export interface DocumentLine {
  line_number: number;
  content: string;
  sentences: string[];
}

export interface IssuesSummary {
  total_issues: number;
  categories: Record<string, number>;
  lines_with_issues: number;
  sentences_with_issues: number;
}

export interface UploadResponse {
  task_id: string;
  message: string;
}

export interface ProcessingStatus {
  task_id: string;
  status: ProcessingStatusEnum;
  progress: number;
  message: string;
  error?: string;
}

export interface ProcessingResult {
  task_id: string;
  status: ProcessingStatusEnum;
  report_path: string;
  filename: string;
  issues_count: number;
  summary: IssuesSummary;
  processing_time?: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  task_id?: string;
}

export enum ProcessingStatusEnum {
  UPLOADED = "uploaded",
  PARSING = "parsing",
  CHECKING = "checking",
  GENERATING = "generating",
  COMPLETED = "completed",
  ERROR = "error"
}

export enum OutputFormatEnum {
  DOCX = "docx",
  PDF = "pdf"
}

export interface GrammarConfig {
  language: string;
  rules: GrammarRule[];
  enable_spacy: boolean;
  enable_languagetool: boolean;
  confidence_threshold: number;
  max_issues_per_sentence: number;
}

export interface GrammarRule {
  name: string;
  enabled: boolean;
  category: string;
  description: string;
  severity: string;
}

export interface DocumentUploadRequest {
  output_filename?: string;
  output_format: OutputFormatEnum;
  grammar_config?: GrammarConfig;
}

export interface AppState {
  currentTask: string | null;
  processingStatus: ProcessingStatus | null;
  isProcessing: boolean;
  error: string | null;
  uploadedFile: File | null;
  outputFilename: string;
  outputFormat: OutputFormatEnum;
}
