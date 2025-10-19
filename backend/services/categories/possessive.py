"""
Possessive category - Detects possessive form errors.

Implements detection for:
- Missing apostrophes in possessives
- Incorrect apostrophe placement (its vs it's, your vs you're)
- Plural possessive errors
- Possessive with inanimate objects (sometimes awkward)
- Double possessives
- Possessive pronoun errors
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class PossessiveCategory(BaseCategory):
    """
    Detects possessive form errors.
    
    Total patterns: 12
    Confidence: 0.85-0.95
    """
    
    def get_category_name(self) -> str:
        return 'possessive'
    
    def get_display_name(self) -> str:
        return 'Possessive'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return possessive detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # It's vs its confusion
            (r"\bits\s+(a|the|an|very|really|quite)\b",
             "Possessive error: Use 'its' (possessive) not 'it's' (it is) before nouns/adjectives",
             None),
            
            (r"\bit's\s+(own|purpose|meaning|value|place|role|function)\b",
             "Possessive error: Use 'its' (possessive) not 'it's' (it is) - 'it's' means 'it is'",
             lambda m, t: f"its {m.group(1)}"),
            
            # Your vs you're confusion
            (r"\byou're\s+(own|book|car|house|idea|plan|job|work|name|life|family|friend)\b",
             "Possessive error: Use 'your' (possessive) not 'you're' (you are)",
             lambda m, t: f"your {m.group(1)}"),
            
            (r"\byour\s+(going|coming|doing|being|having|making|taking)\b",
             "Possessive error: Use 'you're' (you are) not 'your' (possessive) before verbs",
             lambda m, t: f"you're {m.group(1)}"),
            
            # Their vs they're vs there
            (r"\bthey're\s+(book|car|house|idea|plan|job|work|name|life|family|friend)\b",
             "Possessive error: Use 'their' (possessive) not 'they're' (they are)",
             lambda m, t: f"their {m.group(1)}"),
            
            (r"\btheir\s+(going|coming|doing|being|having|making|taking)\b",
             "Possessive error: Use 'they're' (they are) not 'their' (possessive) before verbs",
             lambda m, t: f"they're {m.group(1)}"),
            
            # Whose vs who's
            (r"\bwho's\s+(book|car|house|idea|plan|job)\b",
             "Possessive error: Use 'whose' (possessive) not 'who's' (who is)",
             lambda m, t: f"whose {m.group(1)}"),
            
            # Plural possessive errors
            # Pattern: "the boys book" should be "the boys' book" or "the boy's book"
            (r"\b(boys|girls|dogs|cats|students|teachers|workers|players|kids|children)'\s+(?![s])",
             "Possessive error: Check plural possessive - should be -s' or -'s depending on singular/plural",
             None),
            
            # Possessive with inanimate objects (sometimes better as "of")
            # Pattern: "the book's cover" vs "the cover of the book"
            (r"\b(book|table|chair|wall|door|window|building|house|car)'s\s+(cover|top|side|edge|corner|surface)\b",
             "Style advisory: With inanimate objects, consider 'of' construction (e.g., 'the cover of the book')",
             None),
            
            # Double possessive (sometimes redundant)
            (r"\bof\s+(my|your|his|her|its|our|their)\s+\w+'s\b",
             "Double possessive: Check if both 'of' and possessive -'s are needed",
             None),
            
            # Wrong possessive pronoun form
            (r"\b(her|him|them|us)('s)\s+(book|car|house|idea)\b",
             "Possessive error: Use possessive pronouns (his, her, their) not object pronouns with 's",
             None),
            
            # Plural words with apostrophe that aren't possessive (common error)
            (r"\b(\w+)'s\s+(are|were|have|do|can|will)\b",
             "Apostrophe error: Plural nouns don't need apostrophes unless showing possession",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        """
        # High confidence patterns
        high_confidence = [1, 2, 4, 6, 10, 11]  # Clear its/it's, your/you're, their/they're, whose/who's errors
        
        # Moderate-high confidence
        moderate_high = [0, 3, 5, 7]  # Common confusions
        
        # Moderate confidence (style-dependent)
        moderate = [8, 9]  # Inanimate possessives, double possessives
        
        if pattern_index in high_confidence:
            return 0.95
        elif pattern_index in moderate_high:
            return 0.90
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.85

