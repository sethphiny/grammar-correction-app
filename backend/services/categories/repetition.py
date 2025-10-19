"""
Repetition category - Detects repeated words and phrases.

Implements detection for:
- Immediate word repetition (word word)
- Repeated words within close proximity
- Repeated phrases
- Stuttering effects
- Redundant word pairs
- Same word at sentence start/end
- Overused transition words
- Repeated content words in short span
"""

from typing import List, Tuple, Optional
import re
from .base_category import BaseCategory


class RepetitionCategory(BaseCategory):
    """
    Detects repetition issues in writing.
    
    Total patterns: 12
    Confidence: 0.75-0.90 depending on the type of repetition
    """
    
    def get_category_name(self) -> str:
        return 'repetition'
    
    def get_display_name(self) -> str:
        return 'Repetition'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return repetition detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Immediate word repetition (word word) - most obvious
            # Exclude intentional repetition like "very very" or dialogue emphasis
            (r'\b(?!the|a|an|very|really|so|to|and|or|but)(\w{3,})\s+\1\b',
             "Repeated word: Remove duplicate word",
             lambda m, t: m.group(1)),
            
            # Repeated "the the" or "a a" (common typo)
            (r'\b(the|a|an)\s+\1\b',
             "Repeated article: Remove duplicate article",
             lambda m, t: m.group(1)),
            
            # Repeated "and and", "or or", "but but"
            (r'\b(and|or|but)\s+\1\b',
             "Repeated conjunction: Remove duplicate conjunction",
             lambda m, t: m.group(1)),
            
            # Repeated "to to"
            (r'\bto\s+to\b',
             "Repeated 'to': Remove duplicate 'to'",
             lambda m, t: "to"),
            
            # Same word repeated within 5 words (content words only)
            # This is more complex - we'll use a simpler pattern
            (r'\b(\w{5,})\s+\w+\s+\1\b',
             "Word repetition: Same word used twice in close proximity - consider using a synonym or pronoun",
             None),
            
            (r'\b(\w{5,})\s+\w+\s+\w+\s+\1\b',
             "Word repetition: Same word used twice within a few words - consider varying your vocabulary",
             None),
            
            # Repeated phrase patterns (simple)
            (r'\b(\w+\s+\w+)\s+.*?\s+\1\b',
             "Phrase repetition: Same phrase appears twice - consider rephrasing for variety",
             None),
            
            # Starting consecutive sentences with the same word
            # This requires multi-line context, so we'll flag potential issues
            (r'^\s*(However|Therefore|Moreover|Furthermore|Additionally|Consequently),',
             "Overused transition: Using the same transition word frequently - vary your transitions",
             None),
            
            # Repeated sentence structures (basic detection)
            # Pattern: "The X is Y. The X is Z."
            (r'\bThe\s+(\w+)\s+(is|was|are|were)\s+[\w\s]{3,15}\.\s+The\s+\1\s+(is|was|are|were)\b',
             "Repeated sentence structure: Consider varying sentence beginnings for better flow",
             None),
            
            # Stuttering/stammering effects (unintentional)
            (r'\b(\w)\1{2,}',
             "Possible stuttering: Multiple repeated letters - check if intentional or typo",
             None),
            
            # Same adjective or adverb repeated
            (r'\b(very|really|quite|extremely|incredibly|absolutely)\s+([\w\s]{1,15})\s+\1\b',
             "Repeated intensifier: Using the same intensifier twice - remove one or use different intensifiers",
             None),
            
            # Ending sentence and starting next with same word
            (r'(\w{4,})\.\s+\1\b',
             "Word repetition across sentences: Sentence ends and next begins with same word - consider rephrasing",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for obvious repetition (0.90),
        moderate for potential issues (0.75).
        """
        # High confidence patterns (clear repetition)
        high_confidence = [0, 1, 2, 3, 9]  # Immediate repetition, stuttering
        
        # Moderate-high confidence
        moderate_high = [4, 5, 8, 11]  # Word repetition within close proximity
        
        # Moderate confidence (context-dependent)
        moderate = [6, 7, 10]  # Phrase repetition, transitions, intensifiers
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.80
        elif pattern_index in moderate:
            return 0.75
        else:
            return 0.85

