"""
Run-on Sentences category - Detects improperly joined independent clauses.

Implements detection for:
- Comma splices (two independent clauses joined with only a comma)
- Comma splices with transitional words (however, therefore, etc.)
- Missing commas before coordinating conjunctions
- Fused sentences (no punctuation between clauses)
- Multiple conjunctions without proper punctuation
- Comma splices with "then"
- Very long compound sentences
- "So" used as conjunction without comma
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class RunOnCategory(BaseCategory):
    """
    Detects run-on sentences and comma splices.
    
    Total patterns: 8
    Confidence: 0.78 for clear comma splices, 0.70 for possible run-ons
    """
    
    def get_category_name(self) -> str:
        return 'run_on'
    
    def get_display_name(self) -> str:
        return 'Run-on Sentences'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return run-on sentence detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Comma splice: Independent clause + comma + independent clause (no conjunction)
            # Pattern: pronoun/noun + verb, pronoun/noun + verb
            # Very conservative to avoid false positives with dependent clauses
            (r'\b(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had|do|does|did|can|could|will|would|should|may|might|must)\s+[\w\s]+,\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had|do|does|did|can|could|will|would|should|may|might|must)\b',
             "Possible comma splice: Two independent clauses joined with only a comma - add a conjunction or use a semicolon",
             None),
            
            # Comma splice with common transition words (however, therefore, moreover, etc.)
            # Pattern: "clause, however clause" (should be "; however," or ". However,")
            (r',\s+(however|therefore|moreover|furthermore|nevertheless|consequently|thus|hence|meanwhile|otherwise|instead|likewise|indeed)\s+',
             "Comma splice: Use a semicolon before transitional words like 'however', 'therefore', etc., or start a new sentence",
             lambda m, t: f"; {m.group(1)} "),  # Auto-fix: change comma to semicolon
            
            # Run-on with coordinating conjunction but no comma
            # Pattern: independent clause [FANBOYS] independent clause (missing comma before conjunction)
            # Conservative: only flag if both sides have clear subject-verb
            (r'\b(I|you|he|she|it|we|they|the\s+\w+|this|that)\s+(am|is|are|was|were|have|has|had|can|could|will|would)\s+[\w\s]{5,}\s+(and|but|or|so|yet)\s+(I|you|he|she|it|we|they|the\s+\w+|this|that)\s+(am|is|are|was|were|have|has|had|can|could|will|would)\b',
             "Run-on sentence: Add a comma before coordinating conjunctions (and, but, or, so, yet) when joining independent clauses",
             None),
            
            # Fused sentence indicators: Two complete thoughts with no punctuation
            # Pattern: statement ending with noun/pronoun, then pronoun starts next clause
            (r'\b(it|this|that|he|she|they|we)\s+(is|was|are|were|has|have|had)\s+[\w\s]{8,}\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|think|believe|know|see|feel|want|need|can|should|will|would)\b',
             "Possible run-on: Two independent clauses may need proper punctuation or conjunction between them",
             None),
            
            # Multiple "and" conjunctions without commas (compound run-on)
            # Pattern: clause and clause and clause (no commas)
            (r'\b\w+\s+and\s+\w+\s+and\s+\w+\s+and\s+',
             "Possible run-on: Multiple 'and' conjunctions - consider using commas or breaking into separate sentences",
             None),
            
            # Comma splice with "then" (common error)
            # Pattern: "clause, then clause" (should be a new sentence or semicolon)
            (r',\s+then\s+(I|you|he|she|it|we|they|the\s+\w+)\s+(am|is|are|was|were|have|has|had|do|does|did|can|could|will|would|went|came|said|saw)\b',
             "Comma splice: 'Then' should typically start a new sentence or follow a semicolon",
             None),
            
            # Very long sentence without proper punctuation (likely run-on)
            # Conservative: only flag sentences with 40+ words and no internal punctuation
            (r'^[^,.;!?]{200,}\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had)\s+[^.!?]{50,}\.$',
             "Possible run-on: Very long sentence with multiple clauses - consider breaking into shorter sentences",
             None),
            
            # Comma splice before "so" (common error - needs comma before "so" when it's a conjunction)
            # But this checks for missing the comma
            (r'\b[\w\s]{10,}\s+so\s+(I|you|he|she|it|we|they|the\s+\w+)\s+(am|is|are|was|were|can|could|will|would|have|has|had)\b',
             "Check if 'so' is joining independent clauses - if so, add a comma before it",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear comma splices (0.78),
        lower for possible run-ons (0.70).
        """
        # Patterns 1, 5 are clear comma splices
        if pattern_index in [1, 5]:
            return 0.78
        else:
            return 0.70
    
    def get_description(self) -> str:
        return "Detects run-on sentences and comma splices"

