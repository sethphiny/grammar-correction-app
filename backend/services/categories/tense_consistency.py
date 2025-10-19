"""Tense Consistency category - Detects inappropriate tense shifts."""
from typing import List, Tuple
from .base_category import BaseCategory

class TenseConsistencyCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'tense_consistency'
    
    def get_display_name(self) -> str:
        return 'Tense Consistency'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r'\b(was|were)\s+\w+ing\s+.*\s+(is|are)\s+\w+ing\b',
             "Tense shift: Check if mixing past and present tense is intentional",
             None),
            (r'\b(walked|talked|ran|went|came|saw|did|made)\s+.*\s+(walk|talk|run|go|come|see|do|make)s?\b',
             "Tense shift: Mixing past and present tense in same context",
             None),
            (r'\b(will|would|shall)\s+\w+\s+.*\s+(was|were|had)\b',
             "Tense shift: Mixing future and past tense",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.75

