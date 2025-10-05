"""
Pydantic schemas for the Grammar Correction API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ProcessingStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHECKING = "checking"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"

class OutputFormatEnum(str, Enum):
    DOCX = "docx"
    PDF = "pdf"

class GrammarIssue(BaseModel):
    """Represents a single grammar issue found in the document"""
    line_number: int = Field(..., description="Line number where the issue was found")
    line_range: Optional[str] = Field(None, description="Line range if sentence spans multiple lines")
    sentence_number: int = Field(..., description="Sentence number within the line")
    original_text: str = Field(..., description="Original text with the issue")
    problem: str = Field(..., description="Description of the problem")
    fix: str = Field(..., description="Suggested fix")
    category: str = Field(..., description="Category of the issue")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the issue")

class DocumentLine(BaseModel):
    """Represents a line in the document"""
    line_number: int
    content: str
    sentences: List[str] = Field(default_factory=list)

class DocumentData(BaseModel):
    """Represents the parsed document data"""
    filename: str
    lines: List[DocumentLine]
    total_lines: int
    total_sentences: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IssuesSummary(BaseModel):
    """Summary of all issues found"""
    total_issues: int
    categories: Dict[str, int] = Field(default_factory=dict)
    lines_with_issues: int
    sentences_with_issues: int

class UploadResponse(BaseModel):
    """Response after uploading a document"""
    task_id: str = Field(..., description="Unique task identifier")
    message: str = Field(..., description="Status message")

class ProcessingStatus(BaseModel):
    """Current processing status of a task"""
    task_id: str
    status: ProcessingStatusEnum
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Human-readable status message")
    error: Optional[str] = Field(None, description="Error message if any")

class ProcessingResult(BaseModel):
    """Final result of document processing"""
    task_id: str
    status: ProcessingStatusEnum
    report_path: str
    filename: str
    issues_count: int
    summary: IssuesSummary
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    task_id: Optional[str] = Field(None, description="Task ID if applicable")

class GrammarRule(BaseModel):
    """Configuration for a grammar rule"""
    name: str
    enabled: bool = True
    category: str
    description: str
    severity: str = "medium"  # low, medium, high

class GrammarConfig(BaseModel):
    """Configuration for grammar checking"""
    language: str = "en-US"
    rules: List[GrammarRule] = Field(default_factory=list)
    enable_spacy: bool = True
    enable_languagetool: bool = True
    confidence_threshold: float = 0.7
    max_issues_per_sentence: int = 5

class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    output_format: OutputFormatEnum = Field(OutputFormatEnum.DOCX, description="Output format")
    grammar_config: Optional[GrammarConfig] = Field(None, description="Grammar checking configuration")

class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    issues: List[GrammarIssue]
    document_data: DocumentData
    output_filename: str
    output_format: OutputFormatEnum
    include_original: bool = True
    include_summary: bool = True
