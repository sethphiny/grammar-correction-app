"""Grammar category - Detects common grammar errors."""
from typing import List, Tuple
from .base_category import BaseCategory

class GrammarCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'grammar'
    
    def get_display_name(self) -> str:
        return 'Grammar'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r"\b(don't|doesn't|didn't|won't|wouldn't|shouldn't|can't|couldn't)\s+(no|nothing|nobody|nowhere|never|none)\b", 
             "Double negative", 
             lambda m, t: m.group(1).replace("n't", "") + " any"),
            (r'\bshould\s+of\b', "Incorrect: 'should of' → 'should have'", lambda m, t: "should have"),
            (r'\bcould\s+of\b', "Incorrect: 'could of' → 'could have'", lambda m, t: "could have"),
            (r'\bwould\s+of\b', "Incorrect: 'would of' → 'would have'", lambda m, t: "would have"),
            (r'\bmust\s+of\b', "Incorrect: 'must of' → 'must have'", lambda m, t: "must have"),
            (r'\byour\s+(are|going|not|very|really)\b', "Incorrect: 'your' → 'you're'", lambda m, t: f"you're {m.group(1)}"),
            (r"\bits\s+(a|an|the|very|really|going|been)\b", "Incorrect: 'its' → 'it's'", lambda m, t: f"it's {m.group(1)}"),
            (r'\b(better|worse|more|less|greater|smaller)\s+then\b', "Incorrect: 'then' → 'than'", lambda m, t: f"{m.group(1)} than"),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.85

