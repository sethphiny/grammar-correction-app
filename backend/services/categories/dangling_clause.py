"""
Dangling Clause category - Detects dangling modifiers and misplaced clauses.
"""

from typing import List, Tuple
from .base_category import BaseCategory


class DanglingClauseCategory(BaseCategory):
    """Dangling modifiers and misplaced clauses (8 patterns)."""
    
    def get_category_name(self) -> str:
        return 'dangling_clause'
    
    def get_display_name(self) -> str:
        return 'Dangling Clause'
    
    def get_patterns(self) -> List[Tuple]:
        return [
            # Participial phrases with non-human subject
            (r'^(Walking|Running|Driving|Flying|Swimming|Riding|Climbing|Standing|Sitting|Looking|Reading|Writing|Thinking|Feeling|Watching|Listening|Speaking|Talking|Eating|Drinking|Sleeping|Working|Playing)\s+.*,\s+(the|a|an)\s+(book|movie|car|house|tree|trees|building|door|window|table|chair|bed|phone|computer|TV|radio|paper|document|report|letter|email|message|city|town|place|thing|object|item|flowers|sky|sun|moon|stars|clouds|weather|landscape|view|scenery|picture|painting|photo)\b',
             "Dangling modifier: The participial phrase doesn't clearly connect to the subject",
             None),
            
            # "After/Before/While [verb]ing..., the [thing]"
            (r'^(After|Before|While|When|Upon)\s+(reading|writing|looking|seeing|hearing|thinking|considering|reviewing|examining|analyzing)\s+.*,\s+(the|a|an)\s+(book|movie|report|document|paper|article|study|research|data|information|evidence|result|finding|conclusion)\b',
             "Dangling modifier: Clarify who performed the action in the introductory phrase",
             None),
            
            # "To [verb]..., [subject] must/should"
            (r'^To\s+(achieve|reach|obtain|get|find|discover|understand|learn|master|complete|finish|succeed|win|pass)\s+.*,\s+(the|a|an)\s+\w+\s+(must|should|needs to|has to|ought to)\b',
             "Possible dangling infinitive: Ensure the subject can logically perform the action",
             None),
            
            # "Having [past participle]..., the [thing]"
            (r'^Having\s+(been|seen|heard|read|written|completed|finished|done|found|discovered|learned|studied|reviewed|examined|analyzed)\s+.*,\s+(the|a|an)\s+(book|movie|report|document|study|article|paper|research|data|project|work|task|job)\b',
             "Dangling modifier: The 'having' phrase needs a clear subject",
             None),
            
            # "Born in..., his/her [career/work]"
            (r'^Born\s+in\s+.*,\s+(his|her|their)\s+(work|career|book|novel|research|study|paper|article|writing|art|music|film|movie|project)\b',
             "Dangling modifier: The subject should be the person, not their work",
             None),
            
            # "At the age of..., his/her [work]"
            (r'^At\s+the\s+age\s+of\s+.*,\s+(his|her|their)\s+(work|career|book|novel|research|study|paper|article|writing|project)\b',
             "Dangling modifier: The subject should be the person, not their work",
             None),
            
            # "[verb]ing..., it/this/that"
            (r'^[A-Z][a-z]+ing\s+.*,\s+(it|this|that)\s+(is|was|would|could|should|may|might|can|will)\b',
             "Possible dangling modifier: Ensure the pronoun clearly refers to the subject performing the action",
             None),
            
            # "Without [verb]ing..., the [thing]"
            (r'^Without\s+(reading|seeing|hearing|knowing|understanding|considering|thinking|reviewing|checking|examining|looking)\s+.*,\s+(the|a|an)\s+(decision|conclusion|result|outcome|answer|solution|choice|plan|strategy)\b',
             "Dangling modifier: Clarify who should perform the action in 'without' phrase",
             None),
        ]
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.68

