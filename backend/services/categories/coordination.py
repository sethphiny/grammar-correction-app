"""
Coordination category - Detects issues with coordinating conjunctions and parallel structure.

Implements detection for:
- Missing commas before coordinating conjunctions (FANBOYS)
- Incorrect comma usage with coordinating conjunctions
- Coordinating conjunctions without parallel structure
- Starting sentences with coordinating conjunctions inappropriately
- Overuse of "and" in lists
- Missing conjunctions in lists
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class CoordinationCategory(BaseCategory):
    """
    Detects coordination conjunction issues.
    
    Total patterns: 10
    Confidence: 0.75-0.85 depending on clarity
    """
    
    def get_category_name(self) -> str:
        return 'coordination'
    
    def get_display_name(self) -> str:
        return 'Coordination'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return coordination detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Missing comma before coordinating conjunction with independent clauses
            # Pattern: independent clause + FANBOYS + independent clause (no comma)
            (r'\b(I|you|he|she|it|we|they|the\s+\w+)\s+(am|is|are|was|were|have|has|had|can|could|will|would)\s+[\w\s]{5,}\s+(and|but|or|yet|so)\s+(I|you|he|she|it|we|they|the\s+\w+)\s+(am|is|are|was|were|have|has|had|can|could|will|would)\b',
             "Missing comma: Add a comma before coordinating conjunction when joining independent clauses",
             None),
            
            # Comma before "and" in simple compound predicate (unnecessary)
            # Pattern: "Subject verb X, and verb Y" (comma not needed)
            (r'\b(I|you|he|she|it|we|they)\s+\w+\s+[\w\s]{2,10},\s+and\s+(am|is|are|was|were|have|has|had|do|does|did|can|could|will|would|should|may|might)\b',
             "Unnecessary comma: Don't use comma before 'and' in compound predicate (same subject)",
             None),
            
            # List without Oxford comma
            # Pattern: "X, Y and Z" (should be "X, Y, and Z")
            (r'\b\w+,\s+\w+\s+and\s+\w+\b',
             "Oxford comma: Consider adding comma before 'and' in lists for clarity (e.g., 'X, Y, and Z')",
             None),
            
            # Too many "and"s in a row (lacks variety)
            (r'\band\s+[\w\s]{2,15}\s+and\s+[\w\s]{2,15}\s+and\s+',
             "Repetitive coordination: Too many 'and's - consider varying with other conjunctions or restructuring",
             None),
            
            # "But" or "And" starting sentence (acceptable in modern style, but flag for formal writing)
            (r'^\s*(And|But|Or|So|Yet)\s+(?=[A-Z])',
             "Coordination at sentence start: Starting with 'And/But/Or/So/Yet' is acceptable in modern style but avoid in formal writing",
             None),
            
            # Coordinating conjunction without clear parallel structure
            # Pattern: "verb and noun" or "adjective and verb"
            (r'\b(is|am|are|was|were|have|has|had)\s+([\w]+ing|to\s+\w+)\s+(and|or|but)\s+([a-z]+(?<!ing))\b',
             "Coordination error: Check parallel structure - elements joined by 'and/or/but' should have the same grammatical form",
             None),
            
            # Missing "both" with "and" for emphasis
            # Pattern: "X and Y" when "both X and Y" would be clearer
            (r'\b(is|are|was|were|have|has)\s+(important|necessary|essential|required|needed)\s+and\s+',
             "Coordination: Consider 'both...and' for emphasis (e.g., 'both important and necessary')",
             None),
            
            # "Either" without "or" or vice versa
            (r'\beither\s+[\w\s]{3,30}\s+(and|but)(\s|,)',
             "Coordination error: 'Either' should pair with 'or', not 'and/but'",
             None),
            
            (r'\b(neither|nor)\s+[\w\s]{3,30}\s+(and|or|but)(\s|,)',
             "Coordination error: 'Neither' should pair with 'nor', not other conjunctions",
             None),
            
            # Missing parallel coordinating conjunction
            # Pattern: list without final conjunction
            (r'\b\w+,\s+\w+,\s+\w+\s+[^and|or]',
             "List coordination: Lists typically need 'and' or 'or' before the final item",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear errors (0.85),
        moderate for style preferences (0.75).
        """
        # High confidence patterns
        high_confidence = [1, 7, 8]  # Unnecessary comma, correlative conjunctions
        
        # Moderate-high confidence
        moderate_high = [0, 3, 5, 6, 9]  # Missing comma, too many "and"s, parallel structure
        
        # Moderate confidence (style-dependent)
        moderate = [2, 4]  # Oxford comma, sentence starters
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_high:
            return 0.80
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.80

