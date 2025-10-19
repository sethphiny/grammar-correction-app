"""
Ellipsis category - Detects improper ellipsis usage.

Implements detection for:
- Four dots instead of three
- Ellipsis without proper spacing
- Ellipsis at sentence start (often informal)
- Multiple ellipses in succession
- Ellipsis without proper punctuation context
- Two-dot or one-dot ellipsis (incorrect)
- Ellipsis in formal writing (overuse)
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class EllipsisCategory(BaseCategory):
    """
    Detects ellipsis usage issues.
    
    Total patterns: 8
    Confidence: 0.75-0.90 depending on the violation
    """
    
    def get_category_name(self) -> str:
        return 'ellipsis'
    
    def get_display_name(self) -> str:
        return 'Ellipsis'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return ellipsis detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Four or more dots (should be three or three with period)
            (r'\.{4,}',
             "Ellipsis error: Use three dots (...) or four dots with period (....)",
             lambda m, t: "..."),
            
            # Two dots (incorrect)
            (r'(?<![.])\.\.\s',
             "Ellipsis error: Use three dots (...) not two",
             lambda m, t: "... "),
            
            # Ellipsis without spaces (style issue)
            (r'\w\.\.\.[\w]',
             "Ellipsis spacing: Add space before and after ellipsis for readability",
             None),
            
            # Ellipsis at sentence start (often informal)
            (r'^\s*\.{3}\s*[A-Z]',
             "Informal ellipsis: Starting sentence with ellipsis is informal - avoid in formal writing",
             None),
            
            # Multiple ellipses in close proximity (overuse)
            (r'\.{3}[\w\s]{1,20}\.{3}',
             "Ellipsis overuse: Multiple ellipses in close proximity - use sparingly for maximum effect",
             None),
            
            # Ellipsis followed immediately by comma or period (redundant)
            (r'\.{3}[,.]',
             "Ellipsis punctuation: Ellipsis already indicates omission - additional punctuation is redundant",
             lambda m, t: "..."),
            
            # Ellipsis in formal academic writing (advisory)
            (r'\.{3}',
             "Style advisory: Ellipses are informal - use sparingly in academic/formal writing",
             None),
            
            # Space between dots in ellipsis (incorrect)
            (r'\.\s+\.\s+\.',
             "Ellipsis format: Dots should be together without spaces (... not . . .)",
             lambda m, t: "..."),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear errors (0.90),
        moderate for style issues (0.75).
        """
        # High confidence patterns (clear errors)
        high_confidence = [0, 1, 5, 7]  # Four dots, two dots, redundant punctuation, spaced dots
        
        # Moderate-high confidence
        moderate_high = [2, 4]  # Spacing, overuse
        
        # Moderate confidence (style-dependent)
        moderate = [3, 6]  # Informal usage, style advisory
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.80
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.85

