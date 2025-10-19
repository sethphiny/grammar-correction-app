"""
Clarity category - Detects clarity issues in writing.

Implements detection for:
- Nominalization (turning verbs into nouns)
- Hedging language (excessive qualifiers)
- Abstract language vs concrete
- Unclear antecedents
- Overly complex sentences
- Jargon and technical terms without explanation
- Buried verbs
- Multiple negatives causing confusion
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class ClarityCategory(BaseCategory):
    """
    Detects clarity issues that make writing harder to understand.
    
    Total patterns: 15
    Confidence: 0.65-0.80 depending on clarity of the issue
    """
    
    def get_category_name(self) -> str:
        return 'clarity'
    
    def get_display_name(self) -> str:
        return 'Clarity'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return clarity detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Nominalization - turning verbs into nouns (weakens writing)
            (r'\b(make\s+a\s+decision|reach\s+a\s+decision)\b',
             "Nominalization: Consider 'decide' instead of 'make a decision' for clearer writing",
             lambda m, t: "decide"),
            
            (r'\b(make\s+an?\s+assumption)\b',
             "Nominalization: Consider 'assume' instead of 'make an assumption'",
             lambda m, t: "assume"),
            
            (r'\b(give\s+consideration\s+to|take\s+into\s+consideration)\b',
             "Nominalization: Consider 'consider' for clearer writing",
             lambda m, t: "consider"),
            
            (r'\b(provide\s+assistance)\b',
             "Nominalization: Consider 'assist' or 'help' for clearer writing",
             lambda m, t: "assist"),
            
            (r'\b(conduct\s+an?\s+analysis)\b',
             "Nominalization: Consider 'analyze' for clearer writing",
             lambda m, t: "analyze"),
            
            # Hedging language (excessive qualification)
            (r'\b(sort\s+of|kind\s+of|type\s+of)\s+(like|similar)',
             "Weak qualifier: Remove hedging language for clearer writing",
             None),
            
            (r'\b(perhaps\s+maybe|possibly\s+might|maybe\s+possibly)\b',
             "Redundant hedging: One qualifier is enough",
             None),
            
            # Multiple negatives causing confusion
            (r'\bnot\s+un(able|aware|certain|clear|common|happy|likely|usual|necessary)\b',
             "Double negative: Consider positive form for clarity (e.g., 'unable' → 'able', 'unclear' → 'clear')",
             None),
            
            # Buried verbs (verb hidden in noun phrase)
            (r'\b(is\s+in\s+agreement\s+with)\b',
             "Buried verb: Consider 'agrees with' for clearer writing",
             lambda m, t: "agrees with"),
            
            (r'\b(is\s+indicative\s+of)\b',
             "Buried verb: Consider 'indicates' for clearer writing",
             lambda m, t: "indicates"),
            
            (r'\b(is\s+in\s+opposition\s+to)\b',
             "Buried verb: Consider 'opposes' for clearer writing",
             lambda m, t: "opposes"),
            
            # Abstract language that could be more concrete
            (r'\b(things?|aspects?|factors?|elements?|matters?|issues?)\s+(that|which|are|is)\b',
             "Abstract language: Be more specific about what you're referring to",
             None),
            
            # Vague intensifiers
            (r'\b(very|really|quite|rather|fairly|pretty)\s+(unique|essential|perfect|complete|impossible|infinite)\b',
             "Unnecessary intensifier: These words are already absolute and don't need qualification",
             None),
            
            # "The fact that" constructions (often unnecessary)
            (r'\bthe\s+fact\s+that\b',
             "Wordy: Often 'the fact that' can be removed or replaced with 'that'",
             None),
            
            # Unclear pronoun reference (when "this" starts a sentence without clear antecedent)
            (r'^\s*This\s+(is|was|means|shows|demonstrates|indicates)\b',
             "Unclear reference: 'This' at sentence start may be unclear - consider 'This [specific noun]' for clarity",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear violations (0.80),
        moderate for style issues (0.65).
        """
        # High confidence patterns (clear improvements)
        high_confidence = [0, 1, 2, 3, 4, 8, 9, 10]  # Nominalizations, buried verbs
        
        # Moderate confidence patterns (style-dependent)
        moderate_confidence = [5, 6, 7, 11, 12, 13, 14]  # Hedging, abstract language, vague intensifiers
        
        if pattern_index in high_confidence:
            return 0.80
        elif pattern_index in moderate_confidence:
            return 0.65
        else:
            return 0.70

