# Logging Configuration Guide

## Overview

The refactored `LLMGrammarChecker` now uses Python's `logging` module instead of print statements. This provides better control over log output, levels, and destinations.

## Quick Start

### Basic Configuration

Add this to your application's entry point (e.g., `main.py`):

```python
import logging

# Configure logging at application startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### For Development (Detailed Logs)

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### For Production (Important Logs Only)

```python
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Log Levels Used

### INFO
- Initialization messages
- Start/completion of grammar checking
- Number of paragraphs processed
- Number of issues found

**Example Output:**
```
2025-10-23 14:30:22 - llm_grammar_checker - INFO - LLMGrammarChecker initialized with gpt-4o-mini (context window: 128000 tokens)
2025-10-23 14:30:25 - llm_grammar_checker - INFO - Starting full LLM-based grammar check
2025-10-23 14:30:25 - llm_grammar_checker - INFO - Processing 5 paragraphs
2025-10-23 14:30:35 - llm_grammar_checker - INFO - Complete - Found 12 issues across 5 paragraphs
```

### DEBUG
- Token counts and limits
- Filtered issues (British/American variants, hallucinations)
- Detailed processing information

**Example Output:**
```
2025-10-23 14:30:26 - llm_grammar_checker - DEBUG - Checking paragraph 1 (450 chars, 120 prompt tokens, 300 max response tokens)
2025-10-23 14:30:27 - llm_grammar_checker - DEBUG - Filtered out British/American variant issue: Use American spelling...
2025-10-23 14:30:27 - llm_grammar_checker - DEBUG - Filtered out hallucinated issue (similarity: 0.45): 'The quick brown...'
```

### WARNING
- Missing API keys
- Optional dependencies not installed
- Token limit approaching/exceeded
- API retry attempts
- Progress callback errors

**Example Output:**
```
2025-10-23 14:30:22 - llm_grammar_checker - WARNING - json-repair package not installed. Falling back to basic JSON repair.
2025-10-23 14:30:30 - llm_grammar_checker - WARNING - API call failed (attempt 1/3): RateLimitError. Retrying in 1.0s...
2025-10-23 14:30:35 - llm_grammar_checker - WARNING - Token limit exceeded: 130000 > 128000 (prompt: 125000, response: 5000)
```

### ERROR
- Initialization failures
- API call failures (after retries)
- JSON parsing errors
- Unexpected exceptions

**Example Output:**
```
2025-10-23 14:30:40 - llm_grammar_checker - ERROR - API call failed after 3 attempts: RateLimitError
2025-10-23 14:30:45 - llm_grammar_checker - ERROR - JSON parsing error in paragraph 3: Expecting value: line 1 column 1 (char 0). Response preview: Error: Rate limit...
```

## Advanced Configuration

### Different Levels for Different Loggers

```python
import logging

# Root logger at INFO
logging.basicConfig(level=logging.INFO)

# Set specific logger to DEBUG
llm_logger = logging.getLogger('services.llm_grammar_checker')
llm_logger.setLevel(logging.DEBUG)
```

### File Output

```python
import logging

# Log to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grammar_checker.log'),
        logging.StreamHandler()  # Also print to console
    ]
)
```

### JSON Structured Logging

```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)
```

### Rotating File Handler

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'grammar_checker.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger('services.llm_grammar_checker')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## Integration with Existing Code

### FastAPI Integration

```python
from fastapi import FastAPI
import logging

# Configure at app startup
@app.on_event("startup")
async def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### Testing Configuration

```python
import logging
import pytest

@pytest.fixture
def configure_test_logging():
    """Configure logging for tests"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s - %(message)s'
    )
```

## Environment-Based Configuration

```python
import os
import logging

# Get log level from environment
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Add to `.env`:
```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=WARNING
```

## Filtering Logs

### Only Show LLM Grammar Checker Logs

```python
import logging

# Silence other loggers
logging.basicConfig(level=logging.WARNING)

# Enable LLM grammar checker
llm_logger = logging.getLogger('services.llm_grammar_checker')
llm_logger.setLevel(logging.INFO)
llm_logger.addHandler(logging.StreamHandler())
```

### Exclude Specific Messages

```python
import logging

class ExcludeFilter(logging.Filter):
    def __init__(self, exclude_patterns):
        super().__init__()
        self.exclude_patterns = exclude_patterns
    
    def filter(self, record):
        message = record.getMessage()
        return not any(pattern in message for pattern in self.exclude_patterns)

# Apply filter
handler = logging.StreamHandler()
handler.addFilter(ExcludeFilter(['Filtered out', 'not installed']))
logging.root.addHandler(handler)
```

## Monitoring and Observability

### Log Aggregation (CloudWatch, Datadog, etc.)

```python
import logging
import watchtower  # For AWS CloudWatch

handler = watchtower.CloudWatchLogHandler(
    log_group='/app/grammar-checker',
    stream_name='llm-checker'
)
logging.getLogger('services.llm_grammar_checker').addHandler(handler)
```

### Metrics from Logs

Monitor these log messages for metrics:
- "Complete - Found X issues" → Track issue count over time
- "API call failed" → Track failure rate
- "Timeout checking paragraph" → Track timeout rate
- "Token limit exceeded" → Track large documents

## Troubleshooting

### Problem: No logs appearing

**Solution:**
```python
import logging

# Ensure handlers are configured
if not logging.root.handlers:
    logging.basicConfig(level=logging.INFO)
```

### Problem: Too much output

**Solution:**
```python
# Increase log level
logging.getLogger('services.llm_grammar_checker').setLevel(logging.WARNING)
```

### Problem: Missing debug logs

**Solution:**
```python
# Ensure DEBUG level is set
logging.getLogger('services.llm_grammar_checker').setLevel(logging.DEBUG)
```

## Best Practices

1. **Configure once at startup** - Don't call `basicConfig()` multiple times
2. **Use appropriate levels** - DEBUG for development, INFO for production
3. **Include timestamps** - Essential for debugging async operations
4. **Log exceptions with exc_info** - Already done in refactored code
5. **Don't log sensitive data** - Be careful with API keys, user data
6. **Rotate log files** - Prevent disk space issues
7. **Use structured logging** - Easier to parse and analyze
8. **Monitor log levels** - Adjust based on needs

## Migration from Print Statements

All previous `print()` statements have been replaced:

| Old Code | New Code |
|----------|----------|
| `print("✅ [LLMGrammarChecker] ...")` | `logger.info(...)` |
| `print("⚠️ [LLMGrammarChecker] ...")` | `logger.warning(...)` |
| `print("❌ [LLMGrammarChecker] ...")` | `logger.error(...)` |
| `print(f"   ⚠️ Filtered out...")` | `logger.debug(...)` |

The emoji prefixes have been removed as log levels provide the same information in a more standard way.

---

**Last Updated**: October 23, 2025

