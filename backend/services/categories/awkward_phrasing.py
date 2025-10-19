"""
Awkward Phrasing category - Detects wordy or awkward expressions.

Contains phrases that can be replaced with simpler, more direct alternatives.

Examples:
- "at the present time" → "now"
- "due to the fact that" → "because"
- "make a decision" → "decide"

Note: "a lot of" is explicitly excluded as it's valid casual/conversational language.
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class AwkwardPhrasingCategory(BaseCategory):
    """
    Detects awkward or wordy phrasing that can be simplified.
    
    Total entries: 100+
    Confidence: 0.85
    """
    
    def get_category_name(self) -> str:
        return 'awkward_phrasing'
    
    def get_display_name(self) -> str:
        return 'Awkward Phrasing'
    
    def get_patterns(self) -> List[Tuple]:
        """Awkward phrasing uses dictionary, not patterns."""
        return []
    
    def get_dictionary(self) -> dict:
        """Return dictionary of awkward phrases and their better alternatives."""
        return {
            # NOTE: "a lot of" is valid casual/conversational language - deliberately excluded
            'a majority of': 'most',
            'a number of': 'several',
            'accounted for by the fact that': 'because',
            'all of a sudden': 'suddenly',
            'along the lines of': 'like',
            'are of the same opinion': 'agree',
            'as a matter of fact': 'in fact',
            'as of yet': 'yet',
            'as per': 'according to',
            'as to': 'about',
            'as to whether': 'whether',
            'at all times': 'always',
            'at the present time': 'now',
            'at this time': 'now',
            'by means of': 'by',
            'by the name of': 'named',
            'by virtue of': 'by',
            'came to a realization': 'realized',
            'came to an abrupt end': 'ended abruptly',
            'concerning the matter of': 'about',
            'despite the fact that': 'although',
            'due to the fact that': 'because',
            'during the time that': 'while',
            'fewer in number': 'fewer',
            'for the purpose of': 'to',
            'for the reason that': 'because',
            'give consideration to': 'consider',
            'give rise to': 'cause',
            'had occasion to be': 'was',
            'has a tendency to': 'tends to',
            'has the ability to': 'can',
            'have a need for': 'need',
            'have an effect on': 'affect',
            'have the capacity to': 'can',
            'in a timely manner': 'promptly',
            'in all likelihood': 'probably',
            'in an effort to': 'to',
            'in close proximity to': 'near',
            'in lieu of': 'instead of',
            'in light of the fact that': 'because',
            'in many cases': 'often',
            'in most cases': 'usually',
            'in order that': 'so',
            'in some cases': 'sometimes',
            'in spite of': 'despite',
            'in spite of the fact that': 'although',
            'in such a manner': 'so',
            'in terms of': 'regarding',
            'in the amount of': 'for',
            'in the course of': 'during',
            'in the event that': 'if',
            'in the final analysis': 'finally',
            'in the nature of': 'like',
            'in the near future': 'soon',
            'in the neighborhood of': 'about',
            'in the process of': 'during',
            'in view of the fact that': 'since',
            'is able to': 'can',
            'is capable of': 'can',
            'is in a position to': 'can',
            'it is apparent that': 'apparently',
            'it is clear that': 'clearly',
            'it is evident that': 'evidently',
            'it is obvious that': 'obviously',
            'made a decision': 'decided',
            'make a determination': 'determine',
            'make an assumption': 'assume',
            'make mention of': 'mention',
            'make reference to': 'refer to',
            'make the acquaintance of': 'meet',
            'make a decision': 'decide',
            'notwithstanding the fact that': 'although',
            'of the opinion that': 'think',
            'on a daily basis': 'daily',
            'on a regular basis': 'regularly',
            'on account of': 'because',
            'on behalf of': 'for',
            'on the basis of': 'based on',
            'on the grounds that': 'because',
            'on the occasion of': 'when',
            'on the part of': 'by',
            'owing to the fact that': 'because',
            'pertaining to': 'about',
            'prior to': 'before',
            'provided that': 'if',
            'put an end to': 'end',
            'reach a conclusion': 'conclude',
            'regardless of the fact that': 'although',
            'relative to': 'about',
            'subsequent to': 'after',
            'take action': 'act',
            'take into consideration': 'consider',
            'the majority of': 'most',
            'the question as to whether': 'whether',
            'the reason is because': 'because',
            'there is no doubt but that': 'doubtless',
            'through the use of': 'by',
            'until such time as': 'until',
            'with reference to': 'about',
            'with regard to': 'regarding',
            'with respect to': 'about',
            'with the exception of': 'except',
            'with the result that': 'so that',
        }
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.85
    
    def get_description(self) -> str:
        return "Detects wordy or awkward phrasing that can be simplified"

