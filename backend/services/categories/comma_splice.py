"""
Comma Splice category - Detects comma splices (improper joining of independent clauses with only a comma).

Note: Some patterns overlap with run_on category but this provides more specific comma splice detection.

Implements detection for:
- Classic comma splices (independent clause, independent clause)
- Comma splices with transitional adverbs
- Comma splices with pronouns
- Comma splices with conjunctive adverbs
- Common comma splice patterns
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class CommaSpliceCategory(BaseCategory):
    """
    Detects comma splice errors.
    
    Total patterns: 10
    Confidence: 0.80-0.90 depending on clarity
    """
    
    def get_category_name(self) -> str:
        return 'comma_splice'
    
    def get_display_name(self) -> str:
        return 'Comma Splice'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return comma splice detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Classic comma splice with pronouns
            # Pattern: "clause, I/you/he/she/it/we/they verb"
            (r',\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had|do|does|did|can|could|will|would|should|may|might|must|think|believe|know|see|feel|want|need)\b',
             "Comma splice: Two independent clauses joined with only a comma - add a conjunction, use a semicolon, or split into two sentences",
             None),
            
            # Comma splice with transitional adverbs
            # Pattern: ", however" ", therefore" ", moreover" etc.
            (r',\s+(however|therefore|moreover|furthermore|nevertheless|consequently|thus|hence|meanwhile|otherwise|instead|likewise|indeed|besides|accordingly)\s+',
             "Comma splice: Use semicolon before transitional words (e.g., '; however,' not ', however')",
             lambda m, t: f"; {m.group(1)} "),
            
            # Comma splice with "then"
            (r',\s+then\s+(I|you|he|she|it|we|they|the)\s+(am|is|are|was|were|have|has|had|went|came|did|said|saw)\b',
             "Comma splice with 'then': Start a new sentence or use a semicolon",
             None),
            
            # Comma splice with demonstrative pronouns
            # Pattern: "clause, this/that is"
            (r',\s+(this|that|these|those)\s+(is|was|are|were|will|would|can|could|should)\b',
             "Comma splice: Two independent clauses - use a semicolon or start a new sentence",
             None),
            
            # Comma splice with subject-verb-object pattern
            # Pattern: "S V O, S V" (very conservative)
            (r'\b(I|you|he|she|it|we|they)\s+(ate|ran|went|came|left|arrived|finished|started|began|ended)\s+[\w\s]{2,15},\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had|do|does|did)\b',
             "Comma splice: Independent clauses need more than a comma - add 'and', use a semicolon, or create two sentences",
             None),
            
            # Comma splice with "it" or "there" expletives
            # Pattern: ", it is" ", there is"
            (r',\s+(it|there)\s+(is|was|are|were|has|have|had)\b',
             "Comma splice: Use a semicolon or start a new sentence before expletive constructions",
             None),
            
            # Comma splice with possessive pronouns starting clause
            # Pattern: ", my/his/her/their/our/your X verb"
            (r',\s+(my|his|her|their|our|your)\s+\w+\s+(is|was|are|were|has|have|had)\b',
             "Comma splice: Independent clause after comma - use conjunction, semicolon, or new sentence",
             None),
            
            # Comma splice before "for example" or "for instance"
            (r',\s+(for\s+example|for\s+instance|in\s+fact|in\s+addition|in\s+other\s+words)\s*,',
             "Comma splice: Use semicolon before transitional phrases (e.g., '; for example,' not ', for example,')",
             None),
            
            # Comma splice with "still" or "also" as transition
            (r',\s+(still|also)\s+(I|you|he|she|it|we|they)\s+',
             "Comma splice: 'Still' and 'also' need stronger punctuation when joining clauses - use semicolon or new sentence",
             None),
            
            # Multiple short clauses with commas (serial comma splice)
            (r'\b(I|you|he|she|it|we|they)\s+\w+,\s+(I|you|he|she|it|we|they)\s+\w+,\s+(I|you|he|she|it|we|they)\s+\w+\b',
             "Multiple comma splices: Consider using conjunctions, semicolons, or separating into multiple sentences",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear comma splices (0.90),
        moderate for possible splices (0.80).
        """
        # High confidence patterns
        high_confidence = [1, 2, 7]  # Transitional words, "then", "for example"
        
        # Moderate-high confidence
        moderate_high = [0, 3, 5, 6, 8, 9]  # Clear independent clauses
        
        # Moderate confidence
        moderate = [4]  # S-V-O pattern (conservative)
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.85
        elif pattern_index in moderate:
            return 0.80
        else:
            return 0.85

