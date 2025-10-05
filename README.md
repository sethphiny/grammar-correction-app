# Grammar Correction Web Application

A Dockerized web application that allows users to upload Word documents (.doc or .docx), performs comprehensive grammar and style checking, and generates detailed correction reports in DOCX or PDF format.

## Features

- **Web-based Interface**: Modern React frontend with TailwindCSS
- **Document Upload**: Supports .doc and .docx files up to 10MB
- **Comprehensive Analysis**: Line-by-line and sentence-by-sentence grammar checking
- **Multiple Output Formats**: Generate reports in DOCX or PDF
- **Real-time Progress**: Live progress tracking during processing
- **Detailed Reports**: Includes original text, problems, and suggested fixes
- **Summary Statistics**: Categorized issue counts and totals
- **Accessibility**: WCAG 2.1 AA compliant interface

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LanguageTool**: Grammar checking engine
- **python-docx**: Document parsing and generation
- **ReportLab**: PDF report generation
- **textract**: Legacy .doc file support

### Frontend
- **React**: Modern JavaScript library with TypeScript
- **TailwindCSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **React Dropzone**: File upload handling

### Deployment
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Frontend serving and API proxying

## Quick Start

### Prerequisites
- Docker and Docker Compose (for production)
- Python 3.10+ (for local development)
- Node.js 18+ (for local development)
- Git

### Production Setup (Docker)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd grammar-correction-app
   ```

2. **Build and start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development Setup

**Quick Setup (Recommended)**:
```bash
# One-time setup
./scripts/dev-setup.sh

# Start both servers
./scripts/start-dev.sh
```

**Manual Setup**:

1. **Setup Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Setup Frontend** (in another terminal):
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Development Scripts

The project includes helpful development scripts in the `scripts/` directory:

- `dev-setup.sh` - Initial setup for local development
- `start-dev.sh` - Start both backend and frontend servers
- `start-backend.sh` - Start only backend server
- `start-frontend.sh` - Start only frontend server
- `test-all.sh` - Run all tests
- `test-backend.sh` - Run backend tests
- `test-frontend.sh` - Run frontend tests

See `scripts/README.md` for detailed usage instructions.

## Usage

1. **Upload Document**: Drag and drop or select a .doc/.docx file
2. **Choose Format**: Select DOCX or PDF output format
3. **Custom Name**: Optionally specify a custom filename
4. **Start Analysis**: Click "Start Analysis" to begin processing
5. **Monitor Progress**: Watch real-time progress updates
6. **Review Results**: Preview issues found and summary statistics
7. **Download Report**: Download the generated correction report

## API Endpoints

### Upload Document
```
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: Word document (.doc or .docx)
- output_format: "docx" or "pdf"
- custom_filename: Optional custom filename
```

### Check Processing Status
```
GET /status/{processing_id}
```

### Download Report
```
GET /download/{processing_id}
```

### Health Check
```
GET /health
```

## Grammar Checking Features

### Issue Categories
- **Verb Tense Consistency**: Detects tense shifts and inconsistencies
- **Awkward Phrasing**: Identifies unclear or wordy constructions
- **Redundancy**: Finds repetitive or unnecessary phrases
- **Grammar/Punctuation**: Catches comma errors, subject-verb agreement, quotation marks

### Report Format
Each issue includes:
- **Location**: Line number(s) and sentence number
- **Original Text**: The problematic text in context
- **Problem**: Detailed explanation of the issue
- **Fix**: Suggested correction
- **Confidence**: Detection confidence score

## Configuration

### Environment Variables
- `REACT_APP_API_URL`: Frontend API base URL (default: http://localhost:8000)

### File Limits
- Maximum file size: 10MB
- Supported formats: .doc, .docx
- Processing timeout: 300 seconds
- Concurrent users: Up to 5 simultaneous uploads

## Security Features

- **File Validation**: Server-side file type verification
- **Temporary Storage**: Files deleted after processing
- **No Data Retention**: Document content not stored permanently
- **CORS Protection**: Configured for specific origins

## Performance Optimizations

- **Batch Processing**: Up to 100 sentences per API call
- **Rate Limiting**: Maximum 5 requests per second
- **Fallback Support**: Local grammar checking when API unavailable
- **Efficient Parsing**: Optimized document extraction

## Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Test Coverage
- Unit tests for all grammar checking functions
- Integration tests for end-to-end processing
- Load testing for concurrent uploads
- Sample documents with various structures

## Troubleshooting

### Common Issues

1. **LanguageTool Connection Failed**
   - Check internet connection
   - Verify LanguageTool service availability
   - Application will fall back to local checking

2. **File Upload Fails**
   - Verify file format (.doc or .docx only)
   - Check file size (max 10MB)
   - Ensure file is not password-protected

3. **Processing Timeout**
   - Large documents may take longer
   - Check server resources
   - Verify LanguageTool API response times

### Logs
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
