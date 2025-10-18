# Changelog

All notable changes to the Grammar Correction App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Fixed
- **LLM Enhancement Emoji Removal**: Removed ✨ emoji from LLM enhanced issues in reports and frontend
  - Enhanced problem descriptions and fixes no longer display with sparkle emoji prefix
  - Clean, professional appearance without decorative emojis
  - AI Insight fallback also removed 💡 emoji for consistency
- **Grammar Checker URL Capitalization Detection**: Fixed grammar checker incorrectly flagging URLs as capitalization issues
  - Updated capitalisation patterns to exclude URLs (https://, http://, www.)
  - First word capitalization pattern now uses negative lookahead: `^(?!https?://|www\.)([a-z])`
  - Sentence capitalization pattern now excludes URLs after punctuation: `(?<!\.)([.!?])\s+(?!https?://|www\.)([a-z])`
  - URLs are no longer flagged as capitalization issues in the grammar checker
- **LLM Enhancement URL Capitalization Issue**: Fixed LLM enhancer incorrectly capitalizing URLs
  - Added explicit rules to prevent capitalization of URL protocol prefixes (https://, http://)
  - URLs now maintain their original lowercase formatting in enhanced corrections
  - Enhanced prompts include specific instructions to preserve URL formatting
- **Report Format Category Display**: Improved category display format in generated reports
  - Category now shows inline with problem description: "Problem: Capitalisation → enhanced description"
  - Corrected sentence format updated to: "Corrected sentence: "quoted text""
  - Removed redundant separate category line for cleaner formatting
- **LLM Enhancement Coverage Issue**: Fixed LLM enhancer only processing subset of issues due to high confidence thresholds
  - Lowered confidence thresholds to ensure ALL grammar issue categories get enhanced
  - High priority categories (awkward_phrasing, tense_consistency, etc.): now enhanced if confidence < 95% (was 90%)
  - Medium priority categories (redundancy, capitalisation, etc.): now enhanced if confidence < 98% (was 95%)
  - Lower priority categories (punctuation, spelling): now enhanced if confidence < 99% (was 98%)
  - Default threshold: now enhanced if confidence < 98% (was 95%)
  - This ensures comprehensive LLM enhancement coverage across all grammar categories
- **LLM Enhancement Timeout Issues**: Fixed request timeouts in LLM enhancement service
  - Added configurable timeout settings (default 60s) via `LLM_REQUEST_TIMEOUT` environment variable
  - Implemented retry logic with exponential backoff (default 3 retries) via `LLM_MAX_RETRIES` and `LLM_RETRY_DELAY`
  - Enhanced error handling with specific timeout and rate limit error messages
  - Added proper asyncio timeout handling using `asyncio.wait_for()`
  - Improved reliability for batch enhancement processing
  - **Batch Processing Chunking**: Implemented chunking to process large batches without timeouts
    - Large batches are now processed in chunks of 10 issues to prevent timeouts
    - Each chunk is processed independently with proper error handling
    - Failed chunks don't affect other chunks, improving overall reliability
    - Reduced default batch size from 50 to 15 issues for better stability
  - **Problem Description Enhancement**: LLM now enhances problem descriptions for better context
    - Enhanced problem descriptions provide more contextual explanations (e.g., "The phrase 'a lot of' is unnecessarily wordy in this context and can be simplified to 'many' for more concise writing")
    - Improved prompts to request both enhanced problem descriptions and fixes
    - Increased token limits for batch processing to accommodate longer enhanced descriptions
    - Better JSON parsing error handling for batch responses

### Added
- **Agreement Category (placeholder)**: Added `agreement` to available categories list
  - Visible in `/categories` API and frontend checkboxes
  - Subject–verb agreement rules remain disabled due to past false positives
  - Enables future targeted work without breaking current behavior
- **Article/Specificity Category**: New grammar category for article usage and specificity issues
  - Added `article_specificity` category to grammar checker with comprehensive pattern matching
  - Detects article errors (a/an usage) with smart vowel/consonant sound recognition
  - Identifies unnecessary articles before quantifiers and demonstratives
  - Flags vague language and suggests more specific alternatives
  - Detects vague comparisons and overuse of "the" for general reference
  - Includes LLM enhancement support with category-specific guidance
  - Tested with various examples: "the both students" → "both students", "a elephant" → "an elephant"
- **Corrected Sentence Generation**: LLM enhancer now generates complete corrected sentences
  - Updated single issue enhancement prompts to include `corrected_sentence` field
  - Updated batch enhancement prompts to include `corrected_sentence` for each issue
  - Modified `_apply_enhancement()` method to set the `corrected_sentence` field
  - Modified `_apply_batch_enhancements()` method to handle corrected sentences
  - Tested and verified corrected sentences are properly generated (e.g., "I will start the meeting.")

### Fixed
- **Environment Variable Loading**: Fixed LLM enhancement not working due to incorrect .env file loading
  - Updated `main.py` to load `.env` from project root directory
  - Updated `llm_enhancer.py` to load `.env` from project root directory  
  - Updated `test_llm_connection.py` to load `.env` from project root directory
  - All environment variables now properly loaded: `LLM_ENHANCEMENT_ENABLED`, `OPENAI_API_KEY`, etc.
- **LLM Enhancement Quality**: Improved AI-powered grammar fixes to be more contextual and human-like
  - Enhanced prompts to reference full sentence context instead of generic replacements
  - Changed from "replace X with Y" to "In this sentence, replace X with Y because..."
  - Added contextual explanations that reference the specific sentence
  - Improved system prompts to act as a professional writing coach
  - Example: "In this sentence, replace 'start off' with 'begin' because it conveys the same meaning in a more formal and straightforward manner."
- **Frontend AI Integration**: Streamlined AI enhancement to be always enabled with credit monitoring
  - Removed AI-Enhanced Suggestions checkbox since AI is now enabled by default
  - Updated UI to show "Always On" status instead of toggle
  - Added intelligent credit warning notifications when AI enhancement fails
  - Enhanced error messages for API key issues, package installation, and credit limits
  - Simplified user experience - no need to manually enable AI features
- **IDE Configuration**: Fixed Python import resolution warnings in development environment
  - Added VS Code settings to use virtual environment Python interpreter
  - Created pyrightconfig.json for proper Python path resolution
  - Added pyproject.toml for better project configuration
  - Resolved "could not be resolved" warnings for FastAPI, Uvicorn, python-dotenv, and Spacy imports
- **LLM Enhancement Coverage**: Expanded AI enhancement to cover all grammar categories
  - Updated enhancement logic to process all 9 grammar categories (redundancy, awkward_phrasing, punctuation, grammar, dialogue, capitalisation, tense_consistency, spelling, parallelism_concision)
  - Implemented category-specific enhancement thresholds based on complexity and confidence levels
  - Added category-specific guidance prompts for more targeted AI corrections
  - Increased batch processing limit from 20 to 50 issues to handle more comprehensive enhancement
  - Enhanced prompts with category-specific instructions for better contextual corrections
  - Removed 50-issue cap: enhancer now processes ALL detected issues by default
  - Added `LLM_ENHANCE_ALL` flag (default true) to force full coverage regardless of cost cap
  - Grammar checker now requests unlimited enhancements (`max_issues=None`); chunking prevents timeouts
  - Cost cap (`LLM_MAX_COST_PER_DOCUMENT`) is respected unless `LLM_ENHANCE_ALL` is true

### Documentation
- **LLM Implementation Guide**: Comprehensive guide for integrating AI-powered grammar enhancements
  - Complete implementation plans with 12-week timeline
  - Detailed cost analysis per MB and per provider
  - Phase-by-phase rollout strategy
  - Provider comparison (OpenAI, Google, Anthropic)
  - Cost optimization strategies (selective, batching, caching)
  - ROI analysis and success metrics
  - Complete code examples and architecture diagrams
  - Located in `docs/LLM_IMPLEMENTATION_GUIDE.md`
- **LLM Cost Reference Sheet**: Quick lookup guide for cost estimates
  - Cost calculator by document size
  - Monthly budget estimates for different scales
  - Provider pricing comparison
  - Cost optimization strategies
  - ROI calculator
  - Located in `docs/LLM_COST_REFERENCE.md`
- **API Keys Setup Guide**: Step-by-step guide for obtaining and configuring API keys
  - OpenAI API key setup (recommended)
  - Google Gemini API key setup (budget option)
  - Anthropic Claude API key setup (premium option)
  - Billing configuration and budget limits
  - Security best practices
  - Testing and troubleshooting
  - Located in `docs/API_KEYS_SETUP_GUIDE.md`

### Fixed
- **LLM Enhancement User Feedback**: System now shows clear warnings when AI enhancement is unavailable
  - Frontend displays yellow warning banner when credentials are missing
  - Backend returns specific warning messages (missing package, missing API key, etc.)
  - Green success banner shows when AI enhancement works (with cost and count)
  - Helpful setup guide link provided in warning message
  - Users understand why AI enhancement isn't working and how to fix it
- **Category Selection**: Fixed issue where selected categories were not properly applied during analysis
  - Added `Form(...)` imports to properly parse multipart form data in FastAPI
  - Updated upload endpoint parameters to use `Form()` for all form fields
  - Added debug logging to trace category selection through the system
  - Now correctly filters grammar checks based on user-selected categories

### Added
- **LLM Enhancement Integration (Phase 1 Complete)**: AI-powered grammar correction improvements
  - **LLMEnhancer Service** (`backend/services/llm_enhancer.py`):
    - Selective enhancement: Only processes complex/uncertain issues (20-30% of total)
    - Batch processing: Groups issues for efficient API usage
    - Cost tracking: Real-time cost monitoring and estimation
    - Cost controls: Daily and monthly budget limits with automatic throttling
    - Token counting: Accurate cost estimation before API calls
    - Graceful degradation: Falls back to pattern-based checking if API unavailable
  - **OpenAI GPT-4o-mini Integration**:
    - Recommended provider for best cost/quality balance
    - Cost: $0.01-0.03 per MB (selective mode)
    - Processing time: +3-5 seconds per document
    - Quality improvement: +40-50% on complex issues
  - **Smart Filtering**:
    - Only enhances issues with confidence < 0.85
    - Focuses on complex categories (awkward phrasing, tense consistency, parallelism)
    - Skips simple pattern matches to save costs
  - **Frontend UI**:
    - "✨ AI-Enhanced Suggestions" checkbox with Premium badge
    - Cost estimate displayed (~$0.01-$0.03 per MB)
    - Clear indicator when enhancement is enabled
    - Disabled by default (opt-in feature)
  - **Testing Infrastructure**:
    - `test_llm_connection.py` script to verify API keys
    - Cost estimation and statistics
    - Connection testing for multiple providers
  - **Configuration**:
    - Environment variables for API keys and limits
    - Updated `env.example` with full LLM configuration
    - Budget controls: Per-document, daily, and monthly limits
  - **Dependencies Added**:
    - `openai>=1.12.0` - OpenAI API client
    - `tiktoken>=0.5.2` - Token counting for cost estimation
- **Selective Category Analysis**: Users can now choose which grammar categories to analyze
  - Frontend displays checkboxes for all available grammar categories
  - "Select All" option for convenience (enabled by default)
  - Categories include: Redundancy, Awkward Phrasing, Punctuation, Grammar, Dialogue, Capitalisation, Tense Consistency, Spelling, Parallelism/Concision (Experimental)
  - Backend filters grammar checks based on selected categories
  - API endpoint `/categories` returns available categories
  - Selected categories are passed to grammar checker for targeted analysis
  - Improves performance and allows focus on specific issue types
- **Parallelism/Concision Category (EXPERIMENTAL)**: Grammar checking category for writing clarity and conciseness
  - ⚠️ **EXPERIMENTAL FEATURE**: Enabled but may produce false positives - use with caution
  - Marked as "(Experimental)" in the UI and reports
  - Users can choose to enable/disable this category via checkbox selection
  - **Wordy Phrases**: 40+ verbose phrases with concise alternatives
    - Examples: "at the present moment" → "now", "in order to" → "to", "prior to" → "before"
    - Examples: "make a decision" → "decide", "give consideration to" → "consider", "reach a conclusion" → "conclude"
    - Examples: "on a regular basis" → "regularly", "at all times" → "always", "in many cases" → "often"
  - **Smart Passive Voice Detection with spaCy**: Uses linguistic analysis to detect true passive voice only
    - **Eliminates False Positives**: Uses spaCy dependency parsing (auxpass detection) instead of regex
      - ✅ **Skips**: "is nuanced", "is layered" (linking verb + adjective, NOT passive voice)
      - ❌ **Flags**: "was written", "were marketed" (true passive constructions)
    - **Dynamic Fix Suggestions**: Generates context-specific advice based on the detected verb
      - Example: "was written" → "identify who performs the action of 'write' and make them the subject"
      - Example: "were marketed" → "identify who performs the action of 'market' and make them the subject"
    - **Smart Filtering**: Only flags when the agent is unclear or missing
      - ✅ **Skips**: "was written by Chapman" (clear agent, intentional passive)
      - ✅ **Skips**: "It was designed to..." (intentional passive pattern)
      - ✅ **Skips**: Technical contexts (framework, methodology, research, etc.)
      - ✅ **Skips**: Short sentences (< 8 words) which may be stylistic
      - ❌ **Flags**: "The message was interpreted as harmful" (no clear agent)
    - Requires spaCy and en_core_web_sm model (gracefully degrades if not available)
  - **Nominalization Detection**: Identifies verbs turned into nouns (less concise writing)
    - Examples: "make an analysis of" → suggests "analyze", "provide an explanation of" → suggests "explain"
  - **Redundant Intensifiers**: Flags redundant modifiers of absolute terms
    - Examples: "very unique" → "unique", "completely destroyed" → "destroyed", "absolutely certain" → "certain"
  - Auto-fixes available for most patterns; complex cases are flagged for manual review
  - Integrated into report generation with proper category display name
- **Preserve Empty Lines for Accurate Line Numbers**: Document parser now preserves empty lines
  - Empty lines are included in the parsed document data to maintain accurate line numbering
  - Line numbers in reports now match the original document exactly
  - Makes it easier to locate issues in the original file
  - Empty lines are still skipped during grammar checking (no false errors)

### Changed
- **Simplified Grammar Checker to Focus on Clarity**: Temporarily disabled LanguageTool checks
  - Removed LanguageTool dependency from active checking
  - Now checks for redundant phrases, awkward phrasing, punctuation, and grammar using custom pattern matching
  - **Redundant Phrases**: 100+ common redundancies with corrections
    - Examples: "absolutely essential" → "essential", "past history" → "history", "end result" → "result"
  - **Awkward Phrasing**: 100+ wordy/awkward constructions with clearer alternatives
    - Examples: "due to the fact that" → "because", "at this point in time" → "now", "in the event that" → "if"
    - Examples: "has the ability to" → "can", "made a decision" → "decided", "prior to" → "before"
  - **Punctuation**: Common punctuation errors
    - Multiple consecutive spaces → single space
    - Extra spaces before punctuation (commas, semicolons, etc.)
    - Missing spaces after punctuation  
    - Multiple punctuation marks (e.g., ",," → "," or ";;" → ";")
    - Extra spaces after opening brackets or before closing brackets
    - **Note**: Ellipsis (...) and em dashes (—) are preserved as valid punctuation
  - **Grammar**: Common grammar errors
    - Common verb errors: "should of" → "should have", "could of" → "could have", "would of" → "would have"
    - Homophones: "your/you're", "its/it's", "their/there", "then/than", "loose/lose", "affect/effect"
    - Double negatives (e.g., "don't have nothing" → "don't have anything")
    - **Notes**: 
      - Article checking ("a" vs "an") removed - depends on pronunciation, not spelling
      - Subject-verb agreement removed - too complex (modals, auxiliaries, causatives all affect verb form)
  - Preserves capitalization of original text in suggestions
  - More focused and faster checking - other checks (spelling) will be added back later
  - Simplified codebase by removing unused LanguageTool processing methods

### Previous Features
- **Common Phrase Detection**: Filter out false positives for common English phrases
  - Detects phrases like "out loud", "in order", "a lot", "each other", etc.
  - Prevents incorrect suggestions like "out loud" → "our loud"
  - Works for both line-level and sentence-level checking
  - Added 10+ common phrases that are often incorrectly flagged by spell checkers
- **Improved Report Structure**: Enhanced report formatting with hierarchical organization
  - Added "Text:" field showing the original text at the top of each issue
  - Increased indentation for all sub-items (Text, Problem, Fix, Full correction, Category)
  - Added "Category:" field at the end of each issue with formatted category names
  - Made all labels bold ("Text:", "Problem:", "Fix:", "Full correction:", "Category:")
  - Better visual hierarchy with consistent spacing and indentation
  - Category names are now title-cased and readable (e.g., "Subject Verb Agreement")
- **Improved Style Warning Handling**: Filter out useless fix suggestions
  - Detects when LanguageTool suggests the same word as replacement (e.g., 'For' → 'For')
  - Skips issues entirely if corrected text is identical to original (no real changes)
  - Shows "Consider rephrasing (no specific suggestion available)" for style warnings without real fixes
  - Prevents displaying unhelpful corrections like repetition warnings with no alternatives
  - Only shows "Full correction" when actual fixes are available
  - Eliminates false positives from style checkers that don't produce actionable changes
- **Proper Name Detection**: Added intelligent filtering for proper names to prevent false positives
  - Detects names with title prefixes (Dr., Mr., Mrs., Prof., etc.)
  - Recognizes name patterns like "FirstName LastName" and "By AuthorName"
  - Identifies names with special capitalization (McFarlane, O'Brien, etc.)
  - Filters out MORFOLOGIK spelling suggestions for detected proper names
  - Handles possessive names (e.g., "Pearlman's")
  - Detects acronyms and organizations (all caps words)
  - Examples: "Dr. Bryan Pearlman", "Kwame", "Ekanem", "McFarlane" are no longer flagged
- **Improved Fix Display**: Fixed discrepancy between UI and report fix display
  - `fix` field now shows individual replacements (e.g., 'there' → 'their')
  - `corrected_sentence` field shows the full corrected line
  - UI and report now consistently show the same information
  - Multiple fixes in one line are displayed as summary (e.g., 'word1' → 'fix1'; 'word2' → 'fix2')
  - Added line breaks in reports: Fix and Full correction are now on separate lines for better readability
  - Report format: "• Fix:" followed by "• Full correction:" on new line (instead of arrow on same line)
- **Manual Report Download**: Removed automatic report download, added "Download Report" button
  - Report no longer downloads automatically when analysis completes
  - User can manually download report using the button in results view
  - Better user control over when to download the corrected document
- **🎉 Minimal UI Design**: Completely redesigned frontend with clean, minimal interface
  - Removed header navigation and footer sections for cleaner look
  - Simplified color scheme using gray-900 as primary color
  - Centered layout with focused content area (max-width: 2xl)
  - Minimal file upload interface with compact dropzone
  - Streamlined results display with condensed issue cards
  - Reduced visual noise and unnecessary decorations
  - Cleaner typography using system fonts
  - Simplified CSS with minimal custom classes
  - More efficient use of whitespace for better focus
  - Compact progress indicators during processing
- **🎉 Real-Time Progress with WebSockets**: Added live analysis updates during document processing
  - WebSocket connection provides instant feedback during grammar checking
  - Live statistics display showing:
    - Total lines in document
    - Lines analyzed in real-time (updating continuously)
    - Issues found as they're detected
    - Issues per line ratio
  - Beautiful gradient progress UI with animated stats cards
  - Backend sends granular updates: starting, parsing, checking each line, analysis complete, generating report
  - Frontend automatically connects WebSocket on upload and displays live stats
  - Proper cleanup of WebSocket connections on component unmount
  - Enhanced user experience with immediate visibility into analysis progress

### Changed
- **🚨 MAJOR: Line-Level Grammar Checking**: Completely refactored grammar checking to work at line level instead of sentence level
  - Now checks entire lines (with all sentences combined) before splitting into sentences
  - This prevents false positives from quotes, punctuation, and context that spans multiple sentences
  - New `_check_line_content()` method processes full lines with LanguageTool
  - Eliminates the need for complex post-processing filters for unpaired quotes
  - Much cleaner architecture that respects the natural document structure
- **🚨 MAJOR: Removed spaCy Dependency**: Simplified grammar checker to use only LanguageTool
  - Removed all spaCy code and dependencies
  - Renamed `HybridGrammarChecker` to `GrammarChecker`
  - Reduced package size and improved performance
  - LanguageTool handles all grammar, spelling, punctuation, and style checks
  - Old hybrid checker backed up as `hybrid_grammar_checker.py.backup`
  - Added `get_issues_summary()` method to new GrammarChecker class
- **Enhanced Unpaired Quote Filtering**: Fixed all unpaired quote false positives through line-level checking
  - Line-level checking naturally prevents unpaired quote issues that occurred from sentence splitting
  - Fixed: `"Honestly? Like she gets it."` no longer flagged as unpaired quotes
  - Fixed: `"You don't have to talk. Just be here."` no longer flagged as two unpaired quote errors
  - Fixed: `"Are you serious? I've been doing everything I can think of to show love."` now correctly seen as balanced
  - Single quote character issues (both regular `"` and smart quotes `"` `"`) are filtered out
  - Much simpler and more reliable than previous sentence-level filtering approach
- **Fixed Hyphenated Contractions**: Resolved false positives for hyphenated contractions like "lunch-wasn't"
  - Added text sanitization to preserve hyphenated contractions (e.g., "lunch-wasn't", "act-making")
  - Enhanced false positive filtering to skip spelling errors for partial contractions
  - Fixed: `"lunch-wasn't"` no longer flagged as spelling error "lunch-wasn"
  - Fixed: Apostrophes in contractions no longer flagged as unpaired symbols
  - Added comprehensive pattern matching for all common contractions with hyphens

### Fixed
- **Upload Timeout for Large Files**: Increased upload timeout from 2 minutes to 10 minutes to handle large documents
  - Fixed issue where frontend showed timeout error even though backend processed successfully
  - Large files (like 200KB+ Word documents) now upload without timeout errors
- **Processing Status Display**: Fixed UI getting stuck on "Uploading document..." even when backend is analyzing
  - Frontend now fetches and displays initial status immediately after upload completes
  - Progress percentage and status messages now show immediately instead of waiting for first poll
  - Improved user feedback during document processing
- **Upload Processing & Progress Display**: Fixed issue where document upload would get stuck with no feedback and percentage was not showing. 
  - Added comprehensive logging throughout the processing pipeline (backend and frontend)
  - Added visual progress bar with percentage display
  - Added real-time status updates (uploaded → parsing → checking → generating → completed)
  - Status display now shows even before first poll completes
  - Added detailed console logs for debugging status polling
- **Upload Timeout**: Fixed 30-second timeout issue that was causing uploads to fail for larger documents.
  - Increased upload timeout from 30 seconds to 2 minutes (120 seconds)
  - Created separate axios instance for uploads with longer timeout
  - Added specific timeout error handling with user-friendly message
  - Added dedicated logging for upload requests
- **Status Polling Enhancement**: Enhanced status polling with comprehensive logging and progress tracking.
  - Added detailed logging for each status check with emojis for easy identification
  - Enhanced `getProcessingStatus` function with request/response logging
  - Improved `pollStatus` function to show current progress in continuation messages
  - Added structured logging in App.tsx for status updates received
  - Better error tracking and debugging visibility for status polling issues
- **Sentence-Based Grammar Processing**: Implemented sentence-level grammar checking for better context-aware corrections.
  - Modified grammar checker to process entire sentences as units instead of individual issues
  - Multiple issues in one sentence are now combined into a single GrammarIssue
  - All fixes for a sentence are applied together, providing coherent corrections
  - Enhanced problem descriptions combine multiple issues with clear fix details
  - Improved corrected_sentence generation with all fixes applied simultaneously
  - Better context preservation for grammar corrections
- **Enhanced Issue Display Format**: Updated both frontend UI and report generator to display issues in a clean line-by-line format.
  - Frontend now shows issues with clear line numbers, original text in quotes, and bullet-pointed problems/fixes
  - Report generator (DOCX/PDF) now formats issues as "Line X" headers with indented problem descriptions
  - Added new styling for better readability: monospace font for original text, proper indentation
  - Improved visual hierarchy with line headers, consistent spacing, and color-coded elements
  - Better integration of corrected sentences when different from the main fix
  - Updated to use proper curly quotes (" and ") instead of straight quotes (") for sentence highlighting
- **Missing Method**: Added `get_issues_summary()` method to GrammarChecker class which was causing background processing to fail silently.
- **Spaced Contractions**: Fixed issue where contractions with spaces before apostrophes (e.g., "It 's" instead of "It's") were not being recognized. Added spaced contraction preprocessing in `sanitize_text()` to normalize these patterns.
- **Smart Quote Contractions**: Fixed issue where smart quotes (Unicode 8217 `'` vs ASCII 39 `'`) in contractions were not being recognized. Updated contraction detection in LanguageTool filter to handle both regular apostrophes and smart quotes.
- **LanguageTool Contraction Filtering**: Fixed issue where LanguageTool was incorrectly flagging contractions like "That's", "It's", "He's", etc. as subject-verb disagreement errors. Added intelligent filtering to prevent LanguageTool from generating false positives on contractions.
  - Added `_is_contraction_in_sentence()` method to detect contractions in LanguageTool matches
  - Filters out subject-verb agreement issues when contractions are detected
  - Handles both standard contractions (That's, It's, He's) and complex contractions (I've, We're, They'll)
  - Tested with 10+ contraction patterns - all now correctly filtered
- **Unpaired Quotes Filtering**: Fixed issue where empty quotes ('""', "''") and single quotes ('"', "'") were being flagged as unpaired symbol errors. Added false positive filtering for common punctuation issues.
  - Added `_is_false_positive_punctuation()` method to detect and skip false positive punctuation errors
  - Filters out empty quotes, single quotes in short sentences, and other common false positives
  - Tested with various quote patterns - all now correctly filtered
- **Noun Contraction Detection**: Fixed issue where noun contractions like "part's" (meaning "part is") were incorrectly flagged as subject-verb disagreement errors. The grammar checker now intelligently distinguishes between contractions and possessives, preventing false positives on noun contractions.
  - Enhanced `_is_part_of_contraction()` method to handle noun + 's patterns
  - Distinguishes between contractions (noun + 's = "is") and possessives (noun + 's)
  - Uses context analysis: if next word is adjective/verb/adverb → contraction, if noun → possessive
  - Handles gerund ambiguity (working, running, ringing, etc.) by recognizing common gerund patterns
  - Tested with 13+ patterns including "part's broken", "car's running", "dog's tail", "John's car"
  - All contraction and possessive test cases now pass with 100% accuracy
- **Proper Name Spelling Detection**: Fixed issue where proper names like "Pearlman" were incorrectly flagged as spelling mistakes. The grammar checker now intelligently detects proper names and skips spelling corrections for them, preventing false positives on names, surnames, and titles.
  - Added `_is_proper_name()` method with comprehensive heuristics to identify proper names
  - Detects names with titles (Dr., Mr., Mrs., Ms., Prof.)
  - Recognizes FirstName LastName patterns
  - Identifies common surname suffixes (son, berg, man, etc.)
  - Handles names with apostrophes (O'Connor) and hyphens (Jean-Pierre)
  - Skips spelling corrections only for detected proper names while preserving real spelling error detection
  - Tested with 20+ name patterns including the original "Pearlman" case
- **Contraction Subject-Verb Agreement Bug**: Fixed critical bug where contractions like "it's", "he's", "we're", etc. were incorrectly flagged as subject-verb disagreement errors. The grammar checker now properly recognizes contractions and skips subject-verb agreement checking for them, preventing false positives.
  - Added `_is_part_of_contraction()` method to detect when spaCy splits contractions into separate tokens
  - Enhanced subject-verb agreement checking to skip contraction patterns
  - Updated both main verb and auxiliary verb agreement checking to handle contractions
  - Comprehensive test coverage for 25+ contraction patterns including "it's", "he's", "she's", "we're", "they're", "I'm", "I've", "I'll", etc.
  - All contraction tests now pass with 100% success rate

### Added
- **Spelling Error Corrected Sentences**: Enhanced spelling error detection to show the full corrected sentence after applying the suggested fix. When a spelling error is detected, the report now displays both the suggested fix and the complete sentence with the correction applied, making it easier for users to see the context and understand the improvement.
  - Backend: Added `corrected_sentence` field to GrammarIssue schema and updated hybrid grammar checker to generate corrected sentences for spelling errors
  - Frontend: Updated IssuesPreview component to display corrected sentences in the UI with a distinct blue background for easy identification
- **Passive-to-Active Voice Conversion**: Implemented automatic conversion of passive voice sentences to active voice. When passive voice is detected, the system now provides a corrected sentence showing how to rewrite it in active voice for better clarity and engagement.
  - Backend: Added `convert_passive_to_active()` function that uses spaCy NLP parsing to identify passive constructions and automatically generate active voice alternatives
  - Enhanced passive voice detection to properly identify VBN verbs with auxpass dependencies
  - Updated grammar checker to include corrected sentences for passive voice issues
  - Improved conversion algorithm to handle complex sentences with multiple clauses and proper tense matching
  - Added intelligent verb conjugation based on auxiliary verb tense (present/past)
  - Enhanced sentence reconstruction to preserve complex sentence structure while converting passive to active voice
  - Fixed pronoun handling to properly replace pronouns (it, this, that) with appropriate subjects in active voice
  - Improved sentence span detection to correctly identify and replace passive constructions
- **Tense Consistency Corrections**: Enhanced tense consistency checking to provide corrected sentences showing how to fix tense inconsistencies. The system now automatically converts all verbs in a sentence to the same tense (present or past) based on the most common tense used.
  - Backend: Added `fix_tense_consistency()` function with comprehensive irregular verb handling and proper verb conjugation rules
  - Updated tense consistency detection to generate corrected sentences with consistent verb tenses
  - Added support for 100+ irregular verbs with proper present/past tense conversions
- **Style and Clarity Corrections**: Implemented automatic correction for common style and clarity issues including "a" vs "an" usage and redundant phrase simplification.
  - Backend: Added `fix_style_clarity()` function and `_check_style_clarity()` method
  - Detects and corrects "a" vs "an" issues before vowel sounds
  - Identifies and simplifies redundant phrases (e.g., "in order to" → "to", "due to the fact that" → "because")
  - Generates corrected sentences showing improved style and clarity
- **Confidence Threshold Filtering**: Added configurable confidence threshold to filter out low-confidence grammar issues. Only issues with 80%+ confidence are now flagged by default, reducing false positives and improving accuracy.
  - Backend: Added `confidence_threshold` parameter to HybridGrammarChecker (default: 0.8)
  - Implemented `_filter_by_confidence()` method to filter issues based on confidence scores
  - Updated grammar checking pipeline to apply confidence filtering after issue detection
- **Enhanced Passive Voice Conversion**: Improved passive-to-active voice conversion to handle complex sentences with negation and better verb conjugation.
  - Fixed negation handling in passive voice conversion (e.g., "was not created" → "did not create")
  - Improved verb conjugation for irregular verbs in passive constructions
  - Enhanced sentence structure preservation during passive-to-active conversion

### Fixed
- **Frontend Compilation Error**: Fixed missing App.tsx component that was causing "Module not found: Error: Can't resolve './App'" compilation error. Created comprehensive App component that integrates all existing components (Header, Footer, FileUpload, IssuesPreview) with proper state management, API integration, and user interface flow.
- **DOCX Parsing Regex Error**: Fixed "look-behind requires fixed-width pattern" error in document parser by replacing problematic regex with variable-width look-behind assertions with a more robust manual sentence boundary detection algorithm. The new approach properly handles abbreviations (Dr., Mr., Mrs., etc.) without regex limitations.
- **404 Errors for Web Assets**: Added favicon.ico and manifest.json files to prevent 404 errors in server logs. Created a custom favicon with "GC" branding and a proper web app manifest for better PWA support.
- **spaCy and LanguageTool Freezing**: Added comprehensive text sanitization to prevent spaCy and LanguageTool from freezing or misbehaving with .docx files containing problematic characters. The sanitization removes zero-width spaces, control characters, normalizes whitespace, and handles curly quotes/dashes that commonly cause issues in document processing.

### Added
- **Initial Release** - Complete grammar correction web application
- **Hybrid AI Grammar Checking** - Combines spaCy NLP and LanguageTool for enhanced accuracy
- **Document Processing** - Support for .doc and .docx files up to 10MB
- **Line-by-Line Analysis** - Sentence-by-sentence grammar checking within each line
- **Cross-Line Sentence Support** - Handles sentences spanning multiple lines
- **Multiple Output Formats** - Generate reports in DOCX or PDF format
- **Real-time Progress Tracking** - Live progress updates during processing
- **Modern Web Interface** - React frontend with TailwindCSS
- **RESTful API** - FastAPI backend with comprehensive documentation
- **Docker Support** - Full containerization for easy deployment
- **Development Scripts** - Automated setup and testing scripts

### Features
- **Document Upload** - Drag & drop interface for Word documents
- **Grammar Categories** - Categorizes issues by type (tense, punctuation, style, etc.)
- **Issue Preview** - Interactive preview of found issues before download
- **Confidence Scoring** - AI confidence levels for each correction suggestion
- **Summary Reports** - Comprehensive summary with issue counts by category
- **Accessibility** - WCAG 2.1 AA compliant interface
- **Error Handling** - Graceful error handling with user-friendly messages
- **File Validation** - Server-side file type and size validation
- **Temporary File Management** - Automatic cleanup of uploaded files

### Technical Implementation
- **Backend Architecture**
  - FastAPI with async/await support
  - Pydantic models for data validation
  - Background task processing
  - RESTful API design
  - Comprehensive error handling

- **Frontend Architecture**
  - React 18 with TypeScript
  - TailwindCSS for styling
  - Axios for API communication
  - React Dropzone for file uploads
  - Responsive design

- **Grammar Checking Engine**
  - spaCy for NLP processing (sentence segmentation, POS tagging, NER)
  - LanguageTool for grammar and style checking
  - Hybrid approach for cross-validation
  - Custom rule-based checks for redundancy and awkward phrasing
  - Confidence scoring and issue categorization

- **Document Processing**
  - python-docx for .docx file parsing
  - textract for .doc file parsing
  - Sentence detection with abbreviation handling
  - Line range detection for cross-line sentences

- **Report Generation**
  - python-docx for DOCX report generation
  - reportlab for PDF report generation
  - Custom styling and formatting
  - Summary statistics and categorization

### Infrastructure
- **Docker Configuration**
  - Multi-stage builds for optimization
  - Development and production configurations
  - Nginx reverse proxy setup
  - Health checks and monitoring

- **Development Tools**
  - Automated setup scripts
  - Testing framework (pytest, Jest)
  - Code quality tools (flake8, black, isort, ESLint)
  - Development server scripts
  - Integration testing

### Security
- **File Handling** - Temporary file storage with automatic cleanup
- **Input Validation** - Server-side file type and size validation
- **CORS Configuration** - Configurable cross-origin resource sharing
- **Error Messages** - Humanized error messages for end users
- **Data Privacy** - No permanent storage of document content

### Performance
- **Async Processing** - Non-blocking document processing
- **Batch Processing** - Efficient API calls to LanguageTool
- **Rate Limiting** - Configurable rate limits for API calls
- **Caching** - Optional Redis caching for improved performance
- **Optimization** - Optimized Docker images and build processes

### Documentation
- **API Documentation** - Auto-generated OpenAPI/Swagger docs
- **User Guide** - Comprehensive README with setup instructions
- **Development Guide** - Detailed development and contribution guidelines
- **Script Documentation** - Complete documentation for all development scripts

### Testing
- **Unit Tests** - Comprehensive test coverage for all components
- **Integration Tests** - End-to-end testing of the complete workflow
- **Code Quality** - Automated linting and formatting
- **Performance Testing** - Load testing for concurrent users
- **Sample Documents** - Test suite with various document structures

## [Unreleased]

### Added
- **Dialogue Category**: Added comprehensive dialogue checking for proper punctuation and formatting
  - Missing commas before closing quotation marks with dialogue tags (e.g., "Hello" said John → "Hello," said John)
  - Comma placement inside quotation marks before dialogue tags
  - Dialogue tag capitalization (should be lowercase after quotation marks)
  - Pattern matching for common dialogue tags (said, asked, replied, answered, whispered, shouted, etc.)
- **Capitalisation Category**: Added extensive capitalization error detection
  - Sentences should start with capital letters after punctuation (. ! ?)
  - Days of the week capitalization (monday → Monday)
  - Months capitalization (january → January)
  - Country names capitalization (america → America, england → England, etc.)
  - Pronoun "I" capitalization when used with verbs (i am → I am)
  - Context-aware "May" detection to differentiate between month and modal verb
- **Tense Consistency Category**: Added detection for inconsistent tense usage (past/present)
  - Detects mixing of present and past tense within the same sentence
  - Example: "I walk to the store and bought milk" → flags inconsistent tense usage
  - Example: "I walked to the store and buy milk" → flags inconsistent tense usage
  - Covers 70+ common irregular verbs (go/went, see/saw, know/knew, etc.)
  - Flags issues with guidance to review tense usage (no auto-correction due to complexity)
  - Helps maintain consistent narrative voice throughout the document
- **Frontend Category Support**: Updated UI to display new categories with distinct colors
  - Added blue color scheme for Tense Consistency category
  - Added teal color scheme for Dialogue category
  - Added cyan color scheme for Capitalisation category
  - Added orange color scheme for Grammar category
  - Updated category dropdown filters to include all new categories

### Fixed
### Infrastructure
- **Docker Frontend Build**: Switched `docker/Dockerfile.frontend` to pnpm with Corepack, added `REACT_APP_API_URL` build-arg for correct API base at build time, and replaced runtime env usage.
- **docker-compose (dev)**: Passed build arg `REACT_APP_API_URL=http://backend:8000` to frontend image; removed ineffective runtime env; added backend `--reload` command for hot reload; kept bind mount for backend code and persisted `uploads` and `temp_files` as named volumes.
- **docker-compose (prod)**: Passed build arg `REACT_APP_API_URL=http://localhost/api` for nginx reverse proxy; set `NODE_ENV=production`; nginx continues to proxy `/api` to backend.
- **Nginx**: Confirmed reverse proxy config routes `/api` to `backend` and SPA routes to `frontend`; no functional changes.
- **May Modal Verb False Positive**: Fixed incorrect capitalization of "may" when used as a modal verb
  - "whatever they may be" now correctly keeps "may" lowercase (modal verb)
  - "in May" or "May 15" correctly capitalizes "May" (the month)
  - Uses context-aware regex patterns to check for month indicators (in, on, during, of, next, last, this, until, by, from, since)
  - Also detects "May" followed by day numbers (1-31) or ordinals (1st, 2nd, etc.)
- **Ellipsis Capitalization False Positive**: Fixed incorrect capitalization after ellipsis (...)
  - Text after "..." is no longer flagged for capitalization as it's a sentence continuation
  - Example: "going home... every corner" correctly keeps "every" lowercase
  - Uses negative lookbehind to exclude periods that are part of ellipsis
- **Abbreviation Capitalization False Positive**: Fixed incorrect capitalization after common abbreviations
  - Text after abbreviations like "a.m.", "p.m.", "e.g.", "i.e.", "Dr.", "Mr.", "Mrs.", etc. is no longer incorrectly flagged
  - Example: "12:00 a.m. on the dot" correctly keeps "on" lowercase
  - Added comprehensive abbreviation detection covering 40+ common abbreviations
  - Includes time markers (a.m., p.m.), examples (e.g., i.e., viz.), titles (Dr., Mr., Mrs., Ms., Prof., Sr., Jr.), business terms (Inc., Corp., Ltd., Co.), common Latin phrases (n.b., p.s., a.k.a.), country codes (U.S., U.K., U.N., U.S.A., D.C.), academic degrees (Ph.D., B.A., M.A., B.S., M.S.), and measurements (ft., in., lb., oz., vol.)
- **URL Capitalization False Positive**: Fixed incorrect capitalization detection near URLs
  - Text following URLs no longer triggers false positives
  - Example: "April 4, 2024. https://example.com" correctly ignores the period before URL
  - Detects URLs by looking both before and after periods (http://, https://, www., .com/, .org/, etc.)
  - Prevents flagging legitimate sentence breaks that occur before web links

### Updated
- **LanguageTool Python Library** - Updated from version 2.7.1 to 2.9.4 for improved performance and bug fixes
- **Textract Library** - Replaced with docx2txt due to pip compatibility issues with textract 1.6.5
- **spaCy Library** - Updated to version 3.8.7 for Python 3.12 compatibility
- **Pydantic Library** - Updated to version 2.11.10 for compatibility with spaCy 3.8.7

### Fixed
- **Major Grammar Checker Issues** - Fixed incorrect subject-verb agreement detection that was flagging correct first-person singular verbs (like "I love", "I feel") as errors
- **Contraction Handling** - Fixed false positives on contractions like "it's", "that's" being flagged as subject-verb disagreements
- **Redundancy Detection** - Improved redundancy detection to only flag truly redundant phrases, not normal conjunctions like "and I", "and you"
- **Tense Consistency** - Enhanced tense consistency detection with context awareness for legitimate tense shifts (quoted speech, time expressions, subordinating conjunctions)
- **Long Sentence Detection** - Removed long sentence detection per user request - no longer flags sentences as issues based on length
- **Frontend Issues Display** - Fixed frontend not showing actual grammar issues by:
  - Added new `/results/{task_id}` endpoint to return issues and summary data
  - Updated frontend to fetch and display real issues instead of mock data
  - Modified backend to store actual issues data in processing results
- **Results Accuracy** - Reduced false positives from 898 to 506 issues, focusing on legitimate grammar problems
- **Installation Issues** - Resolved pip dependency conflicts and package compatibility problems
- **spaCy Compatibility** - Fixed Python 3.12 compatibility issues by updating spaCy and Pydantic versions
- **spaCy Model Loading** - Fixed spaCy model download and loading process with direct wheel installation fallback
- **Morphological Analysis** - Improved spaCy morph.get() method usage with proper error handling
- **Subject-Verb Agreement** - Enhanced detection of auxiliary verb agreement issues (e.g., "The cats is running")
- **Grammar Checker Initialization** - Added better error handling and status messages for model loading
- **Document Parsing** - Enhanced .doc file support with multiple fallback methods
- **Development Setup Script** - Updated dev-setup.sh to use pnpm for frontend dependencies
- **Frontend Package Management** - Fixed TypeScript version conflicts using pnpm's --no-strict-peer-dependencies flag
- **Setup Verification** - Added comprehensive verification step to ensure all components are working correctly

### Planned Features
- **Advanced Grammar Rules** - Customizable grammar rule sets
- **Language Variants** - Support for different English dialects (US, UK, AU)
- **Batch Processing** - Process multiple documents simultaneously
- **User Accounts** - User authentication and document history
- **API Keys** - API access for third-party integrations
- **Advanced Analytics** - Detailed processing statistics and insights
- **Plugin System** - Extensible architecture for custom grammar rules
- **Real-time Collaboration** - Multiple users working on the same document
- **Version Control** - Track changes and revisions
- **Export Options** - Additional export formats (HTML, Markdown, etc.)

### Technical Improvements
- **Microservices Architecture** - Split into smaller, focused services
- **Message Queue** - Redis/RabbitMQ for better task management
- **Database Integration** - PostgreSQL for persistent storage
- **Caching Layer** - Redis for improved performance
- **Monitoring** - Prometheus/Grafana for system monitoring
- **Logging** - Structured logging with ELK stack
- **CI/CD Pipeline** - Automated testing and deployment
- **Load Balancing** - Horizontal scaling support
- **SSL/TLS** - HTTPS support for production deployments
- **Backup System** - Automated backup and recovery

### Performance Optimizations
- **Parallel Processing** - Multi-threaded document processing
- **Memory Optimization** - Efficient memory usage for large documents
- **CDN Integration** - Content delivery network for static assets
- **Database Optimization** - Query optimization and indexing
- **Caching Strategy** - Multi-level caching implementation
- **Resource Management** - Better resource allocation and cleanup

---

## Version History

- **1.0.0** - Initial release with core functionality
- **Future versions** - Will follow semantic versioning (MAJOR.MINOR.PATCH)

## Contributing

When making changes, please update this changelog following the format above. Include:
- New features and improvements
- Bug fixes
- Breaking changes
- Deprecations
- Security updates
- Performance improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.
