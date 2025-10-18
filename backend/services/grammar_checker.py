"""
Grammar checker for redundant phrases
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Callable, Tuple
from models.schemas import DocumentData, DocumentLine, GrammarIssue

# Import LLM enhancer for AI-powered improvements
try:
    from services.llm_enhancer import LLMEnhancer
    LLM_ENHANCER_AVAILABLE = True
except ImportError:
    LLM_ENHANCER_AVAILABLE = False
    LLMEnhancer = None
    print("ℹ️ LLM Enhancer not available (optional feature)")

# Import spaCy for linguistic analysis (passive voice detection)
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Model not installed, disable spaCy features
        nlp = None
        SPACY_AVAILABLE = False
        print("Warning: spaCy model 'en_core_web_sm' not found. Passive voice detection will be disabled.")
        print("To enable, run: python3 -m spacy download en_core_web_sm")
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    print("Warning: spaCy not installed. Passive voice detection will be disabled.")


def sanitize_text(text: str) -> str:
    """
    Cleans up text extracted from .docx before analysis.
    - Removes control characters and weird XML leftovers.
    - Normalizes whitespace and quotes.
    - Keeps punctuation and letters intact.
    """
    if not text:
        return ""

    # 1️⃣ Encode-decode to remove non-printable or invalid chars
    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    # 2️⃣ Remove weird zero-width spaces, control chars, etc.
    text = re.sub(r"[\u200B-\u200F\u202A-\u202E\u2060-\u206F]", "", text)

    # 3️⃣ Replace multiple newlines/tabs with a single space
    text = re.sub(r"[\r\n\t]+", " ", text)

    # 4️⃣ Collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 5️⃣ Fix spaced contractions (e.g., "It 's" → "It's")
    # Handle common contractions that might have spaces before apostrophes
    spaced_contraction_patterns = [
        (r"\b([Ii]t)\s+('s)\b", r"\1\2"),
        (r"\b([Hh]e)\s+('s)\b", r"\1\2"),
        (r"\b([Ss]he)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]e)\s+('re)\b", r"\1\2"),
        (r"\b([Tt]hey)\s+('re)\b", r"\1\2"),
        (r"\b([Yy]ou)\s+('re)\b", r"\1\2"),
        (r"\b([Ii])\s+('m)\b", r"\1\2"),
        (r"\b([Ii])\s+('ve)\b", r"\1\2"),
        (r"\b([Ii])\s+('ll)\b", r"\1\2"),
        (r"\b([Ii])\s+('d)\b", r"\1\2"),
        (r"\b([Ww]e)\s+('ve)\b", r"\1\2"),
        (r"\b([Ww]e)\s+('ll)\b", r"\1\2"),
        (r"\b([Ww]e)\s+('d)\b", r"\1\2"),
        (r"\b([Tt]hey)\s+('ve)\b", r"\1\2"),
        (r"\b([Tt]hey)\s+('ll)\b", r"\1\2"),
        (r"\b([Tt]hey)\s+('d)\b", r"\1\2"),
        (r"\b([Yy]ou)\s+('ve)\b", r"\1\2"),
        (r"\b([Yy]ou)\s+('ll)\b", r"\1\2"),
        (r"\b([Yy]ou)\s+('d)\b", r"\1\2"),
        (r"\b([Hh]e)\s+('ll)\b", r"\1\2"),
        (r"\b([Hh]e)\s+('d)\b", r"\1\2"),
        (r"\b([Ss]he)\s+('ll)\b", r"\1\2"),
        (r"\b([Ss]he)\s+('d)\b", r"\1\2"),
        (r"\b([Ii]t)\s+('ll)\b", r"\1\2"),
        (r"\b([Ii]t)\s+('d)\b", r"\1\2"),
        (r"\b([Tt]his)\s+('s)\b", r"\1\2"),
        (r"\b([Tt]hat)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]hat)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]ho)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]here)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]hen)\s+('s)\b", r"\1\2"),
        (r"\b([Ww]hy)\s+('s)\b", r"\1\2"),
        (r"\b([Hh]ow)\s+('s)\b", r"\1\2"),
        (r"\b([Tt]here)\s+('s)\b", r"\1\2"),
        (r"\b([Hh]ere)\s+('s)\b", r"\1\2"),
    ]
    
    for pattern, replacement in spaced_contraction_patterns:
        text = re.sub(pattern, replacement, text)
    
    # 5️⃣.5 Fix hyphenated contractions (e.g., "lunch-wasn't" should not be split)
    # This prevents LanguageTool from flagging "lunch-wasn" as a spelling error
    hyphenated_contraction_patterns = [
        (r"\b(\w+)-wasn't\b", r"\1-wasn't"),
        (r"\b(\w+)-isn't\b", r"\1-isn't"),
        (r"\b(\w+)-aren't\b", r"\1-aren't"),
        (r"\b(\w+)-weren't\b", r"\1-weren't"),
        (r"\b(\w+)-haven't\b", r"\1-haven't"),
        (r"\b(\w+)-hasn't\b", r"\1-hasn't"),
        (r"\b(\w+)-hadn't\b", r"\1-hadn't"),
        (r"\b(\w+)-won't\b", r"\1-won't"),
        (r"\b(\w+)-don't\b", r"\1-don't"),
        (r"\b(\w+)-doesn't\b", r"\1-doesn't"),
        (r"\b(\w+)-didn't\b", r"\1-didn't"),
        (r"\b(\w+)-can't\b", r"\1-can't"),
        (r"\b(\w+)-couldn't\b", r"\1-couldn't"),
        (r"\b(\w+)-shouldn't\b", r"\1-shouldn't"),
        (r"\b(\w+)-wouldn't\b", r"\1-wouldn't"),
    ]
    
    for pattern, replacement in hyphenated_contraction_patterns:
        text = re.sub(pattern, replacement, text)

    # 6️⃣ Normalize curly quotes and dashes
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace("–", "-").replace("—", "-")

    return text


class GrammarChecker:
    """Grammar checker focusing on redundant phrases, awkward phrasing, punctuation, grammar, spelling, and parallelism/concision
    
    Note: Parallelism/Concision is an EXPERIMENTAL feature and may produce false positives
    """
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        
        # Initialize LLM enhancer (optional feature)
        if LLM_ENHANCER_AVAILABLE:
            self.llm_enhancer = LLMEnhancer()
        else:
            self.llm_enhancer = None
        
        # Grammar issue categories
        self.categories = {
            'redundancy': 'Redundant Phrases',
            'awkward_phrasing': 'Awkward Phrasing',
            'punctuation': 'Punctuation',
            'grammar': 'Grammar',
            'dialogue': 'Dialogue',
            'capitalisation': 'Capitalisation',
            'tense_consistency': 'Tense Consistency',
            'spelling': 'Spelling',
            'parallelism_concision': 'Parallelism/Concision (Experimental)',  # EXPERIMENTAL: May produce false positives
            'article_specificity': 'Article/Specificity',
            'agreement': 'Agreement',  # Subject–verb agreement (9 conservative patterns to avoid false positives)
            'ambiguous_pronouns': 'Ambiguous Pronouns',  # Pronoun reference clarity (7 patterns for common ambiguity issues)
        }
        
        # Common redundant phrases and their corrections
        self.redundant_phrases = {
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
            'added bonus': 'bonus',
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
            'join together': 'join',
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
        
        # Awkward phrasing and their better alternatives
        self.awkward_phrases = {
            'a lot of': 'many',
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
        
        # Punctuation patterns: (pattern, description, fix_function)
        # Store as list of tuples for ordered checking
        self.punctuation_patterns = [
            # Multiple spaces
            (r'\s{2,}', 'Multiple consecutive spaces', lambda m, t: ' '),
            # Space before punctuation (except opening quotes/brackets)
            (r'\s+([,;:!?])', 'Extra space before punctuation', lambda m, t: m.group(1)),
            # Missing space after punctuation (except in numbers, ellipsis, or URLs)
            (r'([,;:!?])([a-zA-Z])', 'Missing space after punctuation', lambda m, t: f"{m.group(1)} {m.group(2)}"),
            # Multiple punctuation marks - only flag non-ellipsis cases
            # Skip ellipsis (three or more dots), as it's valid punctuation
            (r'([,;:]){2,}', 'Multiple punctuation marks', lambda m, t: m.group(1)),
            # Space after opening bracket/quote
            (r'([\(\[\{])\s+', 'Extra space after opening bracket', lambda m, t: m.group(1)),
            # Space before closing bracket/quote
            (r'\s+([\)\]\}])', 'Extra space before closing bracket', lambda m, t: m.group(1)),
            # Missing comma in lists (simple pattern: word, word and word -> word, word, and word)
            # This is complex and might have false positives, so we'll skip it for now
            # Comma before 'and' in simple lists is optional and depends on style guide
        ]
        
        # Grammar patterns: (pattern, description, fix_function)
        self.grammar_patterns = [
            # Double negatives
            (r"\b(don't|doesn't|didn't|won't|wouldn't|shouldn't|can't|couldn't)\s+(no|nothing|nobody|nowhere|never|none)\b", 
             "Double negative", 
             lambda m, t: m.group(1).replace("n't", "") + " any" if "nothing" not in m.group(2) else m.group(1).replace("n't", "") + " anything"),
            
            # Article checking removed - too many false positives due to sound vs letter complexity
            # (e.g., "a useful" is correct because "useful" sounds like "yoo-sful", not a vowel sound)
            # (e.g., "an hour" is correct because "hour" has a silent h, vowel sound)
            
            # Subject-verb agreement removed - too many false positives due to complex grammar rules
            # (e.g., "would it feel" is correct - modals take base form)
            # (e.g., "did it go" is correct - auxiliaries take base form)
            # (e.g., "made it feel" is correct - causative verbs take bare infinitive)
            # (e.g., "treat it like" is correct - "like" is a preposition, not a verb)
            
            # Common verb form errors
            (r'\bshould\s+of\b', "Incorrect verb form: 'should of' should be 'should have'", lambda m, t: "should have"),
            (r'\bcould\s+of\b', "Incorrect verb form: 'could of' should be 'could have'", lambda m, t: "could have"),
            (r'\bwould\s+of\b', "Incorrect verb form: 'would of' should be 'would have'", lambda m, t: "would have"),
            (r'\bmust\s+of\b', "Incorrect verb form: 'must of' should be 'must have'", lambda m, t: "must have"),
            (r'\bmight\s+of\b', "Incorrect verb form: 'might of' should be 'might have'", lambda m, t: "might have"),
            
            # Their/there/they're confusion
            (r'\bthere\s+(are|is)\s+\w+\s+(car|house|book|dog|cat|friend|student|teacher|parent|child)', 
             "Possible confusion: check if 'their' (possessive) is more appropriate than 'there' (location)", 
             lambda m, t: f"their {m.group(1)} {m.group(2)}"),
            
            # Your/you're confusion
            (r'\byour\s+(are|going|not|very|really|always|never)\b', 
             "Incorrect usage: 'your' should be 'you're' (you are)", 
             lambda m, t: f"you're {m.group(1)}"),
            
            # Its/it's confusion  
            (r"\bits\s+(a|an|the|very|really|always|going|been)\b",
             "Incorrect usage: 'its' should be 'it's' (it is/has)",
             lambda m, t: f"it's {m.group(1)}"),
            
            # Then/than confusion
            (r'\b(better|worse|more|less|greater|smaller|faster|slower|higher|lower)\s+then\b',
             "Incorrect usage: 'then' should be 'than' (for comparisons)",
             lambda m, t: f"{m.group(1)} than"),
            
            # Lose/loose confusion
            (r'\blose\s+fit\b', "Incorrect usage: 'lose fit' should be 'loose fit'", lambda m, t: "loose fit"),
            (r'\bI\s+loose\b', "Incorrect usage: 'I loose' should be 'I lose'", lambda m, t: "I lose"),
            
            # Affect/effect basic patterns
            (r'\beffect\s+(me|you|him|her|us|them|someone|people)\b',
             "Incorrect usage: 'effect' should be 'affect' (as a verb)",
             lambda m, t: f"affect {m.group(1)}"),
        ]
        
        # Agreement patterns: (pattern, description, fix_function)
        # Subject-verb agreement - only safe patterns to avoid false positives
        self.agreement_patterns = [
            # Basic plural subjects with singular verbs (obvious errors)
            (r'\b(they|we|you)\s+(is|was|has)\b',
             "Subject-verb agreement error: plural subject needs plural verb",
             lambda m, t: f"{m.group(1)} {'are' if m.group(2) == 'is' else 'were' if m.group(2) == 'was' else 'have'}"),
            
            # Singular third-person pronouns with plural verbs (obvious errors)
            (r'\b(he|she|it)\s+(are|were|have)\b',
             "Subject-verb agreement error: singular subject needs singular verb",
             lambda m, t: f"{m.group(1)} {'is' if m.group(2) == 'are' else 'was' if m.group(2) == 'were' else 'has'}"),
            
            # "I" with wrong verb forms
            (r'\bI\s+(is|are|was|were)\b',
             "Subject-verb agreement error with 'I'",
             lambda m, t: f"I {'am' if m.group(1) in ['is', 'are'] else 'was'}"),
            
            # Common errors: "he don't" / "she don't" / "it don't"
            (r'\b(he|she|it)\s+don\'t\b',
             "Subject-verb agreement error: singular subject should use 'doesn't'",
             lambda m, t: f"{m.group(1)} doesn't"),
            
            # "They was" / "We was" / "You was" (common error)
            (r'\b(they|we|you)\s+was\b',
             "Subject-verb agreement error: plural subject needs 'were'",
             lambda m, t: f"{m.group(1)} were"),
            
            # "He/She/It have" (without modals)
            (r'\b(he|she|it)\s+have\s+(a|an|the|to|been)\b',
             "Subject-verb agreement error: singular subject needs 'has'",
             lambda m, t: f"{m.group(1)} has {m.group(2)}"),
            
            # Common plural nouns with singular verbs (safe cases only)
            (r'\b(people|children|men|women|police)\s+(is|was|has)\b',
             "Subject-verb agreement error: plural noun needs plural verb",
             lambda m, t: f"{m.group(1)} {'are' if m.group(2) == 'is' else 'were' if m.group(2) == 'was' else 'have'}"),
            
            # "There is" + plural noun (common error)
            (r'\bthere\s+is\s+(many|several|multiple|some|few|two|three|four|five)\b',
             "Subject-verb agreement error: use 'there are' with plural quantities",
             lambda m, t: f"there are {m.group(1)}"),
            
            # Present tense third person singular missing 's'
            # Only safe, unambiguous verbs to avoid modal/auxiliary false positives
            (r'\b(he|she|it)\s+(walk|talk|run|eat|sleep|work|live|play|need|want|like|love|hate|think|know|feel)\s+(to|the|a|an|in|on|at|with|for|very|really|always|never|often|sometimes)\b',
             "Subject-verb agreement error: third person singular needs verb + 's'",
             lambda m, t: f"{m.group(1)} {m.group(2)}s {m.group(3)}"),
        ]
        
        # Ambiguous pronoun patterns: (pattern, description, fix_function)
        # Pronoun reference clarity - only flag obvious ambiguity issues
        self.ambiguous_pronoun_patterns = [
            # Vague "it" at sentence start without clear referent
            # Only flag when "it" doesn't refer to weather, time, or distance (common idiomatic uses)
            (r'^(It|it)\s+(seems|appears|looks|sounds|feels)\s+(like|that|as if)\b',
             "Vague pronoun: 'It' may be unclear - consider specifying what 'it' refers to",
             None),
            
            # Multiple "it" pronouns in same sentence (potential ambiguity)
            (r'\bit\b.*\bit\b.*\bit\b',
             "Pronoun clarity: Multiple uses of 'it' in one sentence may cause confusion - consider using specific nouns",
             None),
            
            # "This" or "That" at start of sentence without noun (vague reference)
            (r'^(This|this|That|that)\s+(is|was|would|could|should|may|might|can|will)\b',
             "Vague pronoun: Consider adding a noun after 'this/that' for clarity (e.g., 'This approach is...')",
             None),
            
            # "These" or "Those" used vaguely at sentence start
            (r'^(These|these|Those|those)\s+(are|were|would|could|should|may|might|can|will)\b',
             "Vague pronoun: Consider adding a noun after 'these/those' for clarity (e.g., 'These methods are...')",
             None),
            
            # "They" without clear plural antecedent nearby (conservative - only flag certain patterns)
            (r'^(They|they)\s+(say|said|think|thought|believe|believed|claim|claimed)\b',
             "Ambiguous pronoun: Who does 'they' refer to? Consider being more specific",
             None),
            
            # Using "one" repeatedly (can become unclear)
            (r'\bone\b.*\bone\b.*\bone\b',
             "Pronoun clarity: Multiple uses of 'one' may be confusing - consider rephrasing or using specific nouns",
             None),
            
            # Unclear "which" after multiple nouns (potential ambiguity)
            (r'\b(and|or)\s+(\w+\s+)*\w+,\s*which\b',
             "Pronoun clarity: 'Which' may be ambiguous after multiple nouns - clarify what it refers to",
             None),
        ]
        
        # Dialogue patterns: (pattern, description, fix_function, category)
        self.dialogue_patterns = [
            # Missing comma before closing quote with dialogue tag
            (r'([a-zA-Z])"(\s+)(said|asked|replied|answered|whispered|shouted|exclaimed|muttered|added|continued|explained|insisted|suggested|declared|announced|complained|admitted|agreed|disagreed|interrupted|protested)',
             "Missing comma before closing quotation mark in dialogue",
             lambda m, t: f'{m.group(1)}," {m.group(3)}'),
            
            # Comma after closing quote with dialogue tag should be inside
            (r'"(\s*),(\s+)(said|asked|replied|answered|whispered|shouted|exclaimed|muttered|added|continued|explained|insisted|suggested|declared|announced|complained|admitted|agreed|disagreed|interrupted|protested)',
             "Comma should be inside quotation marks before dialogue tag",
             lambda m, t: f'," {m.group(3)}'),
            
            # Dialogue tag capitalization - should be lowercase after quote
            (r'"\s+([A-Z])(said|aid)\b',
             "Dialogue tag should be lowercase after quotation mark",
             lambda m, t: f'" {m.group(1).lower()}{m.group(2)}'),
            
            # Basic dialogue pattern - quotes followed by dialogue tags
            (r'"([^"]+)"\s+(said|asked|replied|answered|whispered|shouted|exclaimed|muttered|added|continued|explained|insisted|suggested|declared|announced|complained|admitted|agreed|disagreed|interrupted|protested)',
             "Dialogue formatting looks correct",
             lambda m, t: m.group(0)),  # No change needed, just flag for review
            
            # Missing comma in dialogue with tag
            (r'([a-zA-Z])"(\s+)(and|but|then|so)',
             "Consider adding comma before dialogue tag or rephrasing",
             lambda m, t: f'{m.group(1)}," {m.group(3)}'),
        ]
        
        # Capitalisation patterns: (pattern, description, fix_function)
        self.capitalisation_patterns = [
            # Sentence doesn't start with capital letter (after . ! ?)
            # But exclude ellipsis (...) as it's often a continuation and URLs
            # Negative lookbehind to exclude cases where period is part of ellipsis
            (r'(?<!\.)([.!?])\s+(?!https?://|www\.)([a-z])',
             "Sentence should start with a capital letter",
             lambda m, t: f'{m.group(1)} {m.group(2).upper()}'),
            
            # First word of text should be capitalized (but exclude URLs)
            (r'^(?!https?://|www\.)([a-z])',
             "Text should start with a capital letter",
             lambda m, t: m.group(1).upper()),
            
            # First word of text should be capitalized
            # This will be checked separately in the line checking logic
            
            # Days of the week not capitalized
            (r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
             "Days of the week should be capitalized",
             lambda m, t: m.group(1).capitalize()),
            
            # Months not capitalized (excluding May - handled separately)
            (r'\b(january|february|march|april|june|july|august|september|october|november|december)\b',
             "Months should be capitalized",
             lambda m, t: m.group(1).capitalize()),
            
            # May (the month) - only when in month context
            # Match "may" when preceded by: in, on, during, of, next, last, this, until, by, from, since
            # Or when followed by day numbers (1-31) or ordinals (1st, 2nd, etc.)
            (r'\b(in|on|during|of|next|last|this|until|by|from|since)\s+(may)\b',
             "Months should be capitalized",
             lambda m, t: f"{m.group(1)} {m.group(2).capitalize()}"),
            
            # May followed by day number
            (r'\b(may)\s+(\d{1,2}(st|nd|rd|th)?)\b',
             "Months should be capitalized",
             lambda m, t: f"{m.group(1).capitalize()} {m.group(2)}"),
            
            # Common proper nouns - countries (simplified list)
            (r'\b(america|england|france|germany|spain|italy|china|japan|india|canada|australia|mexico|brazil|russia)\b',
             "Country names should be capitalized",
             lambda m, t: m.group(1).capitalize()),
            
            # I should always be capitalized when used as pronoun
            (r'\b(i)\s+(am|was|will|would|should|could|can|have|had|do|did|think|feel|see|know|want|need|like|love|hate|believe)\b',
             "The pronoun 'I' should always be capitalized",
             lambda m, t: f"I {m.group(2)}"),
            
            # Common title case issues - titles/headings
            # Skip for now as it's context-dependent
        ]
        
        # Common abbreviations that end with period but don't end a sentence
        self.abbreviations = {
            'a.m.', 'p.m.', 'e.g.', 'i.e.', 'dr.', 'mr.', 'mrs.', 'ms.',
            'sr.', 'jr.', 'prof.', 'vs.', 'etc.', 'st.', 'no.', 'inc.',
            'corp.', 'ltd.', 'co.', 'ave.', 'blvd.', 'dept.', 'est.',
            'approx.', 'viz.', 'cf.', 'n.b.', 'p.s.', 'a.k.a.',
            'u.s.', 'u.k.', 'u.n.', 'u.s.a.', 'ph.d.', 'b.a.', 'm.a.',
            'b.s.', 'm.s.', 'd.c.', 'ft.', 'in.', 'lb.', 'oz.', 'vol.'
        }
        
        # Common irregular verbs for tense consistency checking
        # Format: (present, past, past_participle)
        self.irregular_verbs = {
            'am': ('am', 'was', 'been'),
            'is': ('is', 'was', 'been'),
            'are': ('are', 'were', 'been'),
            'go': ('go', 'went', 'gone'),
            'went': ('go', 'went', 'gone'),
            'do': ('do', 'did', 'done'),
            'did': ('do', 'did', 'done'),
            'have': ('have', 'had', 'had'),
            'had': ('have', 'had', 'had'),
            'say': ('say', 'said', 'said'),
            'said': ('say', 'said', 'said'),
            'get': ('get', 'got', 'gotten'),
            'got': ('get', 'got', 'gotten'),
            'make': ('make', 'made', 'made'),
            'made': ('make', 'made', 'made'),
            'see': ('see', 'saw', 'seen'),
            'saw': ('see', 'saw', 'seen'),
            'come': ('come', 'came', 'come'),
            'came': ('come', 'came', 'come'),
            'take': ('take', 'took', 'taken'),
            'took': ('take', 'took', 'taken'),
            'know': ('know', 'knew', 'known'),
            'knew': ('know', 'knew', 'known'),
            'think': ('think', 'thought', 'thought'),
            'thought': ('think', 'thought', 'thought'),
            'give': ('give', 'gave', 'given'),
            'gave': ('give', 'gave', 'given'),
            'find': ('find', 'found', 'found'),
            'found': ('find', 'found', 'found'),
            'tell': ('tell', 'told', 'told'),
            'told': ('tell', 'told', 'told'),
            'become': ('become', 'became', 'become'),
            'became': ('become', 'became', 'become'),
            'leave': ('leave', 'left', 'left'),
            'left': ('leave', 'left', 'left'),
            'feel': ('feel', 'felt', 'felt'),
            'felt': ('feel', 'felt', 'felt'),
            'bring': ('bring', 'brought', 'brought'),
            'brought': ('bring', 'brought', 'brought'),
            'begin': ('begin', 'began', 'begun'),
            'began': ('begin', 'began', 'begun'),
            'keep': ('keep', 'kept', 'kept'),
            'kept': ('keep', 'kept', 'kept'),
            'hold': ('hold', 'held', 'held'),
            'held': ('hold', 'held', 'held'),
            'write': ('write', 'wrote', 'written'),
            'wrote': ('write', 'wrote', 'written'),
            'stand': ('stand', 'stood', 'stood'),
            'stood': ('stand', 'stood', 'stood'),
            'hear': ('hear', 'heard', 'heard'),
            'heard': ('hear', 'heard', 'heard'),
            'let': ('let', 'let', 'let'),
            'mean': ('mean', 'meant', 'meant'),
            'meant': ('mean', 'meant', 'meant'),
            'set': ('set', 'set', 'set'),
            'meet': ('meet', 'met', 'met'),
            'met': ('meet', 'met', 'met'),
            'run': ('run', 'ran', 'run'),
            'ran': ('run', 'ran', 'run'),
            'pay': ('pay', 'paid', 'paid'),
            'paid': ('pay', 'paid', 'paid'),
            'sit': ('sit', 'sat', 'sat'),
            'sat': ('sit', 'sat', 'sat'),
            'speak': ('speak', 'spoke', 'spoken'),
            'spoke': ('speak', 'spoke', 'spoken'),
            'lie': ('lie', 'lay', 'lain'),
            'lay': ('lay', 'laid', 'laid'),
            'laid': ('lay', 'laid', 'laid'),
            'lead': ('lead', 'led', 'led'),
            'led': ('lead', 'led', 'led'),
            'read': ('read', 'read', 'read'),
            'grow': ('grow', 'grew', 'grown'),
            'grew': ('grow', 'grew', 'grown'),
            'lose': ('lose', 'lost', 'lost'),
            'lost': ('lose', 'lost', 'lost'),
            'fall': ('fall', 'fell', 'fallen'),
            'fell': ('fall', 'fell', 'fallen'),
            'send': ('send', 'sent', 'sent'),
            'sent': ('send', 'sent', 'sent'),
            'build': ('build', 'built', 'built'),
            'built': ('build', 'built', 'built'),
            'understand': ('understand', 'understood', 'understood'),
            'understood': ('understand', 'understood', 'understood'),
            'draw': ('draw', 'drew', 'drawn'),
            'drew': ('draw', 'drew', 'drawn'),
            'break': ('break', 'broke', 'broken'),
            'broke': ('break', 'broke', 'broken'),
            'spend': ('spend', 'spent', 'spent'),
            'spent': ('spend', 'spent', 'spent'),
            'cut': ('cut', 'cut', 'cut'),
            'rise': ('rise', 'rose', 'risen'),
            'rose': ('rise', 'rose', 'risen'),
            'drive': ('drive', 'drove', 'driven'),
            'drove': ('drive', 'drove', 'driven'),
            'buy': ('buy', 'bought', 'bought'),
            'bought': ('buy', 'bought', 'bought'),
            'wear': ('wear', 'wore', 'worn'),
            'wore': ('wear', 'wore', 'worn'),
            'choose': ('choose', 'chose', 'chosen'),
            'chose': ('choose', 'chose', 'chosen'),
            'seek': ('seek', 'sought', 'sought'),
            'sought': ('seek', 'sought', 'sought'),
            'throw': ('throw', 'threw', 'thrown'),
            'threw': ('throw', 'threw', 'thrown'),
            'catch': ('catch', 'caught', 'caught'),
            'caught': ('catch', 'caught', 'caught'),
            'deal': ('deal', 'dealt', 'dealt'),
            'dealt': ('deal', 'dealt', 'dealt'),
            'win': ('win', 'won', 'won'),
            'won': ('win', 'won', 'won'),
            'forget': ('forget', 'forgot', 'forgotten'),
            'forgot': ('forget', 'forgot', 'forgotten'),
            'shake': ('shake', 'shook', 'shaken'),
            'shook': ('shake', 'shook', 'shaken'),
            'hang': ('hang', 'hung', 'hung'),
            'hung': ('hang', 'hung', 'hung'),
            'strike': ('strike', 'struck', 'struck'),
            'struck': ('strike', 'struck', 'struck'),
            'ride': ('ride', 'rode', 'ridden'),
            'rode': ('ride', 'rode', 'ridden'),
            'sing': ('sing', 'sang', 'sung'),
            'sang': ('sing', 'sang', 'sung'),
            'swim': ('swim', 'swam', 'swum'),
            'swam': ('swim', 'swam', 'swum'),
        }
        
        # Tense consistency patterns
        # These patterns detect common tense shifts within a sentence
        self.tense_patterns = [
            # Present tense followed by past tense in same sentence (without time indicators)
            # e.g., "I walk to the store and bought milk" -> should be "I walked to the store and bought milk"
            (r'\b(walks?|runs?|goes?|comes?|takes?|makes?|gets?|says?|knows?|thinks?)\s+(to|and|but|then)\s+\w+\s+(walked|ran|went|came|took|made|got|said|knew|thought)\b',
             "Inconsistent tense: mixing present and past tense",
             lambda m, t: None),  # This is complex, we'll flag it but not auto-fix
            
            # Past tense followed by present tense (e.g., "I walked to the store and buy milk")
            (r'\b(walked|ran|went|came|took|made|got|said|knew|thought)\s+(to|and|but|then)\s+\w+\s+(walk|run|go|come|take|make|get|say|know|think)s?\b',
             "Inconsistent tense: mixing past and present tense",
             lambda m, t: None),
            
            # Common irregular verb mistakes
            (r'\b(buyed|buyed)\b',
             "Incorrect verb form: 'buyed' should be 'bought'",
             lambda m, t: "bought"),
            
            (r'\b(goed|goed)\b',
             "Incorrect verb form: 'goed' should be 'went'",
             lambda m, t: "went"),
            
            (r'\b(drinked|drinked)\b',
             "Incorrect verb form: 'drinked' should be 'drank'",
             lambda m, t: "drank"),
            
            (r'\b(eated|eated)\b',
             "Incorrect verb form: 'eated' should be 'ate'",
             lambda m, t: "ate"),
            
            (r'\b(sleeped|sleeped)\b',
             "Incorrect verb form: 'sleeped' should be 'slept'",
             lambda m, t: "slept"),
            
            (r'\b(keeped|keeped)\b',
             "Incorrect verb form: 'keeped' should be 'kept'",
             lambda m, t: "kept"),
        ]
        
        # Common spelling mistakes: (incorrect, correct)
        self.common_misspellings = {
            'recieve': 'receive',
            'recieved': 'received',
            'occured': 'occurred',
            'occuring': 'occurring',
            'seperate': 'separate',
            'seperated': 'separated',
            'definately': 'definitely',
            'definetly': 'definitely',
            'accomodate': 'accommodate',
            'acommodate': 'accommodate',
            'acheive': 'achieve',
            'acheived': 'achieved',
            'beleive': 'believe',
            'beleived': 'believed',
            'concious': 'conscious',
            'consciense': 'conscience',
            'embarass': 'embarrass',
            'embarassed': 'embarrassed',
            'existance': 'existence',
            'goverment': 'government',
            'grammer': 'grammar',
            'harrass': 'harass',
            'harrassment': 'harassment',
            'independant': 'independent',
            'judgement': 'judgment',
            'liason': 'liaison',
            'maintainance': 'maintenance',
            'millenium': 'millennium',
            'mispell': 'misspell',
            'mispelled': 'misspelled',
            'neccessary': 'necessary',
            'occassion': 'occasion',
            'occassional': 'occasional',
            'occured': 'occurred',
            'occurence': 'occurrence',
            'persue': 'pursue',
            'persuit': 'pursuit',
            'posession': 'possession',
            'prefered': 'preferred',
            'prefering': 'preferring',
            'priviledge': 'privilege',
            'pronounciation': 'pronunciation',
            'publically': 'publicly',
            'reccomend': 'recommend',
            'recomend': 'recommend',
            'refered': 'referred',
            'refering': 'referring',
            'relevent': 'relevant',
            'resistence': 'resistance',
            'rythm': 'rhythm',
            'succesful': 'successful',
            'sucess': 'success',
            'supercede': 'supersede',
            'suprise': 'surprise',
            'suprised': 'surprised',
            'tommorow': 'tomorrow',
            'truely': 'truly',
            'untill': 'until',
            'usefull': 'useful',
            'wich': 'which',
            'wierd': 'weird',
            'writting': 'writing',
            'writen': 'written',
            'begining': 'beginning',
            'buyed': 'bought',
            'goed': 'went',
            'drinked': 'drank',
            'eated': 'ate',
            'sleeped': 'slept',
            'keeped': 'kept',
            'comming': 'coming',
            'desparate': 'desperate',
            'enviroment': 'environment',
            'facinating': 'fascinating',
            'foriegn': 'foreign',
            'fourty': 'forty',
            'freind': 'friend',
            'heigth': 'height',
            'heros': 'heroes',
            'imediate': 'immediate',
            'immediatly': 'immediately',
            'incidently': 'incidentally',
            'intresting': 'interesting',
            'knowlege': 'knowledge',
            'liesure': 'leisure',
            'lightening': 'lightning',
            'noticable': 'noticeable',
            'occassionally': 'occasionally',
            'occured': 'occurred',
            'openning': 'opening',
            'oppurtunity': 'opportunity',
            'paralell': 'parallel',
            'parlament': 'parliament',
            'peice': 'piece',
            'perseverence': 'perseverance',
            'personell': 'personnel',
            'potatos': 'potatoes',
            'preceeding': 'preceding',
            'questionaire': 'questionnaire',
            'reccomendation': 'recommendation',
            'rember': 'remember',
            'remeber': 'remember',
            'responsability': 'responsibility',
            'seperately': 'separately',
            'sieze': 'seize',
            'similiar': 'similar',
            'succede': 'succeed',
            'tomatos': 'tomatoes',
            'tounge': 'tongue',
            'transfered': 'transferred',
            'truley': 'truly',
            'twelvth': 'twelfth',
            'unfortunatly': 'unfortunately',
            'useable': 'usable',
            'visable': 'visible',
            'wether': 'whether',
            'whereever': 'wherever',
        }
        
        # Parallelism/Concision patterns: (pattern, description, fix_function or None)
        # These patterns detect issues with parallel structure and verbosity
        self.parallelism_concision_patterns = [
            # Wordy phrases that can be made more concise
            (r'\bat the present moment\b', "Wordy: 'at the present moment' can be shortened to 'now'", lambda m, t: "now"),
            (r'\bin the event of\b', "Wordy: 'in the event of' can be shortened to 'if'", lambda m, t: "if"),
            (r'\bdue to the fact that\b', "Wordy: 'due to the fact that' can be shortened to 'because'", lambda m, t: "because"),
            (r'\bin spite of the fact that\b', "Wordy: 'in spite of the fact that' can be shortened to 'although'", lambda m, t: "although"),
            (r'\buntil such time as\b', "Wordy: 'until such time as' can be shortened to 'until'", lambda m, t: "until"),
            (r'\bfor the purpose of\b', "Wordy: 'for the purpose of' can be shortened to 'to' or 'for'", lambda m, t: "to"),
            (r'\bin order to\b', "Wordy: 'in order to' can be shortened to 'to'", lambda m, t: "to"),
            (r'\bby means of\b', "Wordy: 'by means of' can be shortened to 'by'", lambda m, t: "by"),
            (r'\bin the near future\b', "Wordy: 'in the near future' can be shortened to 'soon'", lambda m, t: "soon"),
            (r'\bat this point in time\b', "Wordy: 'at this point in time' can be shortened to 'now'", lambda m, t: "now"),
            (r'\bprior to\b', "Wordy: 'prior to' can be shortened to 'before'", lambda m, t: "before"),
            (r'\bsubsequent to\b', "Wordy: 'subsequent to' can be shortened to 'after'", lambda m, t: "after"),
            (r'\bin the amount of\b', "Wordy: 'in the amount of' can be shortened to 'for'", lambda m, t: "for"),
            (r'\bhas the ability to\b', "Wordy: 'has the ability to' can be shortened to 'can'", lambda m, t: "can"),
            (r'\bis able to\b', "Wordy: 'is able to' can be shortened to 'can'", lambda m, t: "can"),
            (r'\bmake a decision\b', "Wordy: 'make a decision' can be shortened to 'decide'", lambda m, t: "decide"),
            (r'\bgive consideration to\b', "Wordy: 'give consideration to' can be shortened to 'consider'", lambda m, t: "consider"),
            (r'\btake into consideration\b', "Wordy: 'take into consideration' can be shortened to 'consider'", lambda m, t: "consider"),
            (r'\bmake an assumption\b', "Wordy: 'make an assumption' can be shortened to 'assume'", lambda m, t: "assume"),
            (r'\bcame to a realization\b', "Wordy: 'came to a realization' can be shortened to 'realized'", lambda m, t: "realized"),
            (r'\breach a conclusion\b', "Wordy: 'reach a conclusion' can be shortened to 'conclude'", lambda m, t: "conclude"),
            (r'\bput an end to\b', "Wordy: 'put an end to' can be shortened to 'end'", lambda m, t: "end"),
            (r'\bmake reference to\b', "Wordy: 'make reference to' can be shortened to 'refer to'", lambda m, t: "refer to"),
            (r'\bfor the reason that\b', "Wordy: 'for the reason that' can be shortened to 'because'", lambda m, t: "because"),
            (r'\bin the process of\b', "Wordy: 'in the process of' can be shortened to 'during' or remove entirely", lambda m, t: "during"),
            (r'\bwith the exception of\b', "Wordy: 'with the exception of' can be shortened to 'except'", lambda m, t: "except"),
            (r'\bin close proximity to\b', "Wordy: 'in close proximity to' can be shortened to 'near'", lambda m, t: "near"),
            (r'\bon a regular basis\b', "Wordy: 'on a regular basis' can be shortened to 'regularly'", lambda m, t: "regularly"),
            (r'\bon a daily basis\b', "Wordy: 'on a daily basis' can be shortened to 'daily'", lambda m, t: "daily"),
            (r'\bat all times\b', "Wordy: 'at all times' can be shortened to 'always'", lambda m, t: "always"),
            (r'\bin many cases\b', "Wordy: 'in many cases' can be shortened to 'often'", lambda m, t: "often"),
            (r'\bin most cases\b', "Wordy: 'in most cases' can be shortened to 'usually'", lambda m, t: "usually"),
            (r'\bat the present time\b', "Wordy: 'at the present time' can be shortened to 'now'", lambda m, t: "now"),
            (r'\bdespite the fact that\b', "Wordy: 'despite the fact that' can be shortened to 'although'", lambda m, t: "although"),
            (r'\bthe majority of\b', "Wordy: 'the majority of' can be shortened to 'most'", lambda m, t: "most"),
            (r'\ba number of\b', "Wordy: 'a number of' can be shortened to 'several' or 'many'", lambda m, t: "several"),
            (r'\bin the event that\b', "Wordy: 'in the event that' can be shortened to 'if'", lambda m, t: "if"),
            (r'\bin view of the fact that\b', "Wordy: 'in view of the fact that' can be shortened to 'since'", lambda m, t: "since"),
            (r'\bon the basis of\b', "Wordy: 'on the basis of' can be shortened to 'based on'", lambda m, t: "based on"),
            (r'\bwith regard to\b', "Wordy: 'with regard to' can be shortened to 'regarding'", lambda m, t: "regarding"),
            (r'\bwith reference to\b', "Wordy: 'with reference to' can be shortened to 'about'", lambda m, t: "about"),
            
            # Nominalization patterns (verbs turned into nouns - less concise)
            (r'\bmake\s+an?\s+(analysis|assessment|evaluation|examination|investigation|determination)\s+of\b',
             "Nominalization: Consider using the verb form instead (e.g., 'analyze' instead of 'make an analysis of')",
             None),
            (r'\bconduct\s+an?\s+(analysis|assessment|evaluation|examination|investigation)\s+of\b',
             "Nominalization: Consider using the verb form instead (e.g., 'analyze' instead of 'conduct an analysis of')",
             None),
            (r'\bprovide\s+an?\s+(explanation|description|illustration)\s+of\b',
             "Nominalization: Consider using the verb form instead (e.g., 'explain' instead of 'provide an explanation of')",
             None),
            
            # Redundant intensifiers
            (r'\bvery\s+unique\b', "Redundant: 'unique' means one of a kind, so 'very unique' is redundant. Use 'unique' alone", lambda m, t: "unique"),
            (r'\bvery\s+perfect\b', "Redundant: 'perfect' is absolute, so 'very perfect' is redundant. Use 'perfect' alone", lambda m, t: "perfect"),
            (r'\bvery\s+essential\b', "Redundant: 'essential' is absolute, so 'very essential' is redundant. Use 'essential' alone", lambda m, t: "essential"),
            (r'\bvery\s+impossible\b', "Redundant: 'impossible' is absolute, so 'very impossible' is redundant. Use 'impossible' alone", lambda m, t: "impossible"),
            (r'\bcompletely\s+full\b', "Redundant: 'full' is absolute, so 'completely full' is redundant. Use 'full' alone", lambda m, t: "full"),
            (r'\bcompletely\s+empty\b', "Redundant: 'empty' is absolute, so 'completely empty' is redundant. Use 'empty' alone", lambda m, t: "empty"),
            (r'\bcompletely\s+destroyed\b', "Redundant: 'destroyed' is absolute, so 'completely destroyed' is redundant. Use 'destroyed' alone", lambda m, t: "destroyed"),
            (r'\babsolutely\s+certain\b', "Redundant: 'certain' is absolute, so 'absolutely certain' is redundant. Use 'certain' alone", lambda m, t: "certain"),
            (r'\bextremely\s+crucial\b', "Redundant: 'crucial' is already strong, so 'extremely crucial' is redundant. Use 'crucial' alone", lambda m, t: "crucial"),
        ]
        
        # Article/Specificity patterns: (pattern, description, fix_function or None)
        # These patterns detect issues with article usage (a, an, the) and specificity
        self.article_specificity_patterns = [
            # Incorrect article usage - only flag obvious errors (words that clearly start with vowel sounds)
            (r'\ba\s+(elephant|eagle|engine|example|evening|exercise|expert|eye|idea|island|office|umbrella|uncle|uniform|unique|unit|apple|orange|egg|arm|ear|ice|ocean|airplane)\b', "Article error: Use 'an' before words starting with a vowel sound", lambda m, t: f"an {m.group(1)}"),
            (r'\ban\s+(car|book|house|dog|cat|man|woman|child|student|teacher|doctor|lawyer|engineer|manager|director|company|school|hospital|restaurant|university|user|union|European|one|once)\b', "Article error: Use 'a' before words starting with a consonant sound", lambda m, t: f"a {m.group(1)}"),
            
            # Missing articles where needed (only flag obvious cases)
            (r'\bis\s+(university|hospital|hour|honor|honest|herb)\s+(in|at|for|with|to)', "Missing article: Add 'a' or 'an' before the noun", lambda m, t: f"is a {m.group(1)} {m.group(2)}"),
            (r'\bis\s+(hour|honor|honest|herb)\s+(in|at|for|with|to)', "Missing article: Add 'an' before words starting with 'h' but pronounced with silent 'h'", lambda m, t: f"is an {m.group(1)} {m.group(2)}"),
            
            # Unnecessary articles
            (r'\bthe\s+(both|all|each|every|some|any|no)\s+', "Unnecessary article: Remove 'the' before quantifiers", lambda m, t: f"{m.group(1)} "),
            (r'\bthe\s+(this|that|these|those)\s+', "Unnecessary article: Remove 'the' before demonstratives", lambda m, t: f"{m.group(1)} "),
            
            # Specificity issues - vague language
            (r'\b(a\s+)?(thing|stuff|item|object|element|factor|aspect)\b', "Vague language: Be more specific about what you're referring to", None),
            (r'\b(something|anything|nothing|everything)\b', "Vague language: Consider being more specific about what you're referring to", None),
            (r'\b(good|bad|nice|great|awesome|cool|terrible|horrible)\b', "Vague language: Use more specific descriptive words", None),
            (r'\b(lots?\s+of|a\s+lot\s+of|tons?\s+of|plenty\s+of)\b', "Vague quantifier: Use more specific numbers or quantities when possible", None),
            
            # Missing specificity in comparisons
            (r'\b(more|less|better|worse|bigger|smaller|faster|slower)\s+than\s+(before|previously|earlier)\b', "Vague comparison: Specify what you're comparing to", None),
            
            # Overuse of "the" when indefinite is more appropriate (be more specific)
            (r'\bthe\s+(book|car|house|person|student|employee|manager|director)\s+(is|was|will be)\s+(good|bad|nice|great|responsible|important)\b', "Consider if 'a/an' would be more appropriate than 'the' for general reference", None),
        ]
        
        # Sentence starters that often indicate intentional passive voice
        self.intentional_passive_starters = [
            'it was', 'it is', 'it has been', 'it had been', 'it will be',
            'there was', 'there is', 'there has been', 'there had been', 'there will be'
        ]
        
        # Words that suggest technical/academic context where passive voice is common
        self.passive_voice_context_words = [
            'framework', 'method', 'methodology', 'algorithm', 'system',
            'approach', 'technique', 'process', 'procedure', 'experiment',
            'study', 'research', 'analysis', 'model', 'protocol'
        ]
    
    def _detect_passive_voice_spacy(self, text: str, line_number: int) -> List[GrammarIssue]:
        """
        Detect true passive voice using spaCy dependency parsing.
        
        This method uses linguistic analysis to identify actual passive voice constructions
        (e.g., "was written", "were marketed") and skips false positives like linking verbs
        with adjectives (e.g., "is nuanced", "is layered").
        
        Args:
            text: The text to analyze
            line_number: The line number for issue reporting
            
        Returns:
            List of GrammarIssue objects for detected passive voice
        """
        if not SPACY_AVAILABLE or nlp is None:
            return []
        
        issues = []
        
        try:
            doc = nlp(text)
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                sentence_lower = sentence_text.lower()
                
                # Check if sentence starts with intentional passive patterns
                skip_sentence = False
                for starter in self.intentional_passive_starters:
                    if sentence_lower.startswith(starter):
                        skip_sentence = True
                        break
                
                if skip_sentence:
                    continue
                
                # Check if sentence contains technical/academic context words
                sentence_words = set(sentence_lower.split())
                if any(word in sentence_words for word in self.passive_voice_context_words):
                    continue
                
                # Skip short sentences (< 8 words) which might be stylistic
                if len(sentence_text.split()) < 8:
                    continue
                
                # Look for passive voice using dependency parsing
                for token in sent:
                    # Look for passive auxiliary (auxpass): was, were, is, are, been, being
                    if token.dep_ == "auxpass":
                        verb = token.head
                        passive_phrase = f"{token.text} {verb.text}"
                        
                        # Check if there's a clear agent (by X)
                        has_agent = False
                        agent_text = None
                        for child in verb.children:
                            if child.dep_ == "agent":  # "by" phrase
                                has_agent = True
                                agent_text = child.text
                                break
                        
                        # Skip if there's a clear agent (intentional passive)
                        if has_agent:
                            continue
                        
                        # Generate dynamic fix suggestion based on the verb
                        verb_lemma = verb.lemma_
                        
                        if agent_text:
                            fix_suggestion = (
                                f"Rewrite as active voice (e.g., move '{agent_text}' to subject position: "
                                f"'{agent_text} {verb_lemma}s ...')"
                            )
                        else:
                            fix_suggestion = (
                                f"Rewrite using active voice (identify who performs the action of '{verb_lemma}' "
                                f"and make them the subject)"
                            )
                        
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=text,
                            problem=f"Passive voice detected: '{passive_phrase}' - Consider using active voice for clarity and directness",
                            fix=fix_suggestion,
                            category='parallelism_concision',
                            confidence=0.75,
                            corrected_sentence=None
                        )
                        
                        issues.append(issue)
        
        except Exception as e:
            # If spaCy processing fails, silently skip
            print(f"Warning: spaCy processing failed for line {line_number}: {e}")
            pass
        
        return issues
    
    def _is_abbreviation_before(self, text: str, match_start: int) -> bool:
        """
        Check if a period before the match position belongs to a known abbreviation or URL.
        
        Args:
            text: The full text content
            match_start: The starting position of the match
            
        Returns:
            True if the period is part of an abbreviation or URL, False otherwise
        """
        # Look back up to 50 characters to check for abbreviations
        look_back = 50
        start = max(0, match_start - look_back)
        context_before = text[start:match_start + 1].lower()
        
        # Look ahead up to 20 characters to check for URLs (in case period comes before URL)
        look_ahead = 20
        end = min(len(text), match_start + look_ahead)
        context_after = text[match_start:end].lower()
        
        # Check for URLs starting after the period (e.g., "2024. https://")
        url_patterns = ['http://', 'https://', 'www.']
        for pattern in url_patterns:
            if pattern in context_after:
                return True
        
        # Check for URLs in the context before (e.g., within ".com/ " or ".org/ ")
        url_domain_patterns = ['.com/', '.org/', '.edu/', '.gov/', '.net/', '.io/', '.co/']
        for pattern in url_domain_patterns:
            if pattern in context_before:
                return True
        
        # Check if any abbreviation appears just before the match
        for abbr in self.abbreviations:
            if context_before.endswith(abbr):
                return True
        
        return False
    
    async def check_document(
        self, 
        document_data: DocumentData, 
        progress_callback: Optional[Callable] = None,
        enabled_categories: Optional[List[str]] = None,
        use_llm_enhancement: bool = False
    ) -> Tuple[List[GrammarIssue], Dict[str, Any]]:
        """
        Check entire document for redundant phrases, awkward phrasing, punctuation, grammar, and spelling
        
        Strategy: Check at LINE level, scanning for predefined patterns of
        redundant phrases, awkward phrasing, punctuation errors, grammar mistakes, and spelling errors.
        Optionally enhance complex issues with LLM for better suggestions.
        
        Args:
            document_data: Parsed document data
            progress_callback: Optional callback for progress updates
                              Signature: async def callback(line_num: int, total_lines: int, issues_found: int)
            enabled_categories: Optional list of category names to check (e.g., ['redundancy', 'grammar'])
                              If None, all categories are checked
            use_llm_enhancement: Enable AI-powered enhancement of complex issues (costs ~$0.01-0.03 per MB)
            
        Returns:
            Tuple of (List of grammar issues found, enhancement metadata)
        """
        # Log enabled categories for debugging
        if enabled_categories is None:
            print(f"[GrammarChecker] Checking ALL categories (no filter specified)")
        else:
            print(f"[GrammarChecker] Checking ONLY these categories: {enabled_categories}")
        
        if use_llm_enhancement:
            print(f"[GrammarChecker] ✨ LLM enhancement ENABLED")
        
        all_issues = []
        total_lines = len(document_data.lines)
        
        for i, line in enumerate(document_data.lines, 1):
            # Skip empty lines
            if not line.content or not line.content.strip():
                continue
            
            # Sanitize the full line content
            full_line_content = sanitize_text(line.content)
            
            # Check the entire line first (with all sentences combined)
            # This handles cases where quotes span multiple sentences on the same line
            line_issues = await self._check_line_content(
                full_line_content,
                line.line_number,
                enabled_categories
            )
            
            all_issues.extend(line_issues)
            
            # Update progress with real-time line count and issues found
            if progress_callback:
                # Check if callback is async or sync
                import inspect
                if inspect.iscoroutinefunction(progress_callback):
                    await progress_callback(i, total_lines, len(all_issues))
                else:
                    # Legacy callback support (just progress percentage)
                    progress = int((i / total_lines) * 100)
                    progress_callback(progress)
        
        # Merge similar issues
        all_issues = self._merge_similar_issues(all_issues)
        
        # Enhancement metadata
        enhancement_metadata = {
            "llm_enabled": False,
            "issues_enhanced": 0,
            "cost": 0.0,
            "warning": None
        }
        
        # Optional: Enhance with LLM
        if use_llm_enhancement:
            if not all_issues:
                enhancement_metadata["warning"] = "No issues found to enhance"
                return all_issues, enhancement_metadata
            
            if not self.llm_enhancer:
                enhancement_metadata["warning"] = "AI enhancement unavailable: openai package not installed"
                print(f"⚠️ [GrammarChecker] LLM enhancement requested but LLMEnhancer not available")
                return all_issues, enhancement_metadata
            
            if not self.llm_enhancer.enabled:
                if not LLM_ENHANCER_AVAILABLE:
                    enhancement_metadata["warning"] = "AI enhancement unavailable: Install with 'pip install openai tiktoken'"
                else:
                    enhancement_metadata["warning"] = "AI enhancement unavailable: Check OPENAI_API_KEY in .env file"
                print(f"⚠️ [GrammarChecker] LLM enhancement requested but not enabled/configured")
                return all_issues, enhancement_metadata
            
            # LLM enhancer is available and enabled
            print(f"[GrammarChecker] Enhancing {len(all_issues)} issues with LLM...")
            
            # Get full document text for context
            full_text = "\n".join(line.content for line in document_data.lines)
            
            # Enhance issues (batch mode for efficiency with chunking)
            enhanced_issues, cost = await self.llm_enhancer.enhance_issues_batch(
                all_issues,
                full_text,
                max_issues=None  # Process ALL issues; chunking inside enhancer prevents timeouts
            )
            
            enhancement_metadata = {
                "llm_enabled": True,
                "issues_enhanced": self.llm_enhancer.total_issues_enhanced,
                "cost": cost,
                "warning": None
            }
            
            print(f"[GrammarChecker] LLM enhancement complete - Cost: ${cost:.4f}")
            
            return enhanced_issues, enhancement_metadata
        
        return all_issues, enhancement_metadata
    
    async def _check_line_content(
        self,
        line_content: str,
        line_number: int,
        enabled_categories: Optional[List[str]] = None
    ) -> List[GrammarIssue]:
        """
        Check an entire line for redundant phrases, awkward phrasing, punctuation, grammar, and spelling.
        
        Args:
            line_content: The full line content (all sentences combined)
            line_number: Line number in the document
            enabled_categories: Optional list of category names to check
            
        Returns:
            List of grammar issues found in the line
        """
        try:
            issues = []
            line_lower = line_content.lower()
            
            # Helper function to check if a category is enabled
            def is_category_enabled(category: str) -> bool:
                if enabled_categories is None:
                    return True  # All categories enabled by default
                return category in enabled_categories
            
            # Check for redundant phrases
            if is_category_enabled('redundancy'):
                for redundant_phrase, correction in self.redundant_phrases.items():
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(redundant_phrase) + r'\b'
                    matches = list(re.finditer(pattern, line_lower, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Preserve the capitalization of the original text
                        if original_text[0].isupper():
                            suggested_fix = correction.capitalize()
                        else:
                            suggested_fix = correction
                    
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"Redundant phrase: '{original_text}' can be simplified to '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='redundancy',
                            confidence=0.95,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for awkward phrasing
            if is_category_enabled('awkward_phrasing'):
                for awkward_phrase, correction in self.awkward_phrases.items():
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(awkward_phrase) + r'\b'
                    matches = list(re.finditer(pattern, line_lower, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Preserve the capitalization of the original text
                        if original_text[0].isupper():
                            suggested_fix = correction.capitalize()
                        else:
                            suggested_fix = correction
                    
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"Awkward phrasing: '{original_text}' can be simplified to '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='awkward_phrasing',
                            confidence=0.90,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for punctuation issues
            if is_category_enabled('punctuation'):
                for pattern, description, fix_func in self.punctuation_patterns:
                    matches = list(re.finditer(pattern, line_content))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Apply the fix function
                        suggested_fix = fix_func(match, line_content)
                    
                        # Skip if no change
                        if original_text == suggested_fix:
                            continue
                   
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description}: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='punctuation',
                            confidence=0.85,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for grammar issues
            if is_category_enabled('grammar'):
                for pattern, description, fix_func in self.grammar_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Apply the fix function
                        try:
                            suggested_fix = fix_func(match, line_content)
                        except Exception:
                            # If fix function fails, skip this match
                            continue
                
                        # Skip if no change
                        if original_text == suggested_fix:
                            continue
                
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description}: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='grammar',
                            confidence=0.80,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for agreement issues (subject-verb agreement)
            if is_category_enabled('agreement'):
                for pattern, description, fix_func in self.agreement_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Apply the fix function
                        try:
                            suggested_fix = fix_func(match, line_content)
                        except Exception:
                            # If fix function fails, skip this match
                            continue
                
                        # Skip if no change
                        if original_text == suggested_fix:
                            continue
                
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description}: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='agreement',
                            confidence=0.85,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for ambiguous pronouns
            if is_category_enabled('ambiguous_pronouns'):
                for pattern, description, fix_func in self.ambiguous_pronoun_patterns:
                    matches = list(re.finditer(pattern, line_content))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # For ambiguous pronouns, we typically flag without auto-fix
                        # If fix_func is provided, use it; otherwise suggest manual review
                        if fix_func is not None:
                            try:
                                suggested_fix = fix_func(match, line_content)
                            except Exception:
                                continue
                            
                            if original_text == suggested_fix:
                                continue
                            
                            corrected_line = (
                                line_content[:start_pos] + 
                                suggested_fix + 
                                line_content[end_pos:]
                            )
                            
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}",
                                fix=f"'{original_text}' → '{suggested_fix}'",
                                category='ambiguous_pronouns',
                                confidence=0.70,
                                corrected_sentence=corrected_line
                            )
                        else:
                            # No auto-fix - flag for manual review
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}: '{original_text}'",
                                fix="Review and clarify pronoun reference",
                                category='ambiguous_pronouns',
                                confidence=0.65,
                                corrected_sentence=None
                            )
                        
                        issues.append(issue)
            
            # Check for dialogue issues
            if is_category_enabled('dialogue'):
                for pattern, description, fix_func in self.dialogue_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                    
                        # Apply the fix function
                        try:
                            suggested_fix = fix_func(match, line_content)
                        except Exception:
                            # If fix function fails, skip this match
                            continue
                
                        # Skip if no change
                        if original_text == suggested_fix:
                            continue
                
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description}: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='dialogue',
                            confidence=0.85,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for capitalisation issues
            if is_category_enabled('capitalisation'):
                for pattern, description, fix_func in self.capitalisation_patterns:
                    matches = list(re.finditer(pattern, line_content))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # Skip if this is after an abbreviation (e.g., "a.m. on" should not flag)
                        # Only check for sentence-start capitalization pattern
                        if "Sentence should start with a capital letter" in description:
                            if self._is_abbreviation_before(line_content, start_pos):
                                continue
                    
                        # Apply the fix function
                        try:
                            suggested_fix = fix_func(match, line_content)
                        except Exception:
                            # If fix function fails, skip this match
                            continue
                
                        # Skip if no change
                        if original_text == suggested_fix:
                            continue
                
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                    
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description}: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='capitalisation',
                            confidence=0.90,
                            corrected_sentence=corrected_line
                        )
                    
                        issues.append(issue)
            
            # Check for tense consistency issues
            if is_category_enabled('tense_consistency'):
                for pattern, description, fix_func in self.tense_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # For tense issues, we flag them but don't auto-fix (too complex)
                        # Instead, we provide guidance in the problem description
                        suggested_fix = "Review and correct tense usage"
                        
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{description} in: '{original_text}'. Ensure all verbs use consistent tense (either all present or all past).",
                            fix=suggested_fix,
                            category='tense_consistency',
                            confidence=0.75,
                            corrected_sentence=None  # We don't auto-correct tense issues
                        )
                        
                        issues.append(issue)
            
            # Check for spelling issues
            if is_category_enabled('spelling'):
                line_lower = line_content.lower()
                for misspelling, correction in self.common_misspellings.items():
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(misspelling) + r'\b'
                    matches = list(re.finditer(pattern, line_lower, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # Preserve the capitalization of the original text
                        if original_text[0].isupper():
                            suggested_fix = correction.capitalize()
                        elif original_text.isupper():
                            suggested_fix = correction.upper()
                        else:
                            suggested_fix = correction
                        
                        # Create a corrected version of the line
                        corrected_line = (
                            line_content[:start_pos] + 
                            suggested_fix + 
                            line_content[end_pos:]
                        )
                        
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"Spelling error: '{original_text}' should be '{suggested_fix}'",
                            fix=f"'{original_text}' → '{suggested_fix}'",
                            category='spelling',
                            confidence=0.95,
                            corrected_sentence=corrected_line
                        )
                        
                        issues.append(issue)
            
            # ========================================================================
            # PARALLELISM/CONCISION CHECKING - EXPERIMENTAL FEATURE
            # ========================================================================
            # Check for parallelism/concision issues (EXPERIMENTAL - may produce false positives)
            if is_category_enabled('parallelism_concision'):
                for pattern, description, fix_func in self.parallelism_concision_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # If there's a fix function, apply it; otherwise just flag the issue
                        if fix_func is not None:
                            try:
                                suggested_fix = fix_func(match, line_content)
                            except Exception:
                                # If fix function fails, skip this match
                                continue
                            
                            # Skip if no change
                            if original_text.lower() == suggested_fix.lower():
                                continue
                            
                            # Preserve the capitalization of the original text
                            if original_text[0].isupper():
                                suggested_fix = suggested_fix.capitalize()
                            
                            # Create a corrected version of the line
                            corrected_line = (
                                line_content[:start_pos] + 
                                suggested_fix + 
                                line_content[end_pos:]
                            )
                            
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}",
                                fix=f"'{original_text}' → '{suggested_fix}'",
                                category='parallelism_concision',
                                confidence=0.85,
                                corrected_sentence=corrected_line
                            )
                        else:
                            # No auto-fix available, just flag the issue
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}: '{original_text}'",
                                fix="Review and revise for better clarity and conciseness",
                                category='parallelism_concision',
                                confidence=0.75,
                                corrected_sentence=None
                            )
                        
                        issues.append(issue)
                
                # Check for passive voice using spaCy (linguistic analysis)
                # This detects true passive voice only and generates context-specific fixes
                passive_issues = self._detect_passive_voice_spacy(line_content, line_number)
                issues.extend(passive_issues)
            
            # Check for article/specificity issues
            if is_category_enabled('article_specificity'):
                for pattern, description, fix_func in self.article_specificity_patterns:
                    matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        # If there's a fix function, apply it; otherwise just flag the issue
                        if fix_func is not None:
                            try:
                                suggested_fix = fix_func(match, line_content)
                            except Exception:
                                # If fix function fails, skip this match
                                continue
                            
                            # Skip if no change
                            if original_text.lower() == suggested_fix.lower():
                                continue
                            
                            # Preserve the capitalization of the original text
                            if original_text[0].isupper():
                                suggested_fix = suggested_fix.capitalize()
                            
                            # Create a corrected version of the line
                            corrected_line = (
                                line_content[:start_pos] + 
                                suggested_fix + 
                                line_content[end_pos:]
                            )
                            
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}",
                                fix=f"'{original_text}' → '{suggested_fix}'",
                                category='article_specificity',
                                confidence=0.90,
                                corrected_sentence=corrected_line
                            )
                        else:
                            # No auto-fix available, just flag the issue
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}: '{original_text}'",
                                fix="Review and revise for better clarity and specificity",
                                category='article_specificity',
                                confidence=0.75,
                                corrected_sentence=None
                            )
                        
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            print(f"Error in grammar check for line {line_number}: {e}")
            return []
    
    # Removed unused LanguageTool processing methods - we only check for redundant phrases, awkward phrasing, punctuation, and grammar now
    
    def _merge_similar_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Merge similar issues to avoid duplicates"""
        if not issues:
            return issues
        
        merged = []
        seen = set()
        
        for issue in issues:
            # Create a unique key for this issue
            key = (
                issue.line_number,
                issue.sentence_number,
                issue.original_text.lower(),
                issue.category
            )
            
            if key not in seen:
                merged.append(issue)
                seen.add(key)
        
        # Additional deduplication: merge issues that fix the same text on the same line
        # This handles cases where "buyed" is flagged by both spelling and tense_consistency
        final_merged = []
        line_issues = {}
        
        # Group issues by line
        for issue in merged:
            if issue.line_number not in line_issues:
                line_issues[issue.line_number] = []
            line_issues[issue.line_number].append(issue)
        
        # Process each line
        for line_num, line_issue_list in line_issues.items():
            # Check for overlapping fixes
            processed_issues = []
            for issue in line_issue_list:
                is_duplicate = False
                for processed in processed_issues:
                    # Check if this issue fixes the same text as a processed issue
                    if (issue.original_text == processed.original_text and 
                        issue.line_number == processed.line_number and
                        issue.fix == processed.fix):
                        # Merge categories and keep the one with higher confidence
                        if issue.confidence > processed.confidence:
                            processed.category = f"{processed.category}/{issue.category}"
                            processed.confidence = issue.confidence
                            processed.problem = f"{processed.problem} (also flagged as {issue.category})"
                        else:
                            processed.category = f"{issue.category}/{processed.category}"
                            processed.problem = f"{processed.problem} (also flagged as {issue.category})"
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    processed_issues.append(issue)
            
            final_merged.extend(processed_issues)
        
        return final_merged
    
    def get_available_categories(self) -> List[Dict[str, Any]]:
        """
        Get list of available grammar checking categories
        
        Returns:
            List of dictionaries with category id and display name
        """
        return [
            {'id': category_id, 'name': category_name}
            for category_id, category_name in self.categories.items()
        ]
    
    def get_issues_summary(self, issues: List[GrammarIssue]) -> Dict[str, Any]:
        """
        Generate a summary of issues found
        
        Args:
            issues: List of grammar issues
            
        Returns:
            Dictionary with summary statistics
        """
        if not issues:
            return {
                'total_issues': 0,
                'categories': {},
                'lines_with_issues': 0,
                'sentences_with_issues': 0
            }
        
        # Count issues by category
        categories = {}
        for issue in issues:
            category = issue.category
            categories[category] = categories.get(category, 0) + 1
        
        # Count unique lines and sentences with issues
        lines_with_issues = len(set(issue.line_number for issue in issues))
        sentences_with_issues = len(set((issue.line_number, issue.sentence_number) for issue in issues))
        
        return {
            'total_issues': len(issues),
            'categories': categories,
            'lines_with_issues': lines_with_issues,
            'sentences_with_issues': sentences_with_issues
        }

