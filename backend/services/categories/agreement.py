"""
Agreement category - Detects subject-verb agreement errors.

Focuses on conservative, high-confidence patterns to avoid false positives.
"""

from typing import List, Tuple
from .base_category import BaseCategory


class AgreementCategory(BaseCategory):
    """Subject-verb agreement detection (9 conservative patterns)."""
    
    def get_category_name(self) -> str:
        return 'agreement'
    
    def get_display_name(self) -> str:
        return 'Agreement'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            # Basic plural subjects with singular verbs
            (r'\b(they|we|you)\s+(is|was|has)\b',
             "Subject-verb agreement error: plural subject needs plural verb",
             lambda m, t: f"{m.group(1)} {'are' if m.group(2) == 'is' else 'were' if m.group(2) == 'was' else 'have'}"),
            
            # Singular pronouns with plural verbs
            (r'\b(he|she|it)\s+(are|were|have)\b',
             "Subject-verb agreement error: singular subject needs singular verb",
             lambda m, t: f"{m.group(1)} {'is' if m.group(2) == 'are' else 'was' if m.group(2) == 'were' else 'has'}"),
            
            # "I" with wrong verb forms
            (r'\bI\s+(is|are|was|were)\b',
             "Subject-verb agreement error with 'I'",
             lambda m, t: f"I {'am' if m.group(1) in ['is', 'are'] else 'was'}"),
            
            # "he/she/it don't"
            (r'\b(he|she|it)\s+don\'t\b',
             "Subject-verb agreement error: singular subject should use 'doesn't'",
             lambda m, t: f"{m.group(1)} doesn't"),
            
            # "They/We/You was"
            (r'\b(they|we|you)\s+was\b',
             "Subject-verb agreement error: plural subject needs 'were'",
             lambda m, t: f"{m.group(1)} were"),
            
            # "He/She/It have"
            (r'\b(he|she|it)\s+have\s+(a|an|the|to|been)\b',
             "Subject-verb agreement error: singular subject needs 'has'",
             lambda m, t: f"{m.group(1)} has {m.group(2)}"),
            
            # Common plural nouns with singular verbs
            (r'\b(people|children|men|women|police)\s+(is|was|has)\b',
             "Subject-verb agreement error: plural noun needs plural verb",
             lambda m, t: f"{m.group(1)} {'are' if m.group(2) == 'is' else 'were' if m.group(2) == 'was' else 'have'}"),
            
            # "There is" + plural
            (r'\bthere\s+is\s+(many|several|multiple|some|few|two|three|four|five)\b',
             "Subject-verb agreement error: use 'there are' with plural quantities",
             lambda m, t: f"there are {m.group(1)}"),
            
            # Third person singular missing 's'
            (r'\b(he|she|it)\s+(walk|talk|run|eat|sleep|work|live|play|need|want|like|love|hate|think|know|feel)\s+(to|the|a|an|in|on|at|with|for|very|really|always|never|often|sometimes)\b',
             "Subject-verb agreement error: third person singular needs verb + 's'",
             lambda m, t: f"{m.group(1)} {m.group(2)}s {m.group(3)}"),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.85

