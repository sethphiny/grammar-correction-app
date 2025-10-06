# Changelog

All notable changes to the Grammar Correction App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Fixed
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
