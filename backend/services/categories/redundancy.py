"""
Redundancy category - Detects redundant phrases and tautologies.

Contains a comprehensive dictionary of redundant phrases where the
modifier is unnecessary because it's already implied by the main word.

Examples:
- "absolutely essential" → "essential" (essential already means absolutely necessary)
- "past history" → "history" (history is always in the past)
- "advance planning" → "planning" (planning is always done in advance)
"""

from typing import List, Tuple, Optional
from .base_category import BaseCategory


class RedundancyCategory(BaseCategory):
    """
    Detects redundant phrases and tautologies.
    
    Total entries: 100+
    Confidence: 0.90 (high confidence for simple replacements)
    """
    
    def get_category_name(self) -> str:
        return 'redundancy'
    
    def get_display_name(self) -> str:
        return 'Redundant Phrases'
    
    def get_patterns(self) -> List[Tuple]:
        """Redundancy uses dictionary, not patterns."""
        return []
    
    def get_dictionary(self) -> dict:
        """
        Return dictionary of redundant phrases and their corrections.
        
        Format: {'redundant phrase': 'corrected version'}
        """
        return {
            'absolutely essential': 'essential',
            'advance planning': 'planning',
            'added bonus': 'bonus',
            'basic fundamentals': 'fundamentals',
            'close proximity': 'proximity',
            'completely eliminate': 'eliminate',
            'end result': 'result',
            'exact same': 'same',
            'free gift': 'gift',
            'future plans': 'plans',
            'general consensus': 'consensus',
            'past history': 'history',
            'personal opinion': 'opinion',
            'plan ahead': 'plan',
            'repeat again': 'repeat',
            'still remains': 'remains',
            'unexpected surprise': 'surprise',
            'usual custom': 'custom',
            'very unique': 'unique',
            'final outcome': 'outcome',
            'join together': 'join',
            'new innovation': 'innovation',
            'advance forward': 'advance',
            'alternative choice': 'alternative',
            'ask the question': 'ask',
            'at this point in time': 'now',
            'brief moment': 'moment',
            'collaborate together': 'collaborate',
            'combine together': 'combine',
            'complete monopoly': 'monopoly',
            'consensus of opinion': 'consensus',
            'continue on': 'continue',
            'different kinds': 'kinds',
            'during the course of': 'during',
            'each and every': 'each',
            'enclosed herewith': 'enclosed',
            'etc. etc.': 'etc.',
            'exact replica': 'replica',
            'false pretense': 'pretense',
            'few in number': 'few',
            'final conclusion': 'conclusion',
            'first priority': 'priority',
            'for the purpose of': 'to',
            'foreign imports': 'imports',
            'former graduate': 'graduate',
            'frozen ice': 'ice',
            'full satisfaction': 'satisfaction',
            'future prospect': 'prospect',
            'gain advantage': 'gain',
            'gather together': 'gather',
            'general public': 'public',
            'grateful thanks': 'thanks',
            'harmful injuries': 'injuries',
            'honest truth': 'truth',
            'in my opinion': 'I think',
            'in order to': 'to',
            'in the event that': 'if',
            'invited guests': 'guests',
            'just recently': 'recently',
            'keep continuing': 'continue',
            'lag behind': 'lag',
            'large in size': 'large',
            'live witness': 'witness',
            'made out of': 'made of',
            'major breakthrough': 'breakthrough',
            'may possibly': 'may',
            'meet together': 'meet',
            'merge together': 'merge',
            'might possibly': 'might',
            'mutual cooperation': 'cooperation',
            'necessary requirement': 'requirement',
            'new beginning': 'beginning',
            'null and void': 'void',
            'old adage': 'adage',
            'original founder': 'founder',
            'over exaggerate': 'exaggerate',
            'pare down': 'pare',
            'past experience': 'experience',
            'period of time': 'period',
            'personal friend': 'friend',
            'plan in advance': 'plan',
            'postpone until later': 'postpone',
            'present time': 'now',
            'previous experience': 'experience',
            'proceed ahead': 'proceed',
            'protrude out': 'protrude',
            'protest against': 'protest',
            'reason why': 'reason',
            'refer back': 'refer',
            'repeat the same': 'repeat',
            'revert back': 'revert',
            'rise up': 'rise',
            'same identical': 'identical',
            'scrutinize closely': 'scrutinize',
            'separate apart': 'separate',
            'sink down': 'sink',
            'skipped over': 'skipped',
            'small in size': 'small',
            'spell out in detail': 'spell out',
            'start off': 'start',
            'sudden impulse': 'impulse',
            'sum total': 'total',
            'surrounding circumstances': 'circumstances',
            'temporary reprieve': 'reprieve',
            'terrible tragedy': 'tragedy',
            'true facts': 'facts',
            'twelve noon': 'noon',
            'two twins': 'twins',
            'unexpected emergency': 'emergency',
            'unintentional mistake': 'mistake',
            'unite together': 'unite',
            'usual habit': 'habit',
            'utter perfection': 'perfection',
            'various different': 'various',
            'visible to the eye': 'visible',
            'warn in advance': 'warn',
            'whether or not': 'whether',
            'widow woman': 'widow',
        }
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """High confidence for simple redundancy replacements."""
        return 0.90
    
    def get_description(self) -> str:
        return "Detects redundant phrases where the modifier is unnecessary"

