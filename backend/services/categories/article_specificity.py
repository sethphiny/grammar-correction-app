"""Article/Specificity category - Detects article usage and vague language."""
from typing import List, Tuple
from .base_category import BaseCategory

class ArticleSpecificityCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'article_specificity'
    
    def get_display_name(self) -> str:
        return 'Article/Specificity'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            (r'\ba\s+(elephant|eagle|engine|example|evening|exercise|expert|eye|idea|island|office|umbrella|uncle|apple|orange|egg|arm|ear|ice|ocean|airplane)\b',
             "Article error: Use 'an' before words starting with vowel sound",
             lambda m, t: f"an {m.group(1)}"),
            (r'\ban\s+(car|book|house|dog|cat|man|woman|child|student|teacher|doctor|user|union|European|one)\b',
             "Article error: Use 'a' before words starting with consonant sound",
             lambda m, t: f"a {m.group(1)}"),
            (r'\bthe\s+(both|all|each|every|some|any|no)\s+',
             "Unnecessary article: Remove 'the' before quantifiers",
             lambda m, t: f"{m.group(1)} "),
            (r'\b(a\s+)?(thing|stuff|item|object|element)\b',
             "Vague language: Be more specific",
             None),
            (r'\b(good|bad|nice|great)\b',
             "Vague language: Use more specific descriptive words",
             None),
            (r'\b(lots?\s+of|a\s+lot\s+of)\b',
             "Vague quantifier: Use more specific numbers when possible",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.75 if pattern_index < 3 else 0.65

