# Grammar Correction Web App

A Dockerized web application that allows users to upload Word documents (.doc or .docx), checks them line by line and sentence by sentence using a hybrid approach combining spaCy and LanguageTool, and generates comprehensive correction reports.

## Features

- **Web-based UI**: React frontend with TailwindCSS
- **File Upload**: Restricted to .doc and .docx files (10MB limit)
- **Advanced Grammar Checking**: Pattern-based + AI-enhanced corrections
- **Selective Category Analysis**: Choose which grammar categories to check
- **✨ AI-Enhanced Suggestions (Premium)**: Optional LLM-powered improvements (~$0.01-0.03 per MB)
- **Line-by-Line Analysis**: Processes text sentence by sentence within each line
- **Cross-Line Sentence Support**: Handles sentences spanning multiple lines
- **Real-Time Progress**: WebSocket-based progress updates during processing
- **Multiple Output Formats**: DOCX or PDF reports
- **Preview Mode**: Review corrections before download
- **Accessibility**: WCAG 2.1 AA compliant
- **Docker Support**: Full containerization for easy deployment

## Quick Start

### Using Docker (Recommended)

```bash
# Clone and navigate to the project
cd grammar-correction-app

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Manual Setup

#### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python3 -m pip install -r requirements.txt

# Download spaCy language model for passive voice detection
python3 -m spacy download en_core_web_sm

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note**: The spaCy model `en_core_web_sm` is required for smart passive voice detection. If not installed, the feature will be automatically disabled with a warning message.

#### Optional: Enable AI-Enhanced Suggestions

For better grammar corrections using OpenAI GPT-4o-mini (~$0.01-0.03 per MB):

```bash
# Install additional dependencies
python3 -m pip install openai tiktoken

# Add to your .env file
echo "LLM_ENHANCEMENT_ENABLED=true" >> .env
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env

# Test connection
python3 test_llm_connection.py

# Restart backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Get API Key:** https://platform.openai.com/api-keys  
**Quick Guide:** See `docs/QUICK_START_LLM.md`  
**Full Guide:** See `docs/API_KEYS_SETUP_GUIDE.md`

#### Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

## Architecture

### Advanced Grammar Checking

The application uses multiple sophisticated approaches:

1. **Pattern-Based Checking**:
   - 100+ redundant phrases with corrections
   - 100+ awkward phrasing alternatives
   - Common punctuation errors
   - Grammar mistakes (homophones, verb errors, double negatives)
   - Capitalization errors
   - Tense consistency issues
   - Common spelling mistakes
   - 40+ wordy phrases for concision

2. **spaCy NLP (Linguistic Analysis)**:
   - **Smart Passive Voice Detection**: Uses dependency parsing (auxpass) to identify true passive constructions
     - Eliminates false positives (e.g., "is nuanced" is NOT flagged)
     - Only flags problematic passives without clear agents
     - Generates context-specific fix suggestions
   - Sentence segmentation and tokenization
   - Part-of-speech tagging for advanced analysis

3. **AI-Powered Enhancement (Optional Premium Feature)**:
   - **Selective LLM Enhancement**: Only processes complex/uncertain issues (20-30%)
   - **Smart Filtering**: Enhances low-confidence issues (< 85%) and complex categories
   - **Batch Processing**: Groups issues for efficient API usage
   - **Cost Optimization**: Typical cost $0.01-0.03 per MB document
   - **Quality Boost**: +40-50% improvement on complex grammar issues
   - **Graceful Degradation**: Falls back to pattern-based checking if unavailable

4. **Intelligent Filtering**:
   - Skips intentional passive voice patterns ("It was...", "There was...")
   - Excludes technical/academic contexts (framework, methodology, research)
   - Context-aware duplicate detection
   - Confidence scoring for each issue
   - User-selectable category filtering (analyze only what you need)

### Report Format

```
Line 4–5, Sentence 1
"Even in retirement, he carried the image of a railing set in stone, the kind that never moved. New boys come to him to watch him measure so they can learn."
• Problem: Tense shift → "come" (present) vs. surrounding past tense.
• Fix: → "New boys came to him to watch…"

✅ Summary
• Verb tense consistency issues: 5
• Awkward phrasing: 3
• Redundancy: 2
• Grammar/punctuation: 4
```

## API Endpoints

- `POST /upload` - Upload document for analysis
- `GET /status/{task_id}` - Check processing status
- `GET /download/{task_id}` - Download generated report
- `GET /results/{task_id}` - Get processing results (issues and summary)
- `GET /categories` - Get available grammar checking categories
- `GET /health` - Health check
- `WebSocket /ws/{task_id}` - Real-time progress updates

## Documentation

### 📚 Guides

- **[Quick Start: LLM Enhancement](docs/QUICK_START_LLM.md)** - 15-minute setup for AI-powered corrections
- **[API Keys Setup Guide](docs/API_KEYS_SETUP_GUIDE.md)** - How to get and configure API keys
- **[LLM Implementation Guide](docs/LLM_IMPLEMENTATION_GUIDE.md)** - Complete implementation plans and architecture
- **[LLM Cost Reference](docs/LLM_COST_REFERENCE.md)** - Cost calculator and budget planning

### 💰 Cost Information

| Feature | Cost | When to Use |
|---------|------|-------------|
| Pattern-Based Checking | Free | Always (default) |
| AI-Enhanced Suggestions | $0.01-0.03/MB | Complex documents, premium quality |

**See:** `docs/LLM_COST_REFERENCE.md` for detailed cost breakdown

## Configuration

### Environment Variables

```bash
# Backend
LANGUAGETOOL_URL=http://localhost:8081  # Optional: local LanguageTool server
MAX_FILE_SIZE=10485760  # 10MB
PROCESSING_TIMEOUT=300  # 5 minutes

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Grammar Rules

The system supports customizable grammar rules:

- Verb tense consistency
- Subject-verb agreement
- Punctuation rules
- Style and clarity
- Redundancy detection
- Awkward phrasing

## Development

### Running Tests

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && pnpm test

# All tests
./scripts/test-all.sh
```

### Code Quality

```bash
# Backend linting
cd backend && flake8 . && black . && isort .

# Frontend linting
cd frontend && pnpm run lint
```

## Deployment

### Production Docker

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Environment Setup

1. Copy `env.example` to `.env`
2. Configure your LanguageTool server (optional)
3. Set appropriate file size limits
4. Configure CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the GitHub repository.
