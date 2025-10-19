"""
Word Order category - Detects incorrect word order in sentences.

Implements detection for:
- Misplaced adverbs (only, just, even, also)
- Incorrect adjective order
- Adverb placement with frequency words (always, never, often, usually)
- Question word order in statements
- Misplaced modifiers
- Time/place order issues
- Double negative constructions
- Split infinitives (optional/style-based)
- "Not only...but also" constructions
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class WordOrderCategory(BaseCategory):
    """
    Detects word order issues in English sentences.
    
    Total patterns: 12
    Confidence: 0.70-0.85 depending on clarity of the issue
    """
    
    def get_category_name(self) -> str:
        return 'word_order'
    
    def get_display_name(self) -> str:
        return 'Word Order'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return word order detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Misplaced "only" - should be placed immediately before the word it modifies
            # Pattern: "only" appearing far from what it modifies
            (r'\bonly\s+\w+\s+\w+\s+(the|a|an|his|her|their|my|your|our)\s+',
             "Misplaced 'only': Place 'only' immediately before the word it modifies for clarity",
             None),
            
            # Adverb between "to" and verb (split infinitive)
            # Pattern: "to quickly run" (some style guides discourage this)
            (r'\bto\s+(really|quickly|slowly|carefully|easily|hardly|barely|definitely|probably|actually|literally|basically)\s+\w+',
             "Split infinitive: Consider placing the adverb before 'to' or after the verb (style preference)",
             None),
            
            # Frequency adverbs in wrong position
            # Should come before main verb but after "to be"
            (r'\b(am|is|are|was|were)\s+[\w\s]{2,15}\s+(always|never|often|rarely|seldom|sometimes|usually|frequently|occasionally)\b',
             "Frequency adverb placement: Move frequency adverbs (always, never, often, etc.) immediately after 'be' verbs",
             None),
            
            # Frequency adverbs after main verb (should be before)
            (r'\b(go|goes|went|run|runs|ran|walk|walks|walked|eat|eats|ate|drink|drinks|drank|work|works|worked)\s+(always|never|often|rarely|seldom|sometimes|usually|frequently|occasionally)\b',
             "Frequency adverb placement: Place frequency adverbs before the main verb (e.g., 'always go' not 'go always')",
             None),
            
            # Place before time (incorrect - should be time before place)
            # Pattern: at/in [place] on/in [time]
            (r'\b(at|in)\s+(home|work|school|office|store|mall|park|beach)\s+(on|in|at)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|morning|afternoon|evening|night|January|February|March|April|May|June|July|August|September|October|November|December)\b',
             "Time/place order: Place time expressions after place expressions (e.g., 'at home on Monday' not 'on Monday at home')",
             None),
            
            # Double negatives creating word order confusion
            (r'\b(don\'t|doesn\'t|didn\'t|won\'t|wouldn\'t|can\'t|couldn\'t|haven\'t|hasn\'t|hadn\'t)\s+[\w\s]{1,20}\b(no|nothing|never|nobody|nowhere|neither|none)\b',
             "Double negative: Avoid double negatives - use either negative verb OR negative word, not both",
             None),
            
            # Misplaced "even" - should be immediately before the word it emphasizes
            (r'\beven\s+\w+\s+\w+\s+\w+\s+(the|a|an|his|her|their)\s+',
             "Misplaced 'even': Place 'even' immediately before the word it emphasizes",
             None),
            
            # "Just" misplaced - should be close to what it modifies
            (r'\bjust\s+(have|has|had|am|is|are|was|were|can|could|will|would|should|may|might)\s+[\w\s]{3,20}(the|a|an)\s+',
             "Misplaced 'just': Consider placing 'just' closer to the word it modifies for clarity",
             None),
            
            # Adjective order: Opinion adjectives should come before fact adjectives
            # Basic pattern for obvious violations (simplified)
            (r'\b(wooden|metal|plastic|glass|paper|cotton|silk|wool)\s+(beautiful|ugly|nice|lovely|awful|terrible|wonderful|horrible|good|bad)\s+',
             "Adjective order: Opinion adjectives (beautiful, nice) should come before material adjectives (wooden, metal)",
             None),
            
            # Question word order in a statement
            # Pattern: "Where he is going" instead of "Where is he going"
            (r'\b(where|when|why|how|what)\s+(he|she|it|they|we|I|you)\s+(is|are|was|were|has|have|had|can|could|will|would|should)\s+',
             "Question word order: Invert subject and auxiliary verb in questions",
             None),
            
            # "Also" placement - should come before the verb, after "be"
            (r'\b(go|goes|went|run|runs|ran|come|comes|came|see|sees|saw|think|thinks|thought|know|knows|knew)\s+also\b',
             "Misplaced 'also': Place 'also' before the main verb (e.g., 'also go' not 'go also')",
             None),
            
            # "Not only...but also" - parallel structure issue
            (r'\bnot\s+only\s+[\w\s]{5,30}\s+but\s+also\s+',
             "Check 'not only...but also' construction: Ensure parallel structure (same grammatical form after each part)",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear violations (0.85),
        moderate for style preferences (0.70).
        """
        # High confidence patterns (clear violations)
        high_confidence = [3, 4, 5, 9, 10]  # Frequency adverb misplacement, time/place, double negatives, question order, "also"
        
        # Moderate confidence patterns (style or context-dependent)
        moderate_confidence = [0, 1, 2, 6, 7, 8, 11]  # "only", split infinitives, "even", "just", adjective order, "not only"
        
        if pattern_index in high_confidence:
            return 0.85
        elif pattern_index in moderate_confidence:
            return 0.70
        else:
            return 0.75

