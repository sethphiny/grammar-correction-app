"""
Broken Quote category - Detects unmatched quotes and quote errors.

Implements detection for:
- Unmatched opening quotes
- Unmatched closing quotes
- Mixing quote styles (" and ')
- Nested quote errors
- Quote direction errors (smart quotes)
- Missing quotes around dialogue
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class BrokenQuoteCategory(BaseCategory):
    """
    Detects unmatched and broken quotation marks.
    
    Total patterns: 8
    Confidence: 0.80-0.90
    """
    
    def get_category_name(self) -> str:
        return 'broken_quote'
    
    def get_display_name(self) -> str:
        return 'Broken Quote'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return broken quote detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Opening quote without closing (basic check)
            (r'"[^"]{50,}$',
             "Unmatched quote: Opening quote without closing quote - check if quote is properly closed",
             None),
            
            # Mixing single and double quotes for same purpose
            (r'"[^"]*\'[^\']*"',
             "Mixed quotes: Use consistent quote style (either \" \" or ' ') throughout",
             None),
            
            # Multiple opening quotes without corresponding closing
            (r'""[^"]',
             "Quote error: Two opening quotes - remove duplicate or add closing quote",
             None),
            
            # Quote after quote without space or punctuation
            (r'""\s*"',
             "Quote formatting: Check quote placement - may need punctuation or space between quotes",
             None),
            
            # Dialogue without quotes
            # Pattern: "he said X" where X looks like dialogue but has no quotes
            (r'\b(he|she|I|they|we)\s+(said|asked|replied|whispered|shouted),\s+[A-Z][a-z]+\s+',
             "Missing quotes: Dialogue after 'said/asked' should be in quotation marks",
             None),
            
            # Quote around single word (often unnecessary except for specific terms)
            (r'"\w+"',
             "Quote usage: Check if quotes around single word are necessary (use for emphasis or specific terms only)",
             None),
            
            # Smart quotes mixed with straight quotes
            (r'[""'']\s*[\"\']',
             "Quote inconsistency: Mixing smart quotes and straight quotes - be consistent",
             None),
            
            # Nested quote errors (single inside double)
            (r'"[^"]*"[^"]*"[^"]*"',
             "Nested quotes: For quotes within quotes, use single quotes inside double quotes",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        """
        # High confidence patterns
        high_confidence = [2, 3]  # Duplicate quotes, formatting errors
        
        # Moderate-high confidence
        moderate_high = [0, 4, 6]  # Unmatched quotes, missing quotes, smart/straight mixing
        
        # Moderate confidence
        moderate = [1, 5, 7]  # Mixed styles, single word quotes, nested quotes
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.85
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.80

