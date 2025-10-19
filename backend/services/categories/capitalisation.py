"""Capitalisation category - Detects capitalization errors."""
from typing import List, Tuple
from .base_category import BaseCategory

class CapitalisationCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'capitalisation'
    
    def get_display_name(self) -> str:
        return 'Capitalisation'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r'(?<!\.)([.!?])\s+(?!https?://|www\.)([a-z])',
             "Sentence should start with a capital letter",
             lambda m, t: f'{m.group(1)} {m.group(2).upper()}'),
            (r'^(?!https?://|www\.)([a-z])',
             "Text should start with a capital letter",
             lambda m, t: m.group(1).upper()),
            (r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
             "Days of the week should be capitalized",
             lambda m, t: m.group(1).capitalize()),
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
             "Months should be capitalized",
             lambda m, t: m.group(1).capitalize()),
            (r'\bi\s+(am|was|have|had|do|did|can|could|will|would|should)\b',
             "Pronoun 'I' should be capitalized",
             lambda m, t: f"I {m.group(1)}"),
            (r'\bi\'(m|ve|d|ll)\b',
             "Pronoun 'I' in contractions should be capitalized",
             lambda m, t: f"I'{m.group(1)}"),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.90

