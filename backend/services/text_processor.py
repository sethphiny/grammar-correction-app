"""
Enhanced text processing inspired by LanguageTool Sublime patterns
"""
import re
import logging
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from .grammar_config import GrammarCheckerConfig, TextProcessingMode

logger = logging.getLogger(__name__)

class SentenceSplitter(ABC):
    """Abstract base class for sentence splitters"""
    
    @abstractmethod
    def split_sentences(self, text: str) -> List[Dict[str, any]]:
        """Split text into sentences with metadata"""
        pass

class SpacySentenceSplitter(SentenceSplitter):
    """spaCy-based sentence splitter"""
    
    def __init__(self, nlp_model):
        self.nlp = nlp_model
    
    def split_sentences(self, text: str) -> List[Dict[str, any]]:
        """Split text using spaCy for better accuracy"""
        try:
            doc = self.nlp(text)
            sentences = []
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if sentence_text and len(sentence_text) > 3:
                    sentences.append({
                        'text': sentence_text,
                        'start_offset': sent.start_char,
                        'end_offset': sent.end_char,
                        'spacy_sent': sent,  # Keep spaCy object for analysis
                        'tokens': [token.text for token in sent],
                        'pos_tags': [token.pos_ for token in sent],
                        'dependencies': [(token.text, token.dep_, token.head.text) for token in sent]
                    })
            
            return sentences
            
        except Exception as e:
            logger.error(f"spaCy sentence splitting failed: {e}")
            # Fallback to regex
            return RegexSentenceSplitter().split_sentences(text)

class RegexSentenceSplitter(SentenceSplitter):
    """Regex-based sentence splitter (fallback)"""
    
    def split_sentences(self, text: str) -> List[Dict[str, any]]:
        """Split text using regex patterns"""
        # More sophisticated sentence splitting that handles abbreviations
        abbreviations = r'\b(Dr|Mr|Mrs|Ms|Prof|Prof\.|Inc|Inc\.|Corp|Corp\.|Ltd|Ltd\.|Co|Co\.|e\.g\.|i\.e\.|etc\.|vs\.|vs)\b'
        
        # Replace abbreviations temporarily to avoid false sentence breaks
        temp_text = text
        abbr_matches = list(re.finditer(abbreviations, text, re.IGNORECASE))
        abbr_replacements = {}
        
        for i, match in enumerate(abbr_matches):
            placeholder = f"__ABBR_{i}__"
            abbr_replacements[placeholder] = match.group(0)
            temp_text = temp_text.replace(match.group(0), placeholder)
        
        # Split on sentence endings but preserve quotes
        sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_endings, temp_text)
        
        # Restore abbreviations
        for placeholder, original in abbr_replacements.items():
            for i, sentence in enumerate(sentences):
                sentences[i] = sentence.replace(placeholder, original)
        
        # Process sentences and add metadata
        processed_sentences = []
        current_offset = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                start_offset = text.find(sentence, current_offset)
                end_offset = start_offset + len(sentence)
                
                processed_sentences.append({
                    'text': sentence,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'spacy_sent': None,
                    'tokens': sentence.split(),
                    'pos_tags': [],  # Not available with regex
                    'dependencies': []  # Not available with regex
                })
                
                current_offset = end_offset
        
        return processed_sentences

class TextProcessor:
    """Enhanced text processor with multiple strategies"""
    
    def __init__(self, config: GrammarCheckerConfig, nlp_model=None):
        self.config = config
        self.nlp_model = nlp_model
        self.sentence_splitter = self._create_sentence_splitter()
    
    def _create_sentence_splitter(self) -> SentenceSplitter:
        """Create appropriate sentence splitter based on configuration"""
        if (self.config.text_processing_mode == TextProcessingMode.SPACY and 
            self.nlp_model is not None):
            return SpacySentenceSplitter(self.nlp_model)
        elif self.config.text_processing_mode == TextProcessingMode.REGEX:
            return RegexSentenceSplitter()
        else:  # HYBRID mode
            if self.nlp_model is not None:
                return SpacySentenceSplitter(self.nlp_model)
            else:
                logger.warning("spaCy model not available, falling back to regex")
                return RegexSentenceSplitter()
    
    def split_into_sentences(self, text: str) -> List[Dict[str, any]]:
        """Split text into sentences with metadata"""
        if not text.strip():
            return []
        
        # Clean the text first
        cleaned_text = self._clean_text(text)
        
        # Split into sentences
        sentences = self.sentence_splitter.split_sentences(cleaned_text)
        
        # Filter sentences based on configuration
        filtered_sentences = []
        for sentence in sentences:
            if (self.config.min_sentence_length <= len(sentence['text']) <= 
                self.config.max_sentence_length):
                filtered_sentences.append(sentence)
            else:
                logger.debug(f"Filtered out sentence: length {len(sentence['text'])}")
        
        return filtered_sentences
    
    def split_into_chunks(self, text: str) -> List[Dict[str, any]]:
        """Split text into manageable chunks for processing"""
        if len(text) <= self.config.chunk_size:
            return [{
                'text': text,
                'start_offset': 0,
                'end_offset': len(text),
                'chunk_index': 0,
                'total_chunks': 1
            }]
        
        chunks = []
        chunk_index = 0
        start_offset = 0
        
        while start_offset < len(text):
            # Find a good breaking point (end of sentence)
            end_offset = min(start_offset + self.config.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end_offset < len(text):
                # Look for sentence ending within the last 200 characters
                search_start = max(start_offset, end_offset - 200)
                search_text = text[search_start:end_offset]
                
                # Find last sentence ending
                sentence_endings = re.finditer(r'[.!?]\s+', search_text)
                last_ending = None
                for match in sentence_endings:
                    last_ending = match.end() + search_start
                
                if last_ending and last_ending > start_offset:
                    end_offset = last_ending
            
            chunk_text = text[start_offset:end_offset].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'chunk_index': chunk_index,
                    'total_chunks': 0  # Will be updated later
                })
                chunk_index += 1
            
            start_offset = end_offset
        
        # Update total chunks count
        for chunk in chunks:
            chunk['total_chunks'] = len(chunks)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common prefixes that aren't part of the actual content
        prefixes_to_remove = [
            r'^Redundant phrases\s*:\s*',
            r'^Grammar issues\s*:\s*',
            r'^Punctuation errors\s*:\s*',
            r'^Verb tense issues\s*:\s*',
            r'^Awkward phrasing\s*:\s*',
            r'^Issues found\s*:\s*',
            r'^Problems\s*:\s*',
            r'^Errors\s*:\s*',
            r'^Spelling errors\s*:\s*',
            r'^Incorrect prepositions\s*:\s*',
            r'^Preposition errors\s*:\s*',
            r'^Subject-verb agreement\s*:\s*',
            r'^Agreement issues\s*:\s*',
            r'^Capitalization errors\s*:\s*',
            r'^Capitalization issues\s*:\s*',
            r'^Word choice\s*:\s*',
            r'^Word choice issues\s*:\s*',
            r'^Style issues\s*:\s*',
            r'^Style problems\s*:\s*',
            r'^Clarity issues\s*:\s*',
            r'^Clarity problems\s*:\s*',
            r'^Conciseness issues\s*:\s*',
            r'^Conciseness problems\s*:\s*',
            r'^Flow issues\s*:\s*',
            r'^Flow problems\s*:\s*',
            r'^Tone issues\s*:\s*',
            r'^Tone problems\s*:\s*',
            r'^Issue\s*:\s*',
            r'^Problem\s*:\s*',
            r'^Error\s*:\s*',
            r'^Fix\s*:\s*',
            r'^Correction\s*:\s*',
            r'^Note\s*:\s*',
            r'^Comment\s*:\s*',
            r'^Suggestion\s*:\s*',
            r'^Recommendation\s*:\s*',
            r'^\d+\.\s*',
            r'^\(\d+\)\s*',
            r'^[a-zA-Z]\)\s*',
            r'^[ivx]+\.\s*',
        ]
        
        cleaned = text
        for prefix_pattern in prefixes_to_remove:
            cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def extract_context(self, text: str, offset: int, length: int) -> Dict[str, str]:
        """Extract context around a specific position in text"""
        context_start = max(0, offset - self.config.context_window_size)
        context_end = min(len(text), offset + length + self.config.context_window_size)
        
        before_context = text[context_start:offset]
        after_context = text[offset + length:context_end]
        full_context = text[context_start:context_end]
        
        return {
            'before': before_context,
            'after': after_context,
            'full': full_context,
            'context_offset': offset - context_start
        }
    
    def is_proper_name(self, text: str, full_text: str, offset: int) -> bool:
        """Enhanced proper name detection"""
        text = text.strip()
        
        if len(text) < 2:
            return False
        
        if not text[0].isupper():
            return False
        
        # Use spaCy if available for better NER
        if self.nlp_model:
            try:
                doc = self.nlp_model(full_text)
                for token in doc:
                    if token.idx <= offset < token.idx + len(token.text):
                        # Check if it's a named entity
                        if token.ent_type_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART"]:
                            return True
                        # Check if it's a proper noun
                        if token.pos_ == "PROPN":
                            return True
                        break
            except Exception as e:
                logger.debug(f"spaCy NER failed: {e}")
        
        # Fallback to regex patterns
        context_start = max(0, offset - 50)
        context_end = min(len(full_text), offset + len(text) + 50)
        context = full_text[context_start:context_end]
        
        # Common patterns that indicate proper names
        name_indicators = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b(Dr|Mr|Mrs|Ms|Prof|Professor)\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+(Jr|Sr|III|IV|V)\b',
        ]
        
        for pattern in name_indicators:
            if re.search(pattern, context, re.IGNORECASE):
                return True
        
        return False
