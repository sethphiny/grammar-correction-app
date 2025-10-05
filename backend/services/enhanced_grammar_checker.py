import re
import asyncio
import logging
from typing import List, Dict, Optional, Set
import language_tool_python
from models.schemas import GrammarIssue, GrammarIssueType, ProposedFix, DocumentLine

logger = logging.getLogger(__name__)

class EnhancedGrammarChecker:
    """Enhanced grammar checker that combines LanguageTool with custom rules"""
    
    def __init__(self, use_server_mode: bool = False, server_url: Optional[str] = None):
        self.use_server_mode = use_server_mode
        self.server_url = server_url
        
        # Initialize LanguageTool
        try:
            if use_server_mode and server_url:
                self.tool = language_tool_python.LanguageToolPublicAPI('en-US')
                logger.info(f"Enhanced grammar checker: Connected to LanguageTool server at {server_url}")
            else:
                self.tool = language_tool_python.LanguageTool('en-US')
                logger.info("Enhanced grammar checker: LanguageTool initialized (local mode)")
        except Exception as e:
            logger.error(f"Could not initialize LanguageTool: {e}")
            self.tool = None
    
    async def check_sentence(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check a sentence for grammar issues using both LanguageTool and custom rules"""
        issues = []
        
        if not sentence.strip():
            return issues
        
        # 1. Use LanguageTool for what it can detect
        if self.tool:
            try:
                matches = await asyncio.to_thread(self.tool.check, sentence)
                for match in matches:
                    issue = self._convert_languagetool_match(match, sentence, line_number, sentence_number)
                    if issue:
                        issues.append(issue)
            except Exception as e:
                logger.warning(f"LanguageTool check failed: {e}")
        
        # 2. Apply custom grammar rules
        custom_issues = self._check_custom_rules(sentence, line_number, sentence_number)
        issues.extend(custom_issues)
        
        return issues
    
    def _convert_languagetool_match(self, match, sentence: str, line_number: int, sentence_number: int) -> Optional[GrammarIssue]:
        """Convert LanguageTool match to GrammarIssue"""
        try:
            # Extract the problematic text
            problematic_text = sentence[match.offset:match.offset + match.errorLength]
            
            # Determine issue type
            issue_type = self._categorize_issue(match.ruleId, match.message)
            
            # Get suggested fix
            suggested_text = match.replacements[0] if match.replacements else problematic_text
            
            # Create comprehensive fix
            corrected_sentence = sentence[:match.offset] + suggested_text + sentence[match.offset + match.errorLength:]
            
            return GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=sentence,
                problem=f"Grammar issue ({issue_type.value})",
                reason=match.message,
                proposed_fix=ProposedFix(
                    action="replace",
                    details=match.message,
                    corrected_text=corrected_sentence
                ),
                issue_type=issue_type,
                confidence=0.8,
                # Legacy fields
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=problematic_text,
                fix=suggested_text,
                corrected_text=corrected_sentence
            )
        except Exception as e:
            logger.error(f"Error converting LanguageTool match: {e}")
            return None
    
    def _categorize_issue(self, rule_id: str, message: str) -> GrammarIssueType:
        """Categorize issue based on rule ID and message"""
        rule_id_lower = rule_id.lower()
        message_lower = message.lower()
        
        if any(keyword in rule_id_lower for keyword in ['verb', 'tense', 'agreement']):
            return GrammarIssueType.VERB_TENSE
        elif any(keyword in rule_id_lower for keyword in ['punctuation', 'comma', 'period']):
            return GrammarIssueType.GRAMMAR_PUNCTUATION
        elif any(keyword in rule_id_lower for keyword in ['wordiness', 'redundancy']):
            return GrammarIssueType.REDUNDANCY
        else:
            return GrammarIssueType.AWKWARD_PHRASING
    
    def _check_custom_rules(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Apply custom grammar rules that LanguageTool misses"""
        issues = []
        
        # 1. Subject-verb disagreement
        issues.extend(self._check_subject_verb_agreement(sentence, line_number, sentence_number))
        
        # 2. Missing articles
        issues.extend(self._check_missing_articles(sentence, line_number, sentence_number))
        
        # 3. Tense consistency
        issues.extend(self._check_tense_consistency(sentence, line_number, sentence_number))
        
        # 4. There is/are agreement
        issues.extend(self._check_there_agreement(sentence, line_number, sentence_number))
        
        return issues
    
    def _check_subject_verb_agreement(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for subject-verb agreement issues"""
        issues = []
        
        # Pattern: "The [noun] [verb]" where verb doesn't match
        patterns = [
            # Singular subject with plural verb
            (r'\b(the|this|that|each|every|a|an)\s+(\w+)\s+(are|were|have|do)\b', 
             lambda m: f"{m.group(1)} {m.group(2)} {self._get_singular_verb(m.group(3))}"),
            # Plural subject with singular verb  
            (r'\b(the|these|those|many|several|some|all)\s+(\w+)\s+(is|was|has|does)\b',
             lambda m: f"{m.group(1)} {m.group(2)} {self._get_plural_verb(m.group(3))}"),
        ]
        
        for pattern, fix_func in patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                original_text = match.group(0)
                suggested_text = fix_func(match)
                corrected_sentence = sentence.replace(original_text, suggested_text, 1)
                
                issues.append(GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="Subject-verb disagreement",
                    reason=f"'{original_text}' has incorrect subject-verb agreement",
                    proposed_fix=ProposedFix(
                        action="replace",
                        details="Correct subject-verb agreement",
                        corrected_text=corrected_sentence
                    ),
                    issue_type=GrammarIssueType.VERB_TENSE,
                    confidence=0.9,
                    # Legacy fields
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=original_text,
                    fix=suggested_text,
                    corrected_text=corrected_sentence
                ))
        
        return issues
    
    def _check_missing_articles(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for missing articles"""
        issues = []
        
        # Pattern: "went to [noun]" should be "went to the [noun]" (but not if already has article)
        patterns = [
            (r'\b(went to|go to|goes to|going to)\s+(?!the|a|an)([a-z]+)\b', 
             lambda m: f"{m.group(1)} the {m.group(2)}"),
            (r'\b(bought|have|has|had)\s+(?!a|an|the)([a-z]+)\b',
             lambda m: f"{m.group(1)} {'an' if m.group(2)[0] in 'aeiou' else 'a'} {m.group(2)}"),
        ]
        
        for pattern, fix_func in patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                original_text = match.group(0)
                suggested_text = fix_func(match)
                corrected_sentence = sentence.replace(original_text, suggested_text, 1)
                
                issues.append(GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="Missing article",
                    reason=f"'{original_text}' is missing an article",
                    proposed_fix=ProposedFix(
                        action="replace",
                        details="Add missing article",
                        corrected_text=corrected_sentence
                    ),
                    issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                    confidence=0.8,
                    # Legacy fields
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=original_text,
                    fix=suggested_text,
                    corrected_text=corrected_sentence
                ))
        
        return issues
    
    def _check_tense_consistency(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for tense consistency issues"""
        issues = []
        
        # Pattern: "Yesterday I [present_verb]" should be "Yesterday I [past_verb]"
        past_indicators = ['yesterday', 'last week', 'last month', 'last year', 'ago', 'before']
        present_to_past = {
            'go': 'went', 'buy': 'bought', 'see': 'saw', 'do': 'did', 'have': 'had',
            'is': 'was', 'are': 'were', 'am': 'was', 'get': 'got', 'come': 'came'
        }
        
        for indicator in past_indicators:
            if indicator in sentence.lower():
                for present, past in present_to_past.items():
                    pattern = rf'\b{indicator}.*?\b{present}\b'
                    if re.search(pattern, sentence, re.IGNORECASE):
                        original_text = present
                        suggested_text = past
                        corrected_sentence = re.sub(rf'\b{present}\b', past, sentence, count=1, flags=re.IGNORECASE)
                        
                        issues.append(GrammarIssue(
                            lines=str(line_number),
                            sentences=str(sentence_number),
                            text=sentence,
                            problem="Tense inconsistency",
                            reason=f"'{present}' should be '{past}' when referring to past time",
                            proposed_fix=ProposedFix(
                                action="replace",
                                details="Correct verb tense",
                                corrected_text=corrected_sentence
                            ),
                            issue_type=GrammarIssueType.VERB_TENSE,
                            confidence=0.9,
                            # Legacy fields
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=original_text,
                            fix=suggested_text,
                            corrected_text=corrected_sentence
                        ))
        
        return issues
    
    def _check_there_agreement(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for 'there is/are' agreement issues"""
        issues = []
        
        # Pattern: "There is many [plural]" should be "There are many [plural]"
        patterns = [
            (r'\bthere is\s+(many|several|some|all|few|a few)\s+(\w+)\b',
             lambda m: f"there are {m.group(1)} {m.group(2)}"),
            (r'\bthere are\s+(a|an|one)\s+(\w+)\b',
             lambda m: f"there is {m.group(1)} {m.group(2)}"),
        ]
        
        for pattern, fix_func in patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                original_text = match.group(0)
                suggested_text = fix_func(match)
                corrected_sentence = sentence.replace(original_text, suggested_text, 1)
                
                issues.append(GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="There is/are agreement",
                    reason=f"'{original_text}' has incorrect agreement",
                    proposed_fix=ProposedFix(
                        action="replace",
                        details="Correct there is/are agreement",
                        corrected_text=corrected_sentence
                    ),
                    issue_type=GrammarIssueType.VERB_TENSE,
                    confidence=0.9,
                    # Legacy fields
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=original_text,
                    fix=suggested_text,
                    corrected_text=corrected_sentence
                ))
        
        return issues
    
    def _get_singular_verb(self, verb: str) -> str:
        """Convert plural verb to singular"""
        conversions = {
            'are': 'is', 'were': 'was', 'have': 'has', 'do': 'does'
        }
        return conversions.get(verb.lower(), verb)
    
    def _get_plural_verb(self, verb: str) -> str:
        """Convert singular verb to plural"""
        conversions = {
            'is': 'are', 'was': 'were', 'has': 'have', 'does': 'do'
        }
        return conversions.get(verb.lower(), verb)
