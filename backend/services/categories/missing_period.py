"""
Missing Period category - Detects sentences missing periods or proper end punctuation.

Implements detection for:
- Sentences ending without punctuation
- Capital letter after comma (should be period)
- Multiple sentences run together without periods
- Missing period before new sentence
- Sentences ending with comma instead of period
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class MissingPeriodCategory(BaseCategory):
    """
    Detects missing periods and end punctuation.
    
    Total patterns: 8
    Confidence: 0.80-0.90
    """
    
    def get_category_name(self) -> str:
        return 'missing_period'
    
    def get_display_name(self) -> str:
        return 'Missing Period'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return missing period detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Capital letter after comma (likely missing period)
            (r',\s+[A-Z][a-z]+\s+',
             "Missing period: Capital letter after comma suggests new sentence - use period instead of comma",
             None),
            
            # Sentence ending with lowercase before capital (no punctuation)
            (r'[a-z]\s+[A-Z][a-z]{2,}',
             "Missing period: New sentence starts without end punctuation",
             None),
            
            # Statement ending with comma when period needed
            # Pattern: "statement, The next" (should be period)
            (r'\b(said|stated|reported|announced|declared|explained|mentioned|noted|observed|concluded),\s+[A-Z]',
             "Missing period: Complete statement should end with period, not comma",
             None),
            
            # Multiple complete thoughts without proper separation
            # Pattern: simple subject-verb-object repeated without punctuation
            (r'\b(I|you|he|she|it|we|they)\s+(am|is|are|was|were)\s+\w+\s+[A-Z]',
             "Missing period: Complete thought should end before starting new sentence",
             None),
            
            # Sentence fragment followed by another fragment (both need punctuation)
            (r'\b(The|A|An)\s+\w+\s+\w+\s+[A-Z]',
             "Missing punctuation: Check if period is needed between sentences",
             None),
            
            # Question or exclamation content with wrong ending punctuation
            (r'\b(who|what|when|where|why|how)\s+[\w\s]{5,}[,;]\s*$',
             "Missing question mark: Question should end with '?' not comma or semicolon",
             None),
            
            # Exclamatory content ending with period (should be exclamation mark)
            (r'\b(wow|amazing|incredible|terrible|awful|great)\s*\.\s*$',
             "Consider exclamation mark: Exclamatory content typically ends with '!' not period",
             None),
            
            # Abbreviation period missing
            (r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs)\s+[A-Z]',
             "Missing period: Abbreviations need periods (e.g., 'Mr.' not 'Mr')",
             lambda m, t: f"{m.group(1)}. "),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        """
        # High confidence patterns
        high_confidence = [0, 2, 7]  # Capital after comma, statement with said, abbreviations
        
        # Moderate-high confidence
        moderate_high = [1, 3, 5]  # Missing punctuation between sentences, questions
        
        # Moderate confidence
        moderate = [4, 6]  # Fragments, exclamations
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.85
        elif pattern_index in moderate:
            return 0.80
        else:
            return 0.85

