"""
Compounds category - Detects compound word errors.

Implements detection for:
- Compound words that should be one word
- Compound words that should be two words
- Compound words that should be hyphenated
- Common compound word errors
- Inconsistent compound usage
"""

from typing import List, Tuple, Optional, Dict
from .base_category import BaseCategory


class CompoundsCategory(BaseCategory):
    """
    Detects compound word errors.
    
    Total entries: 50+ compound word rules
    Confidence: 0.85-0.95
    """
    
    def get_category_name(self) -> str:
        return 'compounds'
    
    def get_display_name(self) -> str:
        return 'Compounds'
    
    def get_dictionary(self) -> Dict[str, str]:
        """
        Return dictionary of compound word corrections.
        
        Key: incorrect form
        Value: correct form
        """
        return {
            # Should be one word
            'any one': 'anyone',  # When meaning "anybody"
            'any body': 'anybody',
            'any thing': 'anything',
            'every one': 'everyone',  # When meaning "everybody"
            'every body': 'everybody',
            'every thing': 'everything',
            'some one': 'someone',  # When meaning "somebody"
            'some body': 'somebody',
            'some thing': 'something',
            'no body': 'nobody',
            'no one': 'no one',  # Correct as two words
            'may be': 'maybe',  # When meaning "perhaps"
            'in to': 'into',  # When showing motion or transformation
            'with in': 'within',
            'with out': 'without',
            'on to': 'onto',  # When meaning "on top of"
            'in side': 'inside',
            'out side': 'outside',
            'up on': 'upon',
            'through out': 'throughout',
            'where as': 'whereas',
            'any more': 'anymore',  # In negative contexts
            'every day life': 'everyday life',  # When used as adjective
            'high school': 'high school',  # Two words is correct
            'home work': 'homework',
            'class room': 'classroom',
            'bed room': 'bedroom',
            'bath room': 'bathroom',
            'any where': 'anywhere',
            'some where': 'somewhere',
            'no where': 'nowhere',
            'every where': 'everywhere',
            'mean while': 'meanwhile',
            'never the less': 'nevertheless',
            'none the less': 'nonetheless',
            
            # Should be two words
            'alot': 'a lot',
            'awhile': 'a while',  # When used as noun
            'alright': 'all right',  # In formal writing
            'atleast': 'at least',
            'infact': 'in fact',
            'aswell': 'as well',
            'inspite': 'in spite',
            'eachother': 'each other',
            'another': 'another',  # Correct as one word
            
            # Should be hyphenated
            'self esteem': 'self-esteem',
            'decision making': 'decision-making',  # When used as adjective
            'well being': 'well-being',
            'up to date': 'up-to-date',  # When used as adjective
            'state of the art': 'state-of-the-art',  # When used as adjective
            'high quality': 'high-quality',  # When used as adjective before noun
            'long term': 'long-term',  # When used as adjective
            'short term': 'short-term',  # When used as adjective
            'real time': 'real-time',  # When used as adjective
            'full time': 'full-time',  # When used as adjective
            'part time': 'part-time',  # When used as adjective
        }
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return empty list - this category uses dictionary matching.
        """
        return []
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level for dictionary matches.
        """
        return 0.90  # High confidence for dictionary-based compound corrections

