"""Dialogue category - Detects dialogue punctuation and formatting issues."""
from typing import List, Tuple
from .base_category import BaseCategory

class DialogueCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'dialogue'
    
    def get_display_name(self) -> str:
        return 'Dialogue'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r'([a-zA-Z])"(\s+)(said|asked|replied|answered|whispered|shouted|exclaimed|muttered|added|continued|explained|insisted|suggested|declared|announced|complained|admitted|agreed|disagreed|interrupted|protested)',
             "Missing comma before closing quotation mark in dialogue",
             lambda m, t: f'{m.group(1)}," {m.group(3)}'),
            (r'"(\s*),(\s+)(said|asked|replied|answered|whispered|shouted|exclaimed|muttered|added|continued|explained)',
             "Comma should be inside quotation marks before dialogue tag",
             lambda m, t: f'," {m.group(3)}'),
            (r'"\s+([A-Z])(said|aid)\b',
             "Dialogue tag should be lowercase after quotation mark",
             lambda m, t: f'" {m.group(1).lower()}{m.group(2)}'),
            (r'"([^"]+)"\s+(said|asked|replied|answered|whispered|shouted)',
             "Dialogue formatting looks correct",
             lambda m, t: m.group(0)),
            (r'([a-zA-Z])"(\s+)(and|but|then|so)',
             "Consider adding comma before dialogue tag or rephrasing",
             lambda m, t: f'{m.group(1)}," {m.group(3)}'),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.80

