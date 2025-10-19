"""
Contrast category - Detects issues with contrastive expressions and contrast markers.

Implements detection for:
- Missing contrast markers when needed
- Incorrect contrast conjunctions
- Weak or vague contrast expressions
- Improper use of "but" vs "however"
- Missing parallel structure in contrasts
- Redundant contrast markers
- Incorrect punctuation with contrast words
- Misplaced contrast expressions
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class ContrastCategory(BaseCategory):
    """
    Detects contrast usage issues in sentences.
    
    Total patterns: 10
    Confidence: 0.70-0.85 depending on clarity of the issue
    """
    
    def get_category_name(self) -> str:
        return 'contrast'
    
    def get_display_name(self) -> str:
        return 'Contrast'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return contrast usage detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # "However" at start without proper punctuation from previous sentence
            # Pattern: However starting a sentence after a period (should be semicolon or new paragraph)
            (r'\.\s+However,\s+',
             "Contrast marker 'However': Consider using a semicolon before 'however' or starting a new paragraph for stronger contrast",
             None),
            
            # "But" starting a sentence (informal in academic/formal writing)
            (r'^\s*But\s+',
             "Informal contrast: Starting a sentence with 'But' is informal - consider 'However,' or 'Nevertheless,' in formal writing",
             None),
            
            # "Although" without contrast in second clause
            # This is a simplified check - just flags for review
            (r'\balthough\s+[\w\s]{10,40}\.\s*$',
             "Incomplete contrast: 'Although' suggests contrast but the contrasting point may be unclear or missing",
             None),
            
            # "While" used for contrast but could be ambiguous (time vs contrast)
            (r'\bwhile\s+[\w\s]{5,25},\s+[\w\s]{5,25}\b',
             "Ambiguous 'while': Check if 'while' means 'during' or 'whereas' - use 'whereas' for clearer contrast",
             None),
            
            # Weak contrast with "but" - could be stronger
            (r'\b(good|nice|okay|fine)\s+but\s+',
             "Weak contrast: Consider stronger contrast words like 'however,' 'nevertheless,' or 'yet' for more impact",
             None),
            
            # Double contrast markers (redundant)
            (r'\b(but|yet)\s+however\b',
             "Redundant contrast: Using both 'but/yet' and 'however' is redundant - choose one",
             None),
            
            # "On the other hand" without "on the one hand"
            (r'\bon\s+the\s+other\s+hand\b',
             "Incomplete contrast pair: 'On the other hand' typically pairs with 'On the one hand' earlier in the text",
             None),
            
            # "Despite" or "In spite of" followed by "but" (redundant)
            (r'\b(despite|in\s+spite\s+of)\s+[\w\s]{5,30},?\s+but\s+',
             "Redundant contrast: 'Despite/In spite of' already shows contrast - 'but' is unnecessary",
             None),
            
            # Missing comma after introductory contrast phrase
            (r'\b(however|nevertheless|nonetheless|furthermore|moreover|consequently|therefore)\s+[a-z]',
             "Punctuation: Contrast/transition words like 'however,' 'nevertheless,' etc. should be followed by a comma",
             None),
            
            # "Though" at the end without comma (informal/colloquial)
            (r',\s+though\s*\.\s*$',
             "Colloquial contrast: Using 'though' at the end is informal - consider 'although' or 'however' for formal writing",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear violations (0.85),
        moderate for style or context-dependent issues (0.70).
        """
        # High confidence patterns (clear violations)
        high_confidence = [5, 7, 8]  # Redundant contrast markers, punctuation issues
        
        # Moderate confidence patterns (style or context-dependent)
        moderate_confidence = [0, 1, 2, 3, 4, 6, 9]  # Stylistic preferences, ambiguous cases
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_confidence:
            return 0.70
        else:
            return 0.75

