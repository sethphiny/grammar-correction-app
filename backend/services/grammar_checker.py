"""
Grammar checker for redundant phrases
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Callable
from models.schemas import DocumentData, DocumentLine, GrammarIssue


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
    """Grammar checker focusing on redundant phrases, awkward phrasing, punctuation, and grammar"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        
        # Grammar issue categories
        self.categories = {
            'redundancy': 'Redundant Phrases',
            'awkward_phrasing': 'Awkward Phrasing',
            'punctuation': 'Punctuation',
            'grammar': 'Grammar',
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
            (r'([,;:!?])([A-Z][a-z])', 'Missing space after punctuation', lambda m, t: f"{m.group(1)} {m.group(2)}"),
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
    
    async def check_document(
        self, 
        document_data: DocumentData, 
        progress_callback: Optional[Callable] = None
    ) -> List[GrammarIssue]:
        """
        Check entire document for redundant phrases, awkward phrasing, punctuation, and grammar
        
        Strategy: Check at LINE level, scanning for predefined patterns of
        redundant phrases, awkward phrasing, punctuation errors, and grammar mistakes.
        
        Args:
            document_data: Parsed document data
            progress_callback: Optional callback for progress updates
                              Signature: async def callback(line_num: int, total_lines: int, issues_found: int)
            
        Returns:
            List of grammar issues found
        """
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
                line.line_number
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
        
        return all_issues
    
    async def _check_line_content(
        self,
        line_content: str,
        line_number: int
    ) -> List[GrammarIssue]:
        """
        Check an entire line for redundant phrases, awkward phrasing, punctuation, and grammar.
        
        Args:
            line_content: The full line content (all sentences combined)
            line_number: Line number in the document
            
        Returns:
            List of grammar issues found in the line
        """
        try:
            issues = []
            line_lower = line_content.lower()
            
            # Check for redundant phrases
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
        
        return merged
    
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

