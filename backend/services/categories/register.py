"""
Register category - Detects formality and register issues in writing.

Implements detection for:
- Informal language in formal contexts
- Contractions that should be expanded in formal writing
- Slang and colloquialisms
- First/second person in academic writing
- Casual intensifiers and qualifiers
- Informal phrasal verbs
- Text-speak and abbreviations
- Mixed register (inconsistent formality)
- Overly casual expressions
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class RegisterCategory(BaseCategory):
    """
    Detects register and formality issues in writing.
    
    Total patterns: 20
    Confidence: 0.70-0.85 depending on context
    
    Note: These are advisory - appropriate register depends on context.
    """
    
    def get_category_name(self) -> str:
        return 'register'
    
    def get_display_name(self) -> str:
        return 'Register / Formality'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return register/formality detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Contractions (inappropriate in formal writing)
            (r"\b(can't|cannot't|couldn't|shouldn't|wouldn't|won't|don't|doesn't|didn't|haven't|hasn't|hadn't|isn't|aren't|wasn't|weren't)\b",
             "Informal contraction: Consider expanding in formal writing (e.g., 'can't' → 'cannot')",
             None),
            
            (r"\b(I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b",
             "Informal contraction: Consider expanding in formal writing (e.g., 'I'm' → 'I am')",
             None),
            
            # First person in academic writing
            (r"\b(I\s+think|I\s+believe|I\s+feel|In\s+my\s+opinion)\b",
             "Informal register: In academic writing, avoid first person - state findings objectively",
             None),
            
            (r"\b(We\s+will\s+show|We\s+will\s+prove|We\s+will\s+demonstrate)\b",
             "Informal register: In academic writing, prefer 'This paper demonstrates' over 'We will show'",
             None),
            
            # Second person (too casual for formal writing)
            (r"\b(You\s+can\s+see|You\s+should|You\s+might|You\s+need\s+to)\b",
             "Informal register: Avoid second person 'you' in formal writing - use 'one can' or passive voice",
             None),
            
            # Casual intensifiers
            (r"\b(really|totally|super|pretty|kind of|sort of)\s+(good|bad|important|interesting|amazing|awful)\b",
             "Informal intensifier: Use more formal intensifiers in academic writing (e.g., 'extremely', 'particularly', 'notably')",
             None),
            
            (r"\b(a\s+lot\s+of|lots\s+of)\b",
             "Informal quantifier: In formal writing, use 'many', 'numerous', 'a large number of', or specific quantities",
             None),
            
            # Slang and colloquialisms
            (r"\b(gonna|wanna|gotta|kinda|sorta)\b",
             "Slang: Inappropriate for formal writing - use full forms ('going to', 'want to', etc.)",
             None),
            
            (r"\b(kids|guys)\b",
             "Colloquialism: In formal writing, use 'children' instead of 'kids', 'people' instead of 'guys'",
             None),
            
            # Informal phrasal verbs (prefer single-word equivalents)
            (r"\b(find\s+out|figure\s+out|come\s+up\s+with)\b",
             "Informal phrasal verb: Consider formal alternatives ('discover', 'determine', 'develop')",
             None),
            
            (r"\b(get\s+rid\s+of|put\s+up\s+with|look\s+into)\b",
             "Informal phrasal verb: Consider formal alternatives ('eliminate', 'tolerate', 'investigate')",
             None),
            
            # Vague/casual language
            (r"\b(thing|things|stuff)\b",
             "Vague informal language: Be specific in formal writing",
             None),
            
            (r"\b(big|huge|tiny|little)\s+(problem|issue|difference|impact)\b",
             "Informal descriptor: Use more precise terms ('significant', 'substantial', 'minimal', 'negligible')",
             None),
            
            # Text-speak and abbreviations (highly informal)
            (r"\b(btw|fyi|asap|etc\.)\b",
             "Abbreviation: In formal writing, spell out abbreviations ('by the way', 'for your information', 'as soon as possible')",
             None),
            
            # Casual connectors
            (r"\b(Plus|Also|And\s+so|So\s+then)\b",
             "Informal connector: Use formal transitions ('Furthermore', 'Moreover', 'Therefore', 'Consequently')",
             None),
            
            # Rhetorical questions (too casual for formal writing)
            (r"\bWhy\s+is\s+this\s+(important|relevant|significant)\?\b",
             "Informal rhetoric: Rhetorical questions are too casual for formal writing - state directly",
             None),
            
            # Emphatic "very" (overused, informal)
            (r"\b(very\s+very|really\s+really)\b",
             "Informal emphasis: Avoid repetition - use stronger vocabulary instead",
             None),
            
            # Casual sentence starters
            (r"^\s*(So|Basically|Anyway),?\s+",
             "Informal starter: Avoid casual sentence starters in formal writing",
             None),
            
            # "Get" overuse (very informal)
            (r"\b(get|gets|got|getting)\s+(better|worse|bigger|smaller|harder|easier)\b",
             "Informal 'get': Use more formal alternatives ('become', 'grow', 'increase', 'decrease', 'improve', 'deteriorate')",
             None),
            
            # Exclamation marks (too emotional for formal writing)
            (r"[!]{1,}",
             "Informal punctuation: Exclamation marks are generally too casual for formal academic writing",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Note: These are context-dependent - confidence reflects how likely
        the pattern indicates a register issue in formal writing.
        """
        # High confidence patterns (clear informality)
        high_confidence = [7, 8, 13, 16]  # Slang, text-speak, very very, exclamation marks
        
        # Moderate-high confidence patterns
        moderate_high = [0, 1, 5, 6, 9, 10, 11, 14, 17, 18, 19]  # Contractions, intensifiers, phrasal verbs
        
        # Moderate confidence patterns (context-dependent)
        moderate = [2, 3, 4, 12, 15]  # First/second person, vague language
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_high:
            return 0.78
        elif pattern_index in moderate:
            return 0.70
        else:
            return 0.75

