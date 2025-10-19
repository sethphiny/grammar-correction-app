"""
Ambiguous Pronouns category - Detects unclear pronoun references.
"""

from typing import List, Tuple
from .base_category import BaseCategory


class AmbiguousPronounsCategory(BaseCategory):
    """Pronoun reference clarity (7 patterns)."""
    
    def get_category_name(self) -> str:
        return 'ambiguous_pronouns'
    
    def get_display_name(self) -> str:
        return 'Ambiguous Pronouns'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            # Vague "it" at sentence start
            (r'^(It|it)\s+(seems|appears|looks|sounds|feels)\s+(like|that|as if)\b',
             "Vague pronoun: 'It' may be unclear - consider specifying what 'it' refers to",
             None),
            
            # Multiple "it" pronouns
            (r'\bit\b.*\bit\b.*\bit\b',
             "Pronoun clarity: Multiple uses of 'it' in one sentence may cause confusion",
             None),
            
            # "This/That" at start without noun
            (r'^(This|this|That|that)\s+(is|was|would|could|should|may|might|can|will)\b',
             "Vague pronoun: Consider adding a noun after 'this/that' for clarity",
             None),
            
            # "These/Those" used vaguely
            (r'^(These|these|Those|those)\s+(are|were|would|could|should|may|might|can|will)\b',
             "Vague pronoun: Consider adding a noun after 'these/those' for clarity",
             None),
            
            # "They" without clear antecedent
            (r'^(They|they)\s+(say|said|think|thought|believe|believed|claim|claimed)\b',
             "Ambiguous pronoun: Who does 'they' refer to? Consider being more specific",
             None),
            
            # Multiple "one" uses
            (r'\bone\b.*\bone\b.*\bone\b',
             "Pronoun clarity: Multiple uses of 'one' may be confusing",
             None),
            
            # Unclear "which"
            (r'\b(and|or)\s+(\w+\s+)*\w+,\s*which\b',
             "Pronoun clarity: 'Which' may be ambiguous after multiple nouns",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.75

