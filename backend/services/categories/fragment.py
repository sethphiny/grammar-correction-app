"""
Fragment category - Detects sentence fragments and incomplete sentences.

Implements detection for:
- Dependent clause fragments (Because..., Although..., While...)
- Subordinate "That" clauses
- Participial phrases
- Prepositional phrases
- "Such as" and "For example" fragments
- Infinitive phrases
- Noun phrase fragments
- Relative clause fragments
- Question word fragments
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class FragmentCategory(BaseCategory):
    """
    Detects sentence fragments - incomplete sentences without main verbs
    or dependent clauses standing alone.
    
    Total patterns: 10
    Confidence: 0.75 for clear fragments, 0.68 for possible fragments
    """
    
    def get_category_name(self) -> str:
        return 'fragment'
    
    def get_display_name(self) -> str:
        return 'Fragment'
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return fragment detection patterns.
        
        Each tuple contains:
        - pattern: regex pattern to match
        - description: explanation of the issue
        - fix_function: function to generate fix (None for advisory only)
        """
        return [
            # Dependent clause fragments: "Because...", "Although...", "While...", etc.
            # Only flag if the sentence ENDS with a period and doesn't contain a comma
            (r'^(Because|Although|Though|While|Since|Unless|Until|If|When|Whenever|Whether|As)\s+[^,]+\.$',
             "Sentence fragment: Dependent clause needs an independent clause to be complete",
             None),
            
            # Subordinate clause starting with "That" without main clause
            (r'^That\s+[^,]+\.$',
             "Possible fragment: 'That' clause may need a main clause",
             None),
            
            # Participial phrases standing alone: "Walking down the street."
            # Pattern: starts with -ing verb, no clear subject-verb pair
            (r'^(Walking|Running|Driving|Flying|Swimming|Riding|Climbing|Standing|Sitting|Looking|Reading|Writing|Thinking|Feeling|Watching|Listening|Speaking|Talking|Eating|Drinking|Working|Playing|Going|Coming|Being|Having|Doing|Making|Taking|Giving|Getting)\s+(?:[\w\s]+(?:the|a|an|my|your|his|her|their|our|its)\s+[\w\s]+)\.$',
             "Fragment: Participial phrase needs a subject and main verb",
             None),
            
            # Prepositional phrase fragments: "In the morning.", "After the meeting."
            # Very short sentences starting with preposition (< 6 words)
            (r'^(In|On|At|By|With|Without|After|Before|During|Through|Under|Over|Between|Among|Against|About)\s+(?:\w+\s+){1,4}\w+\.$',
             "Possible fragment: Prepositional phrase may need a subject and verb",
             None),
            
            # "Such as" fragments: "Such as books, pens, and paper."
            (r'^Such as\s+.+\.$',
             "Fragment: 'Such as' phrase needs to be part of a complete sentence",
             None),
            
            # "For example" or "For instance" standing alone with just a list
            # Flag if it's very short (< 8 words) and has no verb
            (r'^(For example|For instance),?\s+(?:[\w\s,]+(?:and|or)\s+[\w\s]+)\.$',
             "Possible fragment: Consider connecting to previous sentence or adding a subject and verb",
             None),
            
            # Infinitive phrase fragments: "To understand the concept."
            # Pattern: starts with "To [verb]" and ends with period, short (< 10 words)
            (r'^To\s+\w+\s+(?:\w+\s+){1,7}\w+\.$',
             "Possible fragment: Infinitive phrase may need a main clause",
             None),
            
            # Noun phrase fragments: "A beautiful day." without context
            # Very conservative: flag only obvious fragments (article + adj + noun only)
            (r'^(A|An|The)\s+(?:very|really|quite|rather|extremely|incredibly|absolutely)?\s*(?:\w+\s+){0,2}\w+\.$',
             "Possible fragment: Noun phrase may need a verb to form a complete sentence",
             None),
            
            # Relative clause fragments: "Which was unexpected." or "Who came late."
            (r'^(Which|Who|Whom|Whose|Where)\s+[^,]+\.$',
             "Fragment: Relative clause needs to be connected to a main clause",
             None),
            
            # Question word fragments (when not a question): "Why the delay."
            # Pattern: question word + noun phrase, but ends with period (not question mark)
            (r'^(Why|How|What|Where|When)\s+(?:the|a|an|this|that)\s+\w+\.$',
             "Possible fragment: Consider completing the sentence or using a question mark",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return confidence level based on pattern type.
        
        Higher confidence for clear fragments (0.75),
        lower for possible fragments (0.68).
        """
        # Patterns 0, 4, 8 are clear fragments
        if pattern_index in [0, 4, 8]:
            return 0.75
        else:
            return 0.68
    
    def get_description(self) -> str:
        return "Detects sentence fragments and incomplete sentences"

