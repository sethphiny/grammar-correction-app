"""
Number Style category - Detects inconsistent number formatting and style issues.

Implements detection for:
- Numbers that should be spelled out (one-ten in text)
- Inconsistent number formatting (mixing digits and words)
- Starting sentences with digits
- Large numbers without commas
- Mixing ordinals and cardinals
- Inconsistent date formatting
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class NumberStyleCategory(BaseCategory):
    """
    Detects number style and formatting issues.
    
    Total patterns: 10
    Confidence: 0.70-0.85
    """
    
    def get_category_name(self) -> str:
        return 'number_style'
    
    def get_display_name(self) -> str:
        return 'Number Style'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return number style detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Starting sentence with digit (should spell out)
            (r'^\s*\d+\s+[a-z]',
             "Number style: Spell out numbers at sentence start (e.g., 'Twelve' not '12')",
             None),
            
            # Small numbers (1-10) in text (style preference to spell out)
            (r'\b(\d)\s+(people|things|items|cats|dogs|children|books|cars|houses|students|reasons|ways|times)\b',
             "Number style: Consider spelling out small numbers one through ten in text",
             None),
            
            # Large numbers without commas (1000+)
            (r'\b(\d{4,})\b',
             "Number formatting: Add commas to large numbers for readability (e.g., '1,000' not '1000')",
             None),
            
            # Inconsistent number style in same sentence
            # Pattern: mixing "5" and "ten" in same sentence
            (r'\b(\d+)\s+[\w\s]{1,15}\s+(one|two|three|four|five|six|seven|eight|nine|ten)\b',
             "Inconsistent number style: Use either all digits or all words, not mixed",
             None),
            
            # Percentages without %  symbol or spelled incorrectly
            (r'\b(\d+)\s+percent\b',
             "Number style: Use '%' symbol (e.g., '50%' not '50 percent') or spell as 'per cent'",
             lambda m, t: f"{m.group(1)}%"),
            
            # Ordinal numbers (1st, 2nd) in formal writing
            (r'\b(\d+)(st|nd|rd|th)\b',
             "Number style: In formal writing, spell out ordinal numbers (e.g., 'first' not '1st')",
             None),
            
            # Money without decimal (informal)
            # Pattern: "$100" when should be "$100.00" in formal contexts
            (r'\$(\d+)\s',
             "Number style: In formal writing, include decimals for currency (e.g., '$100.00' not '$100')",
             None),
            
            # Decimal numbers starting with period (missing zero)
            (r'\s(\.\d+)\b',
             "Number format: Add leading zero to decimals (e.g., '0.5' not '.5')",
             lambda m, t: f" 0{m.group(1)}"),
            
            # Roman numerals in modern text (style advisory)
            (r'\b([IVXLCDM]{2,})\b',
             "Number style: Consider using Arabic numerals instead of Roman numerals for clarity",
             None),
            
            # Time format inconsistency
            (r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)\b',
             "Time format: Be consistent with time formatting (e.g., all lowercase or all uppercase for am/pm)",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        """
        # High confidence patterns
        high_confidence = [0, 2, 4, 7]  # Sentence start, large numbers, percent, leading zero
        
        # Moderate-high confidence
        moderate_high = [3, 5, 6]  # Inconsistency, ordinals, money
        
        # Moderate confidence (style-dependent)
        moderate = [1, 8, 9]  # Small numbers, Roman numerals, time format
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_high:
            return 0.80
        elif pattern_index in moderate:
            return 0.70
        else:
            return 0.75

