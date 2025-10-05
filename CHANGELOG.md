# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Updated
- **Updated language-tool-python to version 2.9.4**: Updated dependency to latest stable version for improved grammar checking performance and bug fixes
- **Enhanced Grammar Checker Output Format**: Modified grammar checker to return complete sentences/phrases instead of individual words and consolidated multiple issues in one sentence into single comprehensive fixes
  - Updated all grammar check methods to use full sentences as `original_text`
  - Enhanced consolidation logic to merge multiple issues in the same sentence
  - Updated report generator to match sample output format with proper line numbers, quoted sentences, and structured problem/fix descriptions
- **Removed Sentence Length Checks**: Eliminated grammar checker rules that flagged longer sentences as issues to focus on actual grammar problems
- **Streamlined Awkward Phrasing Detection**: Reduced awkward phrasing patterns from 25+ to 8 core patterns to focus on truly problematic phrasing and reduce false positives
- **Enhanced Document Parsing**: Improved Word document parsing to better preserve document structure
  - Treat each paragraph break (Enter) as a new line or text block
  - Preserve manual line breaks (Shift+Enter) as '\n' within the same paragraph
  - Keep table of contents entries separate from body text
  - Preserve whitespace and newlines as they appear without collapsing into one line
  - Ignore hidden fields, page breaks, and formatting that don't affect visible text
  - Return text with proper line and paragraph structure intact

### Added
- **Chunk Processing Fail/Retry Strategy**: Implemented robust error handling for chunk processing to prevent getting stuck at specific chunks
  - Added timeout handling (30 seconds per chunk) with automatic retry mechanism
  - Implemented exponential backoff retry strategy (up to 3 retries per chunk)
  - Added fallback strategy to skip problematic chunks and continue processing
  - Enhanced progress monitoring with heartbeat system to detect stuck chunks (60-second timeout)
  - Added detailed logging and status updates for retry attempts and failures

### Added
- **Proposed Sentence Feature**: Added ability to show complete corrected sentences after applying suggested fixes
  - Added `proposed_sentence` field to `GrammarIssue` schema in both backend and frontend
  - Enhanced grammar checker with intelligent sentence correction algorithms for different issue types:
    - Verb tense consistency fixes
    - Redundancy removal (e.g., "in order to" → "to", "due to the fact that" → "because")
    - Awkward phrasing improvements (e.g., "there is/are" → "we have", "in terms of" → "regarding")
    - Punctuation corrections (removing extra commas before quotation marks)
  - Updated frontend IssuesPreview component to display proposed sentences with blue styling
  - Proposed sentences only show when they differ from the original text

### Fixed
- Fixed Pydantic serialization warning by using `ProcessingStatusEnum` values instead of string literals in `main.py`
  - Updated all status assignments to use proper enum values (UPLOADING, PARSING, CHECKING_GRAMMAR, GENERATING_REPORT, COMPLETED, ERROR)
  - Updated status comparison in download endpoint to use enum value
  - This resolves the warning: `PydanticSerializationUnexpectedValue(Expected 'enum' - serialized value may not be as expected [input_value='completed', input_type=str])`
- **Fixed Awkward Phrasing Detection**: Improved grammar checker to provide specific suggested fixes instead of generic messages
  - Removed overly broad alliteration pattern that was flagging legitimate titles like "Test Document for Grammar Correction"
  - Enhanced fix generation to provide specific replacement suggestions with corrected sentences
  - Added proper handling of regex group references in suggested fixes
  - Now provides actionable corrections like "Replace 'very good' with 'good'" instead of generic rephrasing advice
- **Enhanced Grammar Checker Quality**: Fixed multiple issues identified through comprehensive testing
  - Improved problem consolidation to avoid confusing messages like "The words 'are', 'many', 'are' and 'is' contain spelling mistakes"
  - Enhanced verb tense inconsistency detection with better pattern matching and specific corrections
  - Fixed fix quality issues where "very good" was becoming "good and good" - now suggests "excellent and wonderful"
  - Added better detection for overly complex sentences with multiple relative clauses
  - Improved suggested fixes to provide complete corrected sentences instead of generic advice
- **Fixed Large File Processing Performance**: Resolved backend freezing issues with large documents (5.6MB+ files)
  - Implemented intelligent batching system: 50 lines/batch for large docs, 20 for medium, 5 for small
  - Added memory optimizations: garbage collection, reduced status update frequency, text length limits
  - Enhanced progress tracking: less frequent updates for large files to reduce overhead
  - Added timeout protection: 30-minute maximum processing time with automatic cancellation
  - Optimized LanguageTool usage: limited issues per sentence, skipped very short text, truncated long sentences
  - Added large file warnings: alerts when files exceed 5MB threshold
- **Enhanced ETA Calculation System**: Implemented dynamic time estimation based on actual processing performance
  - Added 30KB baseline metrics: 10 seconds processing time, 3KB/s, 5 lines/s reference speeds
  - Dynamic ETA calculation using multiple methods: actual speed, file size ratio, baseline scaling
  - File size scaling: larger files (5.6MB) estimated at 30+ minutes vs small files (30KB) at 10 seconds
  - Real-time baseline learning: system updates performance metrics based on actual processing times
  - Intelligent fallback system: uses actual speeds when available, falls back to baseline estimates
  - Enhanced progress tracking with detailed processing statistics and performance monitoring
