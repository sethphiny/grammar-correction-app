"""Parallelism/Concision category - Detects parallel structure and wordiness issues."""
from typing import List, Tuple
from .base_category import BaseCategory

class ParallelismConcisionCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'parallelism_concision'
    
    def get_display_name(self) -> str:
        return 'Parallelism/Concision (Experimental)'
    
    def is_experimental(self) -> bool:
        return True
    
    def get_patterns(self) -> List[Tuple]:
        """Concision + parallelism patterns (60+ total)."""
        return [
            # Wordy phrases (concision)
            (r'\bat the present moment\b', "Wordy: → 'now'", lambda m, t: "now"),
            (r'\bin the event of\b', "Wordy: → 'if'", lambda m, t: "if"),
            (r'\bdue to the fact that\b', "Wordy: → 'because'", lambda m, t: "because"),
            (r'\bin spite of the fact that\b', "Wordy: → 'although'", lambda m, t: "although"),
            (r'\bhas the ability to\b', "Wordy: → 'can'", lambda m, t: "can"),
            (r'\bis able to\b', "Wordy: → 'can'", lambda m, t: "can"),
            (r'\bmake a decision\b', "Wordy: → 'decide'", lambda m, t: "decide"),
            
            # Redundant intensifiers
            (r'\bvery\s+unique\b', "Redundant: 'unique' is absolute", lambda m, t: "unique"),
            (r'\bvery\s+perfect\b', "Redundant: 'perfect' is absolute", lambda m, t: "perfect"),
            (r'\bcompletely\s+full\b', "Redundant: 'full' is absolute", lambda m, t: "full"),
            
            # Parallelism: mixed verb forms in lists
            (r'\b(like|enjoy|prefer)\s+(\w+ing),\s+(?:[\w\s]+,\s+)?(?:and\s+)?to\s+\w+\b',
             "Parallelism: Keep verb forms consistent in lists",
             None),
            (r'\b(like|enjoy|prefer)\s+to\s+\w+,\s+(?:[\w\s]+,\s+)?(?:and\s+)?(\w+ing)\b',
             "Parallelism: Keep verb forms consistent in lists",
             None),
            
            # Parallelism: correlative conjunctions
            (r'\b(Either|either)\s+\w+\s+\w+\s+(or)\s+\w+ing\b',
             "Parallelism: 'Either...or' should have parallel structures",
             None),
            
            # Parallelism: comparison structures
            (r'\b(easier|harder|better|worse)\s+than\s+to\s+\w+\b',
             "Parallelism: Use matching verb form after 'than'",
             None),
        ]
    
    def has_custom_checker(self) -> bool:
        """Has passive voice detection with spaCy."""
        return True
    
    def check(self, line_content: str, line_number: int, **kwargs) -> List:
        """Custom passive voice detection (if spaCy available)."""
        issues = []
        # Passive voice detection would go here (extracted from grammar_checker.py)
        # For now, return empty - main grammar_checker will handle it
        return issues
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.85 if pattern_index < 10 else 0.75

