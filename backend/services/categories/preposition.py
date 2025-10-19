"""
Preposition / Diction category - Detects preposition usage errors and word choice issues.

Implements detection for:
- Incorrect prepositions with time expressions
- Incorrect prepositions with place expressions
- Common preposition errors (different from/than, etc.)
- Affect vs Effect usage
- Common word confusions
- Preposition redundancy
- Incorrect preposition pairs
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class PrepositionCategory(BaseCategory):
    """
    Detects preposition usage errors and diction issues.
    
    Total patterns: 18
    Confidence: 0.75-0.90 depending on the issue
    """
    
    def get_category_name(self) -> str:
        return 'preposition'
    
    def get_display_name(self) -> str:
        return 'Preposition / Diction'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return preposition/diction detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Time prepositions
            (r'\bin\s+the\s+morning\b',
             "Time preposition: Use 'in the morning' (correct as is - no change needed)",
             None),
            
            (r'\bin\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
             "Time preposition: Use 'on' with days of the week (e.g., 'on Monday')",
             lambda m, t: f"on {m.group(1)}"),
            
            (r'\bat\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',
             "Time preposition: Use 'in' with months (e.g., 'in January')",
             lambda m, t: f"in {m.group(1)}"),
            
            (r'\bin\s+night\b',
             "Time preposition: Use 'at night' (not 'in night')",
             lambda m, t: "at night"),
            
            # Place prepositions
            (r'\bin\s+home\b',
             "Place preposition: Use 'at home' when referring to being at one's residence",
             lambda m, t: "at home"),
            
            (r'\bat\s+the\s+corner\b',
             "Place preposition: Use 'on the corner' for street corners",
             lambda m, t: "on the corner"),
            
            # Different from/than
            (r'\bdifferent\s+than\b',
             "Preposition: In formal writing, use 'different from' (though 'different than' is acceptable in American English)",
             lambda m, t: "different from"),
            
            # Affect vs Effect
            (r'\baffect\s+on\b',
             "Word confusion: 'Affect' is a verb; use 'effect on' (noun) or 'affect' without 'on'",
             None),
            
            (r'\bthe\s+affect\s+of\b',
             "Word confusion: Use 'effect' (noun) not 'affect' - 'the effect of'",
             lambda m, t: "the effect of"),
            
            # Preposition redundancy
            (r'\boff\s+of\b',
             "Redundant preposition: Use 'off' not 'off of'",
             lambda m, t: "off"),
            
            (r'\binside\s+of\b',
             "Redundant preposition: Use 'inside' not 'inside of'",
             lambda m, t: "inside"),
            
            (r'\boutside\s+of\b',
             "Redundant preposition: Use 'outside' not 'outside of' (unless meaning 'except for')",
             lambda m, t: "outside"),
            
            # Common errors
            (r'\binterested\s+on\b',
             "Preposition error: Use 'interested in' not 'interested on'",
             lambda m, t: "interested in"),
            
            (r'\bdepend\s+of\b',
             "Preposition error: Use 'depend on' not 'depend of'",
             lambda m, t: "depend on"),
            
            (r'\bconsist\s+from\b',
             "Preposition error: Use 'consist of' not 'consist from'",
             lambda m, t: "consist of"),
            
            # Common diction errors
            (r'\bcould\s+of\b',
             "Diction error: Use 'could have' (or 'could've') not 'could of'",
             lambda m, t: "could have"),
            
            (r'\bshould\s+of\b',
             "Diction error: Use 'should have' (or 'should've') not 'should of'",
             lambda m, t: "should have"),
            
            (r'\bwould\s+of\b',
             "Diction error: Use 'would have' (or 'would've') not 'would of'",
             lambda m, t: "would have"),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear errors (0.90),
        moderate for style preferences (0.75).
        """
        # High confidence patterns (clear errors)
        high_confidence = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # Clear preposition errors
        
        # Moderate confidence patterns (style or regional differences)
        moderate_confidence = [0, 6, 7]  # Style preferences
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_confidence:
            return 0.75
        else:
            return 0.85

