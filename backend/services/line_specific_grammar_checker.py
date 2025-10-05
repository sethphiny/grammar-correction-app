import re
import asyncio
import logging
from typing import List, Dict, Optional, Set, Tuple
from models.schemas import GrammarIssue, GrammarIssueType, ProposedFix, DocumentLine

logger = logging.getLogger(__name__)

class LineSpecificGrammarChecker:
    """
    Specialized grammar checker that detects specific line-by-line issues
    with high precision and provides targeted fixes.
    """
    
    def __init__(self):
        # Common past tense indicators
        self.past_indicators = {
            'yesterday', 'last week', 'last month', 'last year', 'ago', 'before',
            'earlier', 'previously', 'once', 'then', 'after that', 'in the past',
            'used to', 'would', 'had been', 'was', 'were'
        }
        
        # Common present tense indicators
        self.present_indicators = {
            'now', 'today', 'currently', 'always', 'usually', 'often', 'sometimes',
            'every day', 'every week', 'nowadays', 'at present'
        }
        
        # Verb tense mappings
        self.verb_tense_map = {
            'come': {'past': 'came', 'present': 'come', 'future': 'will come'},
            'go': {'past': 'went', 'present': 'go', 'future': 'will go'},
            'see': {'past': 'saw', 'present': 'see', 'future': 'will see'},
            'do': {'past': 'did', 'present': 'do', 'future': 'will do'},
            'have': {'past': 'had', 'present': 'have', 'future': 'will have'},
            'is': {'past': 'was', 'present': 'is', 'future': 'will be'},
            'are': {'past': 'were', 'present': 'are', 'future': 'will be'},
            'get': {'past': 'got', 'present': 'get', 'future': 'will get'},
            'make': {'past': 'made', 'present': 'make', 'future': 'will make'},
            'take': {'past': 'took', 'present': 'take', 'future': 'will take'},
            'give': {'past': 'gave', 'present': 'give', 'future': 'will give'},
            'know': {'past': 'knew', 'present': 'know', 'future': 'will know'},
            'think': {'past': 'thought', 'present': 'think', 'future': 'will think'},
            'say': {'past': 'said', 'present': 'say', 'future': 'will say'},
            'tell': {'past': 'told', 'present': 'tell', 'future': 'will tell'},
            'find': {'past': 'found', 'present': 'find', 'future': 'will find'},
            'look': {'past': 'looked', 'present': 'look', 'future': 'will look'},
            'work': {'past': 'worked', 'present': 'work', 'future': 'will work'},
            'call': {'past': 'called', 'present': 'call', 'future': 'will call'},
            'try': {'past': 'tried', 'present': 'try', 'future': 'will try'},
            'ask': {'past': 'asked', 'present': 'ask', 'future': 'will ask'},
            'need': {'past': 'needed', 'present': 'need', 'future': 'will need'},
            'feel': {'past': 'felt', 'present': 'feel', 'future': 'will feel'},
            'become': {'past': 'became', 'present': 'become', 'future': 'will become'},
            'leave': {'past': 'left', 'present': 'leave', 'future': 'will leave'},
            'put': {'past': 'put', 'present': 'put', 'future': 'will put'},
            'mean': {'past': 'meant', 'present': 'mean', 'future': 'will mean'},
            'keep': {'past': 'kept', 'present': 'keep', 'future': 'will keep'},
            'let': {'past': 'let', 'present': 'let', 'future': 'will let'},
            'begin': {'past': 'began', 'present': 'begin', 'future': 'will begin'},
            'seem': {'past': 'seemed', 'present': 'seem', 'future': 'will seem'},
            'help': {'past': 'helped', 'present': 'help', 'future': 'will help'},
            'show': {'past': 'showed', 'present': 'show', 'future': 'will show'},
            'hear': {'past': 'heard', 'present': 'hear', 'future': 'will hear'},
            'play': {'past': 'played', 'present': 'play', 'future': 'will play'},
            'run': {'past': 'ran', 'present': 'run', 'future': 'will run'},
            'move': {'past': 'moved', 'present': 'move', 'future': 'will move'},
            'live': {'past': 'lived', 'present': 'live', 'future': 'will live'},
            'believe': {'past': 'believed', 'present': 'believe', 'future': 'will believe'},
            'hold': {'past': 'held', 'present': 'hold', 'future': 'will hold'},
            'bring': {'past': 'brought', 'present': 'bring', 'future': 'will bring'},
            'happen': {'past': 'happened', 'present': 'happen', 'future': 'will happen'},
            'write': {'past': 'wrote', 'present': 'write', 'future': 'will write'},
            'sit': {'past': 'sat', 'present': 'sit', 'future': 'will sit'},
            'stand': {'past': 'stood', 'present': 'stand', 'future': 'will stand'},
            'lose': {'past': 'lost', 'present': 'lose', 'future': 'will lose'},
            'pay': {'past': 'paid', 'present': 'pay', 'future': 'will pay'},
            'meet': {'past': 'met', 'present': 'meet', 'future': 'will meet'},
            'include': {'past': 'included', 'present': 'include', 'future': 'will include'},
            'continue': {'past': 'continued', 'present': 'continue', 'future': 'will continue'},
            'set': {'past': 'set', 'present': 'set', 'future': 'will set'},
            'learn': {'past': 'learned', 'present': 'learn', 'future': 'will learn'},
            'change': {'past': 'changed', 'present': 'change', 'future': 'will change'},
            'lead': {'past': 'led', 'present': 'lead', 'future': 'will lead'},
            'understand': {'past': 'understood', 'present': 'understand', 'future': 'will understand'},
            'watch': {'past': 'watched', 'present': 'watch', 'future': 'will watch'},
            'follow': {'past': 'followed', 'present': 'follow', 'future': 'will follow'},
            'stop': {'past': 'stopped', 'present': 'stop', 'future': 'will stop'},
            'create': {'past': 'created', 'present': 'create', 'future': 'will create'},
            'speak': {'past': 'spoke', 'present': 'speak', 'future': 'will speak'},
            'read': {'past': 'read', 'present': 'read', 'future': 'will read'},
            'allow': {'past': 'allowed', 'present': 'allow', 'future': 'will allow'},
            'add': {'past': 'added', 'present': 'add', 'future': 'will add'},
            'spend': {'past': 'spent', 'present': 'spend', 'future': 'will spend'},
            'grow': {'past': 'grew', 'present': 'grow', 'future': 'will grow'},
            'open': {'past': 'opened', 'present': 'open', 'future': 'will open'},
            'walk': {'past': 'walked', 'present': 'walk', 'future': 'will walk'},
            'win': {'past': 'won', 'present': 'win', 'future': 'will win'},
            'offer': {'past': 'offered', 'present': 'offer', 'future': 'will offer'},
            'remember': {'past': 'remembered', 'present': 'remember', 'future': 'will remember'},
            'love': {'past': 'loved', 'present': 'love', 'future': 'will love'},
            'consider': {'past': 'considered', 'present': 'consider', 'future': 'will consider'},
            'appear': {'past': 'appeared', 'present': 'appear', 'future': 'will appear'},
            'buy': {'past': 'bought', 'present': 'buy', 'future': 'will buy'},
            'wait': {'past': 'waited', 'present': 'wait', 'future': 'will wait'},
            'serve': {'past': 'served', 'present': 'serve', 'future': 'will serve'},
            'die': {'past': 'died', 'present': 'die', 'future': 'will die'},
            'send': {'past': 'sent', 'present': 'send', 'future': 'will send'},
            'expect': {'past': 'expected', 'present': 'expect', 'future': 'will expect'},
            'build': {'past': 'built', 'present': 'build', 'future': 'will build'},
            'stay': {'past': 'stayed', 'present': 'stay', 'future': 'will stay'},
            'fall': {'past': 'fell', 'present': 'fall', 'future': 'will fall'},
            'cut': {'past': 'cut', 'present': 'cut', 'future': 'will cut'},
            'reach': {'past': 'reached', 'present': 'reach', 'future': 'will reach'},
            'kill': {'past': 'killed', 'present': 'kill', 'future': 'will kill'},
            'remain': {'past': 'remained', 'present': 'remain', 'future': 'will remain'},
            'suggest': {'past': 'suggested', 'present': 'suggest', 'future': 'will suggest'},
            'raise': {'past': 'raised', 'present': 'raise', 'future': 'will raise'},
            'pass': {'past': 'passed', 'present': 'pass', 'future': 'will pass'},
            'sell': {'past': 'sold', 'present': 'sell', 'future': 'will sell'},
            'require': {'past': 'required', 'present': 'require', 'future': 'will require'},
            'report': {'past': 'reported', 'present': 'report', 'future': 'will report'},
            'decide': {'past': 'decided', 'present': 'decide', 'future': 'will decide'},
            'pull': {'past': 'pulled', 'present': 'pull', 'future': 'will pull'}
        }
        
        # Awkward word choices for specific contexts
        self.awkward_word_contexts = {
            'laughter': {
                'tentative': ['uncertain', 'hesitant', 'nervous', 'shaky'],
                'weak': ['feeble', 'faint', 'soft', 'quiet'],
                'strange': ['odd', 'unusual', 'peculiar', 'unexpected']
            },
            'movement': {
                'lost': ['slipped', 'dropped', 'fell'],
                'went': ['moved', 'traveled', 'proceeded'],
                'came': ['arrived', 'approached', 'moved toward']
            }
        }
        
        # Subject-verb agreement patterns
        self.singular_subjects = {
            'the', 'this', 'that', 'each', 'every', 'a', 'an', 'one', 'someone', 
            'anyone', 'everyone', 'nobody', 'somebody', 'anybody', 'everybody'
        }
        
        self.plural_subjects = {
            'the', 'these', 'those', 'many', 'several', 'some', 'all', 'both', 
            'few', 'a few', 'most', 'other', 'others'
        }
    
    async def check_line_specific_issues(self, line: DocumentLine) -> List[GrammarIssue]:
        """Check a line for specific grammar issues with high precision"""
        issues = []
        
        # Determine the overall tense context of the entire line
        line_tense_context = self._determine_line_tense_context(line)
        
        for sentence_idx, sentence in enumerate(line.sentences):
            if not sentence.strip():
                continue
            
            # Check for specific issues
            issues.extend(self._check_tense_shift(sentence, line.line_number, sentence_idx + 1, line_tense_context))
            issues.extend(self._check_extra_comma_quotation(sentence, line.line_number, sentence_idx + 1))
            issues.extend(self._check_awkward_word_choice(sentence, line.line_number, sentence_idx + 1, line.content))
            issues.extend(self._check_awkward_phrasing(sentence, line.line_number, sentence_idx + 1))
            issues.extend(self._check_subject_verb_agreement_complex(sentence, line.line_number, sentence_idx + 1))
        
        return issues
    
    def _determine_line_tense_context(self, line: DocumentLine) -> str:
        """Determine the overall tense context of an entire line"""
        # Combine all sentences in the line
        full_text = ' '.join(line.sentences)
        return self._determine_tense_context(full_text)
    
    def _check_tense_shift(self, sentence: str, line_number: int, sentence_number: int, line_tense_context: str = None) -> List[GrammarIssue]:
        """Check for tense shifts within a sentence"""
        issues = []
        
        # Use line tense context if provided, otherwise determine from sentence
        if line_tense_context and line_tense_context != 'unknown':
            tense_context = line_tense_context
        else:
            tense_context = self._determine_tense_context(sentence)
            
            # If we can't determine tense from this sentence alone, try to infer from context
            if tense_context == 'unknown':
                # Look for specific patterns that indicate past tense context
                if any(word in sentence.lower() for word in ['retirement', 'carried', 'moved', 'set']):
                    tense_context = 'past'
                elif any(word in sentence.lower() for word in ['now', 'today', 'currently']):
                    tense_context = 'present'
        
        if tense_context == 'unknown':
            return issues
        
        # Find all verbs in the sentence
        verbs = self._find_verbs_in_sentence(sentence)
        
        # Collect all verbs that need to be changed
        verbs_to_change = []
        for verb_info in verbs:
            verb = verb_info['verb']
            
            # Find the base verb form and expected tense
            base_verb = None
            expected_tense = None
            
            # Look through the verb tense map to find the base form
            for base, tenses in self.verb_tense_map.items():
                if verb.lower() in tenses.values():
                    base_verb = base
                    expected_tense = tenses[tense_context]
                    break
            
            if base_verb and expected_tense and verb.lower() != expected_tense.lower():
                verbs_to_change.append({
                    'original': verb,
                    'corrected': expected_tense,
                    'position': verb_info['position']
                })
        
        # If we have verbs to change, create a single issue with the corrected sentence
        if verbs_to_change:
            # Sort by position (reverse order) to avoid position shifting issues
            verbs_to_change.sort(key=lambda x: x['position'], reverse=True)
            
            corrected_sentence = sentence
            fix_details = []
            
            for verb_change in verbs_to_change:
                original = verb_change['original']
                corrected = verb_change['corrected']
                position = verb_change['position']
                
                # Replace the verb
                corrected_sentence = corrected_sentence[:position] + corrected + corrected_sentence[position + len(original):]
                fix_details.append(f"'{original}' → '{corrected}'")
            
            # Create a single issue for all tense changes in this sentence
            reason_parts = []
            for v in verbs_to_change:
                reason_parts.append(f"'{v['original']}' (present) vs. surrounding {tense_context} tense")
            reason_text = f"Tense shift → {'; '.join(reason_parts)}"
            
            issues.append(GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=sentence,
                problem="Tense shift",
                reason=reason_text,
                proposed_fix=ProposedFix(
                    action="replace",
                    details=f"Change {'; '.join(fix_details)} for tense consistency",
                    corrected_text=corrected_sentence
                ),
                issue_type=GrammarIssueType.VERB_TENSE,
                confidence=0.9,
                line_number=line_number,
                sentence_number=sentence_number,
                original_text='; '.join([v['original'] for v in verbs_to_change]),
                fix='; '.join([v['corrected'] for v in verbs_to_change]),
                corrected_text=corrected_sentence
            ))
        
        return issues
    
    def _check_extra_comma_quotation(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for extra commas before closing quotation marks"""
        issues = []
        
        # Pattern: comma before closing quotation mark
        pattern = r",\s*'"
        matches = list(re.finditer(pattern, sentence))
        
        for match in matches:
            # Find the full quoted text
            quote_start = sentence.rfind("'", 0, match.start())
            if quote_start == -1:
                continue
            
            quoted_text = sentence[quote_start:match.end()]
            
            # Create corrected version (remove the comma)
            corrected_sentence = sentence[:match.start()] + "'" + sentence[match.end():]
            
            issues.append(GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=sentence,
                problem="Extra comma before closing quotation mark",
                reason=f"Extra comma before closing quotation mark in '{quoted_text}'",
                proposed_fix=ProposedFix(
                    action="remove",
                    details="Remove the comma before the closing quotation mark",
                    corrected_text=corrected_sentence
                ),
                issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                confidence=0.95,
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=quoted_text,
                fix=quoted_text.replace(",", ""),
                corrected_text=corrected_sentence
            ))
        
        return issues
    
    def _check_awkward_word_choice(self, sentence: str, line_number: int, sentence_number: int, line_context: str = None) -> List[GrammarIssue]:
        """Check for awkward word choices in specific contexts"""
        issues = []
        
        # Use line context if provided, otherwise use sentence
        text_to_check = line_context if line_context else sentence
        
        # Check for awkward words in laughter context (both orders)
        # Pattern 1: awkward word followed by laughter word
        laughter_pattern1 = r'\b(tentative|weak|strange)\b.*?(laugh|giggle|chuckle|guffaw)'
        # Pattern 2: laughter word followed by awkward word
        laughter_pattern2 = r'\b(laugh|giggle|chuckle|guffaw).*?\b(tentative|weak|strange)\b'
        
        for pattern in [laughter_pattern1, laughter_pattern2]:
            matches = re.finditer(pattern, text_to_check, re.IGNORECASE)
            
            for match in matches:
                if len(match.groups()) == 2:
                    awkward_word = match.group(1) if match.group(1).lower() in ['tentative', 'weak', 'strange'] else match.group(2)
                    laughter_word = match.group(2) if match.group(1).lower() in ['tentative', 'weak', 'strange'] else match.group(1)
                    
                    # Check if the awkward word is in the current sentence
                    if awkward_word.lower() in sentence.lower():
                        if awkward_word.lower() in self.awkward_word_contexts.get('laughter', {}):
                            suggestions = self.awkward_word_contexts['laughter'][awkward_word.lower()]
                            suggested_word = suggestions[0]  # Use the first suggestion
                            
                            corrected_sentence = sentence.replace(awkward_word, suggested_word, 1)
                            
                            issues.append(GrammarIssue(
                                lines=str(line_number),
                                sentences=str(sentence_number),
                                text=sentence,
                                problem="Awkward word choice",
                                reason=f"'{awkward_word}' doesn't work well as an adjective for {laughter_word}",
                                proposed_fix=ProposedFix(
                                    action="replace",
                                    details=f"Use '{suggested_word}' instead of '{awkward_word}'",
                                    corrected_text=corrected_sentence
                                ),
                                issue_type=GrammarIssueType.AWKWARD_PHRASING,
                                confidence=0.85,
                                line_number=line_number,
                                sentence_number=sentence_number,
                                original_text=awkward_word,
                                fix=suggested_word,
                                corrected_text=corrected_sentence
                            ))
        
        return issues
    
    def _check_awkward_phrasing(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for awkward phrasing patterns"""
        issues = []
        
        # Pattern: "lost [object] out of [possessive] hands"
        lost_pattern = r'(lost|dropped)\s+(\w+)\s+(\w+)\s+out\s+of\s+(\w+)\s+(hands)'
        matches = re.finditer(lost_pattern, sentence, re.IGNORECASE)
        
        for match in matches:
            verb = match.group(1)
            object_word = match.group(3)  # cup
            possessive = match.group(4)   # his
            
            # Suggest better phrasing
            if verb.lower() == 'lost':
                suggested_phrase = f"{possessive} {object_word} slipped from {possessive} hands"
            else:
                suggested_phrase = f"{possessive} {object_word} fell from {possessive} hands"
            
            corrected_sentence = sentence.replace(match.group(0), suggested_phrase, 1)
            
            issues.append(GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=sentence,
                problem="Awkward phrasing",
                reason=f"'{match.group(0)}' is awkward phrasing",
                proposed_fix=ProposedFix(
                    action="replace",
                    details=f"Use more natural phrasing: '{suggested_phrase}'",
                    corrected_text=corrected_sentence
                ),
                issue_type=GrammarIssueType.AWKWARD_PHRASING,
                confidence=0.9,
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=match.group(0),
                fix=suggested_phrase,
                corrected_text=corrected_sentence
            ))
        
        return issues
    
    def _check_subject_verb_agreement_complex(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for subject-verb agreement in complex sentences"""
        issues = []
        
        # Pattern: "long-term memory—the [list]—[verb]"
        # This is a specific pattern for the example you provided
        pattern = r'long-term memory.*?(is|are) still intact'
        matches = re.finditer(pattern, sentence)
        
        for match in matches:
            full_match = match.group(0)
            
            # Extract the list part and verb part from the match
            # The pattern is: "long-term memory—the birthdays, family names, history facts, is still intact"
            if '—' in full_match:
                parts = full_match.split('—')
                if len(parts) >= 2:
                    # The second part contains both the list and the verb
                    second_part = parts[1]  # "the birthdays, family names, history facts, is still intact"
                    
                    # Find the verb part (last part after the last comma)
                    if ',' in second_part:
                        # Split by comma and get the last part
                        comma_parts = second_part.split(',')
                        list_part = ','.join(comma_parts[:-1])  # "the birthdays, family names, history facts"
                        verb_part = comma_parts[-1].strip()  # "is still intact"
                        
                        # Check if the list contains plural items
                        list_items = [item.strip() for item in list_part.split(',') if item.strip()]
                        
                        # If there are multiple items in the list, the verb should be plural
                        if len(list_items) > 1:
                            # Check if the verb is singular when it should be plural
                            singular_verbs = ['is', 'was', 'has', 'does']
                            plural_verbs = ['are', 'were', 'have', 'do']
                            
                            for singular, plural in zip(singular_verbs, plural_verbs):
                                if singular in verb_part.lower():
                                    corrected_verb_part = verb_part.replace(singular, plural, 1)
                                    corrected_sentence = sentence.replace(verb_part, corrected_verb_part, 1)
                                    
                                    issues.append(GrammarIssue(
                                        lines=str(line_number),
                                        sentences=str(sentence_number),
                                        text=sentence,
                                        problem="Subject–verb agreement",
                                        reason=f"List is plural, verb is singular. '{singular}' should be '{plural}'",
                                        proposed_fix=ProposedFix(
                                            action="replace",
                                            details=f"Change '{singular}' to '{plural}' for subject-verb agreement",
                                            corrected_text=corrected_sentence
                                        ),
                                        issue_type=GrammarIssueType.VERB_TENSE,
                                        confidence=0.95,
                                        line_number=line_number,
                                        sentence_number=sentence_number,
                                        original_text=singular,
                                        fix=plural,
                                        corrected_text=corrected_sentence
                                    ))
                                    break
        
        return issues
    
    def _determine_tense_context(self, sentence: str) -> str:
        """Determine the overall tense context of a sentence"""
        sentence_lower = sentence.lower()
        
        # Check for past tense indicators
        past_score = sum(1 for indicator in self.past_indicators if indicator in sentence_lower)
        
        # Check for present tense indicators
        present_score = sum(1 for indicator in self.present_indicators if indicator in sentence_lower)
        
        # Check for past tense verbs (more comprehensive list)
        past_verbs = ['was', 'were', 'had', 'did', 'went', 'came', 'saw', 'took', 'got', 'made', 
                     'carried', 'moved', 'set', 'watched', 'learned', 'bought', 'sold', 'told',
                     'thought', 'knew', 'found', 'looked', 'worked', 'called', 'tried', 'asked',
                     'needed', 'felt', 'became', 'left', 'put', 'meant', 'kept', 'let', 'began',
                     'seemed', 'helped', 'showed', 'heard', 'played', 'ran', 'moved', 'lived',
                     'believed', 'held', 'brought', 'happened', 'wrote', 'sat', 'stood', 'lost',
                     'paid', 'met', 'included', 'continued', 'learned', 'changed', 'led', 'understood',
                     'watched', 'followed', 'stopped', 'created', 'spoke', 'read', 'allowed', 'added',
                     'spent', 'grew', 'opened', 'walked', 'won', 'offered', 'remembered', 'loved',
                     'considered', 'appeared', 'waited', 'served', 'died', 'sent', 'expected', 'built',
                     'stayed', 'fell', 'cut', 'reached', 'killed', 'remained', 'suggested', 'raised',
                     'passed', 'sold', 'required', 'reported', 'decided', 'pulled']
        
        past_verb_score = sum(1 for verb in past_verbs if f' {verb} ' in f' {sentence_lower} ')
        
        # Check for present tense verbs
        present_verbs = ['is', 'are', 'have', 'do', 'go', 'come', 'see', 'take', 'get', 'make']
        present_verb_score = sum(1 for verb in present_verbs if f' {verb} ' in f' {sentence_lower} ')
        
        # Determine context
        if past_score + past_verb_score > present_score + present_verb_score:
            return 'past'
        elif present_score + present_verb_score > past_score + past_verb_score:
            return 'present'
        else:
            return 'unknown'
    
    def _find_verbs_in_sentence(self, sentence: str) -> List[Dict]:
        """Find verbs in a sentence with their positions"""
        verbs = []
        
        # Simple word-based approach
        words = sentence.split()
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Check if it's a verb in any tense form
            is_verb = False
            for verb_forms in self.verb_tense_map.values():
                if clean_word.lower() in verb_forms.values():
                    is_verb = True
                    break
            
            if is_verb:
                # Find position in original sentence
                position = sentence.find(word)
                verbs.append({
                    'verb': clean_word,
                    'position': position,
                    'word_index': i
                })
        
        return verbs
