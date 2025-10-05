from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class ProcessingStatusEnum(str, Enum):
    UPLOADING = "uploading"
    PARSING = "parsing"
    CHECKING_GRAMMAR = "checking_grammar"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    ERROR = "error"

class GrammarIssueType(str, Enum):
    VERB_TENSE = "verb_tense_consistency"
    AWKWARD_PHRASING = "awkward_phrasing"
    REDUNDANCY = "redundancy"
    GRAMMAR_PUNCTUATION = "grammar_punctuation"

class ProposedFix(BaseModel):
    action: str
    details: str
    corrected_text: str

class GrammarIssue(BaseModel):
    lines: str  # Line number or range (e.g., "31" or "31–32")
    sentences: str  # Sentence number(s) within that line (e.g., "1", "2", or "1–2")
    text: str  # The exact sentence text with the detected issue
    problem: str  # Problem type (e.g., "Verb tense consistency")
    reason: str  # Reason for the issue (e.g., "The tense shifts from past to present.")
    proposed_fix: ProposedFix
    issue_type: GrammarIssueType
    confidence: float = 0.0
    # Legacy fields for backward compatibility
    line_number: Optional[int] = None
    line_range: Optional[str] = None
    sentence_number: Optional[int] = None
    original_text: Optional[str] = None
    fix: Optional[str] = None
    corrected_text: Optional[str] = None

class CorrectionSummary(BaseModel):
    verb_tense_consistency: int = 0
    awkward_phrasing: int = 0
    redundancy: int = 0
    grammar_punctuation: int = 0
    total_issues: int = 0

class ProcessingStatus(BaseModel):
    id: str
    status: ProcessingStatusEnum
    progress: int  # 0-100
    message: str
    filename: str
    output_format: str
    custom_filename: Optional[str] = None
    issues: List[GrammarIssue] = []
    summary: Optional[Dict] = None
    download_path: Optional[str] = None
    output_filename: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    # Progress tracking fields
    estimated_time_remaining: Optional[int] = None  # seconds
    current_stage_progress: Optional[int] = None  # 0-100 for current stage
    total_stages: Optional[int] = None  # total number of processing stages
    current_stage: Optional[int] = None  # current stage number (1-based)
    stage_name: Optional[str] = None  # name of current stage

class CorrectionReport(BaseModel):
    document_title: str
    processed_at: str
    total_lines: int
    total_sentences: int
    issues: List[GrammarIssue]
    summary: CorrectionSummary

class UploadRequest(BaseModel):
    output_format: str = "docx"
    custom_filename: Optional[str] = None

class DocumentLine(BaseModel):
    line_number: int
    content: str
    sentences: List[str]
