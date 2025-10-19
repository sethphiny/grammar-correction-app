"""
Pronoun Reference category - Detects pronoun reference and resolution issues.

Note: Some overlap with ambiguous_pronouns category, but this focuses on broader reference issues.

Implements detection for:
- Pronoun without clear antecedent
- Pronoun too far from antecedent
- Ambiguous "this", "that", "it" references
- Pronoun case errors (subject vs object)
- Reflexive pronoun errors
- Relative pronoun errors (who/whom, that/which)
- Pronoun-antecedent agreement
- Vague pronoun references
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class PronounReferenceCategory(BaseCategory):
    """
    Detects pronoun reference issues.
    
    Total patterns: 15
    Confidence: 0.70-0.90
    """
    
    def get_category_name(self) -> str:
        return 'pronoun_reference'
    
    def get_display_name(self) -> str:
        return 'Pronoun Reference'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return pronoun reference detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Vague "it" without clear antecedent
            (r'^\s*It\s+(is|was|has|had|will|would|can|could|should|may|might)\s+(important|necessary|essential|critical|vital|clear|obvious|apparent)\b',
             "Vague pronoun: 'It' at sentence start may be unclear - specify what 'it' refers to",
             None),
            
            # Vague "this" or "that" starting sentence
            (r'^\s*(This|That)\s+(is|was|will|would|can|could|should|may|means|shows|proves|demonstrates)\b',
             "Vague pronoun: Specify what 'this' or 'that' refers to (e.g., 'This approach', 'That method')",
             None),
            
            # "They" without plural antecedent
            (r'\b(person|individual|someone|anyone|everyone|somebody|anybody|everybody)\s+[\w\s]{1,20}\s+they\b',
             "Pronoun agreement: 'They' refers to singular antecedent - use 'he or she' or rephrase with plural",
             None),
            
            # Who vs whom (simple case)
            (r'\bwho\s+(I|you|he|she|it|we|they)\s+(met|saw|called|contacted|invited|helped)\b',
             "Pronoun case: Use 'whom' (object) not 'who' (subject) - 'whom I met' not 'who I met'",
             lambda m, t: f"whom {m.group(1)} {m.group(2)}"),
            
            # Whom used incorrectly as subject
            (r'\bwhom\s+(is|was|are|were|has|have|had|can|could|will|would)\b',
             "Pronoun case: Use 'who' (subject) not 'whom' (object) - 'who is' not 'whom is'",
             lambda m, t: f"who {m.group(1)}"),
            
            # Me vs I in compound subjects (common error)
            (r'\b(me|him|her|them|us)\s+and\s+(I|you|he|she|it|we|they)\s+(am|is|are|was|were|have|has|had|do|does|did|will|would|can|could)\b',
             "Pronoun case: Use subject pronouns in compound subjects ('I' not 'me', 'he' not 'him')",
             None),
            
            # I vs me after "between" (should be object form)
            (r'\bbetween\s+(I|he|she|we|they)\s+and\b',
             "Pronoun case: Use object pronouns after 'between' ('between him and me' not 'between he and I')",
             None),
            
            # Reflexive pronoun without matching subject
            (r'\b(myself|yourself|himself|herself|itself|ourselves|yourselves|themselves)\s+(?!and|,)',
             "Reflexive pronoun: Use reflexive pronouns only when subject and object are the same",
             None),
            
            # That vs which (restrictive vs non-restrictive)
            (r',\s+that\s+',
             "Relative pronoun: Use 'which' (not 'that') after commas for non-restrictive clauses",
             lambda m, t: ", which "),
            
            # Which without comma (restrictive clause)
            (r'\b(the|a|an)\s+\w+\s+which\s+(?!,)',
             "Relative pronoun: For restrictive clauses, consider 'that' instead of 'which' (or add comma for non-restrictive)",
             None),
            
            # Their/there/they're confusion
            (r'\btheir\s+(is|are|was|were)\b',
             "Pronoun confusion: Use 'there' (location) not 'their' (possessive) - 'there is' not 'their is'",
             lambda m, t: f"there {m.group(1)}"),
            
            (r'\bthere\s+(car|house|book|idea|plan|job|family|friend|money|time)\b',
             "Pronoun confusion: Use 'their' (possessive) not 'there' (location)",
             lambda m, t: f"their {m.group(1)}"),
            
            # Capitalization of "I"
            (r'\b i \b',
             "Capitalization: Pronoun 'I' is always capitalized",
             lambda m, t: " I "),
            
            # Generic "you" in formal writing (better to use "one" or passive)
            (r'\b(If|When|While)\s+you\s+(want|need|are|have|do)\b',
             "Informal pronoun: In formal writing, avoid generic 'you' - use 'one' or passive voice",
             None),
            
            # Pronoun shift (changing from one pronoun to another)
            (r'\b(I|we)\s+[\w\s]{5,30}\s+(you|they|he|she)\s+(?!(said|asked|replied))',
             "Pronoun shift: Maintain consistent pronouns - don't shift from 'I' to 'you' or 'they' mid-sentence",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        """
        # High confidence patterns
        high_confidence = [3, 4, 8, 10, 11, 12]  # who/whom, that/which, their/there, capitalization
        
        # Moderate-high confidence
        moderate_high = [5, 6, 7, 9]  # Compound subjects, between, reflexives
        
        # Moderate confidence
        moderate = [0, 1, 2, 13, 14]  # Vague pronouns, generic you, pronoun shifts
        
        if pattern_index in high_confidence:
            return 0.90
        elif pattern_index in moderate_high:
            return 0.85
        elif pattern_index in moderate:
            return 0.70
        else:
            return 0.80

