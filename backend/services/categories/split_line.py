"""
Split Line / Broken Dialogue category - Detects improperly split dialogue and line breaks.

Implements detection for:
- Dialogue split across lines incorrectly
- Unclosed quotation marks at line end
- Dialogue interrupted mid-sentence without proper formatting
- Missing closing quotes before attribution
- Inconsistent dialogue formatting
- Broken dialogue tags
- Split attributions
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class SplitLineCategory(BaseCategory):
    """
    Detects split lines and broken dialogue formatting issues.
    
    Total patterns: 10
    Confidence: 0.75-0.85 depending on clarity of the issue
    """
    
    def get_category_name(self) -> str:
        return 'split_line'
    
    def get_display_name(self) -> str:
        return 'Split Line / Broken Dialogue'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return split line and broken dialogue detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Unclosed quotes at end of line (missing closing quote)
            # Pattern: Opening quote but no closing quote before end of line
            (r'"[^"]{10,}$',
             "Possible unclosed quotation: Line starts with quote but doesn't close it - check if dialogue continues or quote is missing",
             None),
            
            # Dialogue tag split incorrectly (comma inside quote when attribution follows)
            # Pattern: "dialogue," she said (correct) vs "dialogue" she said (incorrect)
            (r'"[^"]+"\s+(he|she|I|they|we|you|it|[A-Z]\w+)\s+(said|asked|replied|answered|shouted|whispered|muttered|exclaimed|continued|added)\b',
             "Broken dialogue: Missing comma before closing quote when dialogue tag follows",
             None),
            
            # Split dialogue without em-dash or proper continuation marker
            # Pattern: "Text that seems incomplete (no end punctuation before quote closes)
            (r'"[^"]{15,}[^.!?,]"\s*$',
             "Possible split dialogue: Dialogue ends without punctuation - may need em-dash (—) if interrupted or continuation marker",
             None),
            
            # Dialogue starting mid-line without proper setup
            # Pattern: Text before quote without attribution or action beat
            (r'[a-z]{10,}\s+"[A-Z]',
             "Possible split dialogue: Quote appears mid-line - check if dialogue tag or action beat is needed",
             None),
            
            # Multiple dialogue snippets on same line without proper separation
            # Pattern: "text" "text" (missing separator or attribution)
            (r'"\s+"\s*[A-Z]',
             "Split dialogue: Multiple dialogue snippets on same line - separate with attribution or new line",
             None),
            
            # Interrupted dialogue without em-dash
            # Pattern: "Text that cuts off" without proper punctuation
            (r'"[^"]{10,}[a-z]\s+[a-z]+"',
             "Interrupted dialogue: May need em-dash (—) to indicate interruption or trail-off",
             None),
            
            # Dialogue continuation without lowercase start
            # Pattern: Second part of split dialogue starts with capital when it shouldn't
            (r'\.\s+"[A-Z][^"]+"\s+(he|she|I|they|we|it)\s+(said|continued)',
             "Dialogue continuation: If continuing same sentence after action, second part should start lowercase",
             None),
            
            # Missing quote marks on continued dialogue
            # Pattern: Line ends with comma/period inside quote, next line has speech but no opening quote
            (r'[.,!?]"\s*\n\s*[A-Z][a-z]{4,}\s+',
             "Possible missing opening quote: Previous line closed dialogue, but this line seems to continue without opening quote",
             None),
            
            # Attribution split across lines incorrectly
            # Pattern: "Dialogue" \n he said (should be same line)
            (r'"\s*$\n^\s*(he|she|I|they|we|you|it|[A-Z]\w+)\s+(said|asked|replied)',
             "Split attribution: Dialogue tag should be on same line as closing quote",
             None),
            
            # Dialogue without closing punctuation before quote closes
            # Pattern: "dialogue without punctuation" (should have comma, period, etc.)
            (r'"[A-Z][^"]{15,}[a-z]"\s+(he|she|I|they|we|you|it|[A-Z]\w+)\s+(said|asked|replied|whispered|shouted)',
             "Broken dialogue: Dialogue should end with punctuation (comma, period, question mark, or exclamation) before closing quote",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear formatting errors (0.85),
        moderate for possible issues (0.75).
        """
        # High confidence patterns (clear violations)
        high_confidence = [1, 4, 9]  # Missing comma in tag, multiple snippets, missing punctuation
        
        # Moderate confidence patterns (may have exceptions)
        moderate_confidence = [0, 2, 3, 5, 6, 7, 8]  # Unclosed quotes, splits, interruptions
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_confidence:
            return 0.75
        else:
            return 0.80

