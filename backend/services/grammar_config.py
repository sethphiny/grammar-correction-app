"""
Enhanced configuration system inspired by LanguageTool Sublime plugin patterns
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class ServerType(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    AUTO = "auto"  # Try local first, fallback to remote

class TextProcessingMode(str, Enum):
    SPACY = "spacy"
    REGEX = "regex"
    HYBRID = "hybrid"  # Use spaCy when available, fallback to regex

@dataclass
class GrammarCheckerConfig:
    """Configuration for the grammar checker inspired by LanguageTool Sublime patterns"""
    
    # Language settings
    language: str = "en-US"
    supported_languages: list = field(default_factory=lambda: ["en-US", "en-GB", "en-AU"])
    
    # Server configuration
    server_type: ServerType = ServerType.AUTO
    local_server_url: str = "http://localhost:8081"
    remote_server_url: str = "https://api.languagetool.org/v2"
    local_jar_path: Optional[str] = None
    
    # Text processing settings
    text_processing_mode: TextProcessingMode = TextProcessingMode.HYBRID
    max_text_length: int = 20000
    max_issues_per_sentence: int = 5
    max_issues_per_chunk: int = 50
    
    # Feature toggles
    enable_spacy: bool = True
    enable_custom_rules: bool = True
    enable_proper_name_filtering: bool = True
    enable_confidence_scoring: bool = True
    
    # Quality thresholds
    confidence_threshold: float = 0.7
    min_sentence_length: int = 3
    max_sentence_length: int = 1000
    
    # Performance settings
    chunk_size: int = 1000  # Characters per chunk
    max_concurrent_requests: int = 3
    request_timeout: int = 30  # seconds
    
    # Error handling
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    fallback_on_error: bool = True
    
    # Custom rules configuration
    custom_rules_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "collective_nouns": True,
        "subject_verb_agreement": True,
        "article_usage": True,
        "tense_consistency": True,
        "redundancy_detection": True
    })
    
    # Advanced settings
    enable_context_analysis: bool = True
    context_window_size: int = 50  # Characters before/after error
    enable_semantic_analysis: bool = False  # Future feature
    
    @classmethod
    def from_env(cls) -> 'GrammarCheckerConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('LANGUAGETOOL_LANGUAGE'):
            config.language = os.getenv('LANGUAGETOOL_LANGUAGE')
        
        if os.getenv('LANGUAGETOOL_SERVER_TYPE'):
            config.server_type = ServerType(os.getenv('LANGUAGETOOL_SERVER_TYPE'))
        
        if os.getenv('LANGUAGETOOL_LOCAL_URL'):
            config.local_server_url = os.getenv('LANGUAGETOOL_LOCAL_URL')
        
        if os.getenv('LANGUAGETOOL_REMOTE_URL'):
            config.remote_server_url = os.getenv('LANGUAGETOOL_REMOTE_URL')
        
        if os.getenv('LANGUAGETOOL_JAR_PATH'):
            config.local_jar_path = os.getenv('LANGUAGETOOL_JAR_PATH')
        
        if os.getenv('LANGUAGETOOL_MAX_TEXT_LENGTH'):
            config.max_text_length = int(os.getenv('LANGUAGETOOL_MAX_TEXT_LENGTH'))
        
        if os.getenv('LANGUAGETOOL_CONFIDENCE_THRESHOLD'):
            config.confidence_threshold = float(os.getenv('LANGUAGETOOL_CONFIDENCE_THRESHOLD'))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'language': self.language,
            'server_type': self.server_type.value,
            'local_server_url': self.local_server_url,
            'remote_server_url': self.remote_server_url,
            'text_processing_mode': self.text_processing_mode.value,
            'max_text_length': self.max_text_length,
            'max_issues_per_sentence': self.max_issues_per_sentence,
            'enable_spacy': self.enable_spacy,
            'enable_custom_rules': self.enable_custom_rules,
            'confidence_threshold': self.confidence_threshold,
            'chunk_size': self.chunk_size,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_timeout': self.request_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'fallback_on_error': self.fallback_on_error,
            'custom_rules_enabled': self.custom_rules_enabled,
            'enable_context_analysis': self.enable_context_analysis,
            'context_window_size': self.context_window_size
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if self.max_text_length <= 0:
            return False
        
        if self.max_issues_per_sentence <= 0:
            return False
        
        if not 0.0 <= self.confidence_threshold <= 1.0:
            return False
        
        if self.chunk_size <= 0:
            return False
        
        if self.max_concurrent_requests <= 0:
            return False
        
        if self.request_timeout <= 0:
            return False
        
        if self.max_retries < 0:
            return False
        
        if self.retry_delay < 0:
            return False
        
        return True

# Default configuration instance
DEFAULT_CONFIG = GrammarCheckerConfig()
