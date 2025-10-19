"""
Hyphenation category - Detects hyphenation issues.

Implements detection for:
- Missing hyphens in compound adjectives before nouns
- Unnecessary hyphens in compound adjectives after nouns  
- Missing hyphens in compound numbers (twenty-one to ninety-nine)
- Hyphenation with adverbs ending in -ly (never hyphenated)
- Missing hyphens in fractions
- Suspended hyphenation errors
- Prefix hyphenation rules (re-, pre-, non-, anti-, etc.)
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class HyphenationCategory(BaseCategory):
    """
    Detects hyphenation issues.
    
    Total patterns: 10
    Confidence: 0.75-0.90 depending on clarity
    """
    
    def get_category_name(self) -> str:
        return 'hyphenation'
    
    def get_display_name(self) -> str:
        return 'Hyphenation'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return hyphenation detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Compound adjectives before noun (should be hyphenated)
            # Pattern: "well known person" should be "well-known person"
            (r'\b(well|long|short|high|low|fast|slow|hard|soft|full|half|self|all|ever)\s+(known|term|range|time|level|based|acting|made|scale|grown|employed)\s+(person|man|woman|thing|item|object|factor|element)\b',
             "Missing hyphen: Compound adjectives before nouns should be hyphenated (e.g., 'well-known person')",
             None),
            
            # Adverbs ending in -ly with adjectives (never hyphenated)
            (r'\b(highly|really|very|extremely|particularly|especially|completely|totally|fully|barely|hardly|nearly|merely)-(\w+)\b',
             "Unnecessary hyphen: Don't hyphenate adverbs ending in -ly with adjectives",
             lambda m, t: f"{m.group(1)} {m.group(2)}"),
            
            # Compound numbers twenty-one to ninety-nine (should be hyphenated)
            (r'\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\s+(one|two|three|four|five|six|seven|eight|nine)\b',
             "Missing hyphen: Compound numbers from twenty-one to ninety-nine should be hyphenated",
             None),
            
            # Fractions used as adjectives (should be hyphenated)
            # Pattern: "one half cup" should be "one-half cup"
            (r'\b(one|two|three|four|five|six|seven|eight|nine)\s+(half|third|quarter|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+(cup|inch|mile|pound|ounce|tablespoon|teaspoon)\b',
             "Missing hyphen: Fractional adjectives should be hyphenated (e.g., 'one-half cup')",
             None),
            
            # Prefix rules - some prefixes should have hyphens
            # Pattern: "re-election" but "reevaluate" (depends on vowel collision)
            (r'\b(re|pre|co|anti|non)(e|a|i|o|u)',
             "Hyphenation check: When prefix ends with vowel and root starts with vowel, consider hyphen (e.g., 're-enter', 'co-operate')",
             None),
            
            # "Self" prefix (always hyphenated)
            (r'\bself(confident|aware|esteem|control|sufficient|employed|made|taught|help|defense|service)\b',
             "Missing hyphen: 'Self' compounds are always hyphenated (e.g., 'self-confident')",
             lambda m, t: f"self-{m.group(1)}"),
            
            # "Ex" prefix meaning "former" (always hyphenated)
            (r'\bex(president|minister|husband|wife|boyfriend|girlfriend|partner|employee|student)\b',
             "Missing hyphen: 'Ex' meaning 'former' is always hyphenated (e.g., 'ex-president')",
             lambda m, t: f"ex-{m.group(1)}"),
            
            # Age expressions (should be hyphenated when used as adjective)
            # Pattern: "five year old" should be "five-year-old" when before noun
            (r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+year\s+old\s+(boy|girl|child|man|woman|person)\b',
             "Missing hyphens: Age expressions used as adjectives should be fully hyphenated (e.g., 'five-year-old boy')",
             None),
            
            # Compound adjectives with numbers
            # Pattern: "20 story building" should be "20-story building"
            (r'\b(\d+)\s+(story|page|hour|minute|mile|year|day|week|month|dollar|foot|inch)\s+(building|book|drive|journey|old|plan|house)\b',
             "Missing hyphen: Number + noun acting as adjective should be hyphenated (e.g., '20-story building')",
             None),
            
            # Suspended hyphenation (coordinate adjectives)
            # Pattern: "short- and long-term" (suspended hyphen)
            (r'\b(\w+)-\s+and\s+(\w+)-',
             "Suspended hyphenation: Correct format detected (e.g., 'short- and long-term')",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear rules (0.90),
        moderate for context-dependent (0.75).
        """
        # High confidence patterns
        high_confidence = [1, 5, 6, 9]  # -ly adverbs, self prefix, ex prefix, suspended hyphenation
        
        # Moderate-high confidence
        moderate_high = [2, 3, 7, 8]  # Numbers, fractions, age expressions
        
        # Moderate confidence (context-dependent)
        moderate = [0, 4]  # Compound adjectives, prefix vowel collision
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.85
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.80

