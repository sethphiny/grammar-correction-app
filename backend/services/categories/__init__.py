"""
Grammar checking categories module.

Each category is defined in its own file for easy maintenance and enhancement.
"""

from .base_category import BaseCategory
from .redundancy import RedundancyCategory
from .awkward_phrasing import AwkwardPhrasingCategory
from .punctuation import PunctuationCategory
from .grammar import GrammarCategory
from .dialogue import DialogueCategory
from .capitalisation import CapitalisationCategory
from .tense_consistency import TenseConsistencyCategory
from .spelling import SpellingCategory
from .parallelism_concision import ParallelismConcisionCategory
from .article_specificity import ArticleSpecificityCategory
from .agreement import AgreementCategory
from .ambiguous_pronouns import AmbiguousPronounsCategory
from .dangling_clause import DanglingClauseCategory
from .fragment import FragmentCategory
from .run_on import RunOnCategory
from .split_line import SplitLineCategory
from .word_order import WordOrderCategory
from .contrast import ContrastCategory
from .clarity import ClarityCategory
from .preposition import PrepositionCategory
from .register import RegisterCategory
from .repetition import RepetitionCategory
from .comma_splice import CommaSpliceCategory
from .coordination import CoordinationCategory
from .ellipsis import EllipsisCategory
from .hyphenation import HyphenationCategory
from .missing_period import MissingPeriodCategory
from .number_style import NumberStyleCategory
from .possessive import PossessiveCategory
from .broken_quote import BrokenQuoteCategory
from .compounds import CompoundsCategory
from .pronoun_reference import PronounReferenceCategory

__all__ = [
    'BaseCategory',
    'RedundancyCategory',
    'AwkwardPhrasingCategory',
    'PunctuationCategory',
    'GrammarCategory',
    'DialogueCategory',
    'CapitalisationCategory',
    'TenseConsistencyCategory',
    'SpellingCategory',
    'ParallelismConcisionCategory',
    'ArticleSpecificityCategory',
    'AgreementCategory',
    'AmbiguousPronounsCategory',
    'DanglingClauseCategory',
    'FragmentCategory',
    'RunOnCategory',
    'SplitLineCategory',
    'WordOrderCategory',
    'ContrastCategory',
    'ClarityCategory',
    'PrepositionCategory',
    'RegisterCategory',
    'RepetitionCategory',
    'CommaSpliceCategory',
    'CoordinationCategory',
    'EllipsisCategory',
    'HyphenationCategory',
    'MissingPeriodCategory',
    'NumberStyleCategory',
    'PossessiveCategory',
    'BrokenQuoteCategory',
    'CompoundsCategory',
    'PronounReferenceCategory',
]

