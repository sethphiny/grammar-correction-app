"""Punctuation category - Detects punctuation errors."""
from typing import List, Tuple
from .base_category import BaseCategory

class PunctuationCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'punctuation'
    
    def get_display_name(self) -> str:
        return 'Punctuation'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r'\s{2,}', 'Multiple consecutive spaces', lambda m, t: ' '),
            (r'\s+([,;:!?])', 'Extra space before punctuation', lambda m, t: m.group(1)),
            (r'([,;:!?])([a-zA-Z])', 'Missing space after punctuation', lambda m, t: f"{m.group(1)} {m.group(2)}"),
            (r'([,;:]){2,}', 'Multiple punctuation marks', lambda m, t: m.group(1)),
            (r'([\(\[\{])\s+', 'Extra space after opening bracket', lambda m, t: m.group(1)),
            (r'\s+([\)\]\}])', 'Extra space before closing bracket', lambda m, t: m.group(1)),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.90

