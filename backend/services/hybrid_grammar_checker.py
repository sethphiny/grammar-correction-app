import re
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
import language_tool_python
from models.schemas import GrammarIssue, GrammarIssueType, CorrectionSummary, DocumentLine, ProposedFix
from .grammar_config import GrammarCheckerConfig, DEFAULT_CONFIG
from .language_tool_server import LanguageToolServer, LanguageToolServerError
from .text_processor import TextProcessor

# Set up logger for hybrid grammar checking
logger = logging.getLogger(__name__)

# Optional spaCy import
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

class HybridGrammarChecker:
    """Enhanced grammar checker combining spaCy and LanguageTool for maximum accuracy"""
    
    def __init__(self, config: Optional[GrammarCheckerConfig] = None):
        # Use provided config or default
        self.config = config or DEFAULT_CONFIG
        
        # Initialize spaCy if available and enabled
        self.nlp = None
        if SPACY_AVAILABLE and self.config.enable_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            except Exception as e:
                logger.warning(f"Could not initialize spaCy: {e}")
        elif not SPACY_AVAILABLE:
            logger.warning("spaCy not available. Install with: pip install spacy")
        
        # Initialize enhanced components
        self.language_tool_server = LanguageToolServer(self.config)
        self.text_processor = TextProcessor(self.config, self.nlp)
        
        # Legacy tool for backward compatibility
        self.tool = None
        try:
            self.tool = language_tool_python.LanguageTool(self.config.language)
        except Exception as e:
            logger.warning(f"Could not initialize legacy LanguageTool: {e}")
    
    async def initialize(self) -> bool:
        """Initialize the grammar checker components"""
        try:
            # Initialize the language tool server
            server_initialized = await self.language_tool_server.initialize()
            if not server_initialized:
                logger.warning("LanguageTool server initialization failed, but continuing with fallback")
            
            logger.info("Hybrid grammar checker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing hybrid grammar checker: {e}")
            return False
    
    async def check_line(self, line: DocumentLine, line_number: int) -> List[GrammarIssue]:
        """Check a line for grammar issues using hybrid approach"""
        issues = []
        
        for sentence_idx, sentence in enumerate(line.sentences):
            if not sentence.strip():
                continue
                
            # Process sentence with hybrid approach
            sentence_issues = await self._check_sentence_hybrid(sentence, line_number, sentence_idx + 1)
            issues.extend(sentence_issues)
        
        # Deduplicate and merge issues
        unique_issues = self._deduplicate_and_merge_issues(issues)
        
        return unique_issues
    
    async def check_text_chunk(self, chunk_text: str, chunk_lines: List[DocumentLine], start_line_number: int) -> List[GrammarIssue]:
        """Check a chunk of text using hybrid approach with enhanced text processing"""
        logger.info(f"Enhanced hybrid chunk analysis starting - Start line: {start_line_number}, Chunk length: {len(chunk_text)} chars, Lines: {len(chunk_lines)}")
        
        if not chunk_text.strip():
            logger.info("Empty chunk text - returning empty results")
            return []
        
        try:
            # Use enhanced text processor for sentence segmentation
            logger.info("Using enhanced text processor for sentence segmentation")
            sentences = self.text_processor.split_into_sentences(chunk_text)
            
            logger.info(f"Split chunk into {len(sentences)} sentences")
            issues = []
            
            for sentence_idx, sentence_data in enumerate(sentences):
                sentence = sentence_data['text']
                start_offset = sentence_data['start_offset']
                end_offset = sentence_data['end_offset']
                
                # Calculate line numbers based on offsets
                start_line = start_line_number + chunk_text[:start_offset].count('\n')
                end_line = start_line_number + chunk_text[:end_offset].count('\n')
                
                logger.debug(f"Processing sentence {sentence_idx + 1}: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}' (lines {start_line}-{end_line})")
                
                if not sentence.strip():
                    logger.debug(f"Skipping empty sentence {sentence_idx + 1}")
                    continue
                
                # Determine line range for sentences spanning multiple lines
                if start_line == end_line:
                    lines_str = str(start_line)
                else:
                    lines_str = f"{start_line}–{end_line}"
                
                # Check the sentence with hybrid approach
                try:
                    sentence_issues = await self._check_sentence_hybrid_enhanced(sentence, start_line, sentence_idx + 1, sentence_data)
                    logger.debug(f"Sentence {sentence_idx + 1} hybrid analysis complete - Found {len(sentence_issues)} issues")
                    
                    # Update the line information in the issues
                    for issue in sentence_issues:
                        issue.lines = lines_str
                        issue.line_number = start_line
                        issue.line_range = lines_str  # Always set line_range for proper formatting
                    
                    issues.extend(sentence_issues)
                    
                except Exception as e:
                    logger.error(f"Error in hybrid analysis of sentence {sentence_idx + 1}: {e}", exc_info=True)
                    continue
            
            # Deduplicate and merge issues
            unique_issues = self._deduplicate_and_merge_issues(issues)
            logger.info(f"Enhanced hybrid chunk analysis complete - Total issues: {len(issues)}, Unique issues: {len(unique_issues)}")
            
            return unique_issues
            
        except Exception as e:
            logger.error(f"Critical error in enhanced hybrid chunk analysis: {e}", exc_info=True)
            return []
    
    def _split_into_sentences_with_spacy(self, text: str, start_line_number: int) -> List[Dict]:
        """Split text into sentences using spaCy for better accuracy"""
        if not self.nlp:
            return self._split_into_sentences_with_line_info(text, start_line_number)
        
        try:
            doc = self.nlp(text)
            sentence_info = []
            current_line = start_line_number
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if sentence_text and len(sentence_text) > 3:
                    # Calculate line numbers for this sentence
                    sentence_start = text.find(sentence_text)
                    sentence_end = sentence_start + len(sentence_text)
                    
                    # Count newlines to determine line numbers
                    start_line = start_line_number + text[:sentence_start].count('\n')
                    end_line = start_line_number + text[:sentence_end].count('\n')
                    
                    sentence_info.append({
                        'text': sentence_text,
                        'start_line': start_line,
                        'end_line': end_line,
                        'start_offset': sentence_start,
                        'end_offset': sentence_end,
                        'spacy_sent': sent  # Keep spaCy sentence object for analysis
                    })
            
            return sentence_info
        except Exception as e:
            print(f"Error with spaCy sentence segmentation: {e}")
            return self._split_into_sentences_with_line_info(text, start_line_number)
    
    def _split_into_sentences_with_line_info(self, text: str, start_line_number: int) -> List[Dict]:
        """Fallback sentence splitting using regex (from original implementation)"""
        import re
        
        # Calculate line offsets
        line_offsets = self._calculate_line_offsets(text)
        
        # More sophisticated sentence splitting that handles abbreviations
        abbreviations = r'\b(Dr|Mr|Mrs|Ms|Prof|Prof\.|Inc|Inc\.|Corp|Corp\.|Ltd|Ltd\.|Co|Co\.|e\.g\.|i\.e\.|etc\.|vs\.|vs)\b'
        
        # Replace abbreviations temporarily to avoid false sentence breaks
        temp_text = text
        abbr_matches = list(re.finditer(abbreviations, text, re.IGNORECASE))
        abbr_replacements = {}
        
        for i, match in enumerate(abbr_matches):
            placeholder = f"__ABBR_{i}__"
            abbr_replacements[placeholder] = match.group(0)
            temp_text = temp_text.replace(match.group(0), placeholder)
        
        # Split on sentence endings but preserve quotes
        sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_endings, temp_text)
        
        # Restore abbreviations
        for placeholder, original in abbr_replacements.items():
            for i, sentence in enumerate(sentences):
                sentences[i] = sentence.replace(placeholder, original)
        
        # Process sentences and determine line ranges
        sentence_info = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                # Find the line number where this sentence starts
                sentence_start = text.find(sentence)
                start_line = self._find_line_number_for_offset(sentence_start, line_offsets, start_line_number)
                
                # Find the line number where this sentence ends
                sentence_end = sentence_start + len(sentence)
                end_line = self._find_line_number_for_offset(sentence_end - 1, line_offsets, start_line_number)
                
                sentence_info.append({
                    'text': sentence,
                    'start_line': start_line,
                    'end_line': end_line,
                    'start_offset': sentence_start,
                    'end_offset': sentence_end
                })
        
        return sentence_info
    
    def _calculate_line_offsets(self, text: str) -> List[int]:
        """Calculate character offsets for each line in the text"""
        offsets = [0]
        for i, char in enumerate(text):
            if char == '\n':
                offsets.append(i + 1)
        return offsets
    
    def _find_line_number_for_offset(self, offset: int, line_offsets: List[int], start_line_number: int) -> int:
        """Find which line number corresponds to a character offset"""
        for i, line_offset in enumerate(line_offsets):
            if i + 1 < len(line_offsets) and line_offset <= offset < line_offsets[i + 1]:
                return start_line_number + i
            elif i == len(line_offsets) - 1 and offset >= line_offset:
                return start_line_number + i
        return start_line_number
    
    async def _check_sentence_hybrid_enhanced(self, sentence: str, line_number: int, sentence_number: int, sentence_data: Dict) -> List[GrammarIssue]:
        """Enhanced sentence checking using new server architecture and text processing"""
        logger.debug(f"Starting enhanced hybrid sentence analysis - Line: {line_number}, Sentence: {sentence_number}")
        
        all_issues = []
        
        # Clean up the sentence
        cleaned_sentence = self._clean_sentence_prefixes(sentence)
        if cleaned_sentence != sentence:
            logger.debug(f"Sentence cleaned: '{sentence[:30]}...' -> '{cleaned_sentence[:30]}...'")
        
        # Get issues from enhanced LanguageTool server
        languagetool_issues = []
        try:
            logger.debug("Running enhanced LanguageTool analysis")
            matches = await self.language_tool_server.check_text(cleaned_sentence)
            
            for match in matches:
                # Enhanced proper name filtering
                if (self.config.enable_proper_name_filtering and 
                    self.text_processor.is_proper_name(
                        cleaned_sentence[match.offset:match.offset + match.error_length],
                        cleaned_sentence,
                        match.offset
                    )):
                    logger.debug(f"Filtered out proper name: '{cleaned_sentence[match.offset:match.offset + match.error_length]}'")
                    continue
                
                # Create issue from match
                issue = self._create_issue_from_match(match, cleaned_sentence, line_number, sentence_number)
                if issue:
                    languagetool_issues.append(issue)
            
            logger.debug(f"Enhanced LanguageTool analysis complete - Found {len(languagetool_issues)} issues")
        except LanguageToolServerError as e:
            logger.warning(f"Enhanced LanguageTool analysis failed: {e}")
            # Fallback to legacy method
            languagetool_issues = await self._check_with_language_tool_hybrid(cleaned_sentence, line_number, sentence_number)
        except Exception as e:
            logger.error(f"Enhanced LanguageTool analysis failed: {e}", exc_info=True)
        
        # spaCy analysis (if available)
        spacy_issues = []
        if self.nlp and self.config.enable_spacy:
            logger.debug("Running spaCy analysis")
            try:
                spacy_issues = await self._check_with_spacy(cleaned_sentence, line_number, sentence_number)
                logger.debug(f"spaCy analysis complete - Found {len(spacy_issues)} issues")
            except Exception as e:
                logger.error(f"spaCy analysis failed: {e}", exc_info=True)
        
        # Custom rules analysis
        custom_issues = []
        if self.config.enable_custom_rules:
            logger.debug("Running custom grammar rules analysis")
            try:
                custom_issues = await self._check_with_custom_rules(cleaned_sentence, line_number, sentence_number)
                logger.debug(f"Custom rules analysis complete - Found {len(custom_issues)} issues")
            except Exception as e:
                logger.error(f"Custom rules analysis failed: {e}", exc_info=True)
        
        # Combine and analyze results
        all_issues.extend(custom_issues)
        all_issues.extend(spacy_issues)
        all_issues.extend(languagetool_issues)
        logger.debug(f"Combined enhanced analysis - Total issues: {len(all_issues)} (Custom: {len(custom_issues)}, spaCy: {len(spacy_issues)}, LanguageTool: {len(languagetool_issues)})")
        
        # If no issues found, return empty list
        if not all_issues:
            logger.debug("No issues found in enhanced hybrid analysis")
            return []
        
        # Merge overlapping issues and calculate confidence scores
        merged_issues = self._merge_overlapping_issues(all_issues, spacy_issues, languagetool_issues)
        logger.debug(f"Issues merged - {len(all_issues)} -> {len(merged_issues)} unique issues")
        
        # Filter by confidence threshold
        filtered_issues = [issue for issue in merged_issues if issue.confidence >= self.config.confidence_threshold]
        logger.debug(f"Issues filtered by confidence ({self.config.confidence_threshold}) - {len(merged_issues)} -> {len(filtered_issues)} issues")
        
        # Consolidate multiple issues into comprehensive fixes
        if len(filtered_issues) > 1:
            logger.debug("Consolidating multiple issues into single comprehensive fix")
            result = [self._consolidate_sentence_issues_hybrid(cleaned_sentence, filtered_issues, line_number, sentence_number)]
        else:
            result = filtered_issues
        
        logger.debug(f"Enhanced hybrid sentence analysis complete - Returning {len(result)} issues")
        return result

    async def _check_sentence_hybrid(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check a sentence using both spaCy and LanguageTool for maximum accuracy"""
        logger.debug(f"Starting hybrid sentence analysis - Line: {line_number}, Sentence: {sentence_number}")
        
        all_issues = []
        
        # Clean up the sentence
        cleaned_sentence = self._clean_sentence_prefixes(sentence)
        if cleaned_sentence != sentence:
            logger.debug(f"Sentence cleaned: '{sentence[:30]}...' -> '{cleaned_sentence[:30]}...'")
        
        # Get issues from both tools
        spacy_issues = []
        languagetool_issues = []
        custom_issues = []
        
        # Custom grammar rules analysis
        logger.debug("Running custom grammar rules analysis")
        try:
            custom_issues = await self._check_with_custom_rules(cleaned_sentence, line_number, sentence_number)
            logger.debug(f"Custom rules analysis complete - Found {len(custom_issues)} issues")
        except Exception as e:
            logger.error(f"Custom rules analysis failed: {e}", exc_info=True)
        
        # spaCy analysis
        if self.nlp:
            logger.debug("Running spaCy analysis")
            try:
                spacy_issues = await self._check_with_spacy(cleaned_sentence, line_number, sentence_number)
                logger.debug(f"spaCy analysis complete - Found {len(spacy_issues)} issues")
            except Exception as e:
                logger.error(f"spaCy analysis failed: {e}", exc_info=True)
        else:
            logger.debug("spaCy not available - skipping spaCy analysis")
        
        # LanguageTool analysis
        if self.tool:
            logger.debug("Running LanguageTool analysis")
            try:
                languagetool_issues = await self._check_with_language_tool_hybrid(cleaned_sentence, line_number, sentence_number)
                logger.debug(f"LanguageTool analysis complete - Found {len(languagetool_issues)} issues")
            except Exception as e:
                logger.error(f"LanguageTool analysis failed: {e}", exc_info=True)
        else:
            logger.debug("LanguageTool not available - skipping LanguageTool analysis")
        
        # Combine and analyze results
        all_issues.extend(custom_issues)
        all_issues.extend(spacy_issues)
        all_issues.extend(languagetool_issues)
        logger.debug(f"Combined analysis - Total issues: {len(all_issues)} (Custom: {len(custom_issues)}, spaCy: {len(spacy_issues)}, LanguageTool: {len(languagetool_issues)})")
        
        # If no issues found, return empty list
        if not all_issues:
            logger.debug("No issues found in hybrid analysis")
            return []
        
        # Merge overlapping issues and calculate confidence scores
        merged_issues = self._merge_overlapping_issues(all_issues, spacy_issues, languagetool_issues)
        logger.debug(f"Issues merged - {len(all_issues)} -> {len(merged_issues)} unique issues")
        
        # Consolidate multiple issues into comprehensive fixes
        if len(merged_issues) > 1:
            logger.debug("Consolidating multiple issues into single comprehensive fix")
            result = [self._consolidate_sentence_issues_hybrid(cleaned_sentence, merged_issues, line_number, sentence_number)]
        else:
            result = merged_issues
        
        logger.debug(f"Hybrid sentence analysis complete - Returning {len(result)} issues")
        return result
    
    async def _check_with_spacy(self, text: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check text using spaCy for linguistic analysis"""
        if not self.nlp or len(text.strip()) < 3:
            return []
        
        try:
            doc = self.nlp(text)
            issues = []
            
            # Check for dependency parsing issues
            dep_issues = self._check_dependency_issues(doc, line_number, sentence_number)
            issues.extend(dep_issues)
            
            # Check for named entity recognition to avoid false positives
            ner_issues = self._check_ner_issues(doc, line_number, sentence_number)
            issues.extend(ner_issues)
            
            # Check for part-of-speech inconsistencies
            pos_issues = self._check_pos_issues(doc, line_number, sentence_number)
            issues.extend(pos_issues)
            
            # Check for morphological analysis issues
            morph_issues = self._check_morphological_issues(doc, line_number, sentence_number)
            issues.extend(morph_issues)
            
            return issues
            
        except Exception as e:
            print(f"Error checking with spaCy: {e}")
            return []
    
    def _check_dependency_issues(self, doc, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for dependency parsing issues"""
        issues = []
        
        # Check for subject-verb agreement using dependency parsing
        for token in doc:
            if token.dep_ == "nsubj":  # Subject
                # Find the verb this subject is connected to
                head = token.head
                if head.pos_ == "VERB":
                    # Check if subject and verb agree in number
                    if self._check_subject_verb_agreement_spacy(token, head):
                        continue  # Agreement is correct
                    else:
                        # Create issue for subject-verb disagreement
                        issue = GrammarIssue(
                            lines=str(line_number),
                            sentences=str(sentence_number),
                            text=doc.text,
                            problem="Subject-verb agreement",
                            reason=f"The subject '{token.text}' and verb '{head.text}' don't agree in number.",
                            proposed_fix=ProposedFix(
                                action="Fix subject-verb agreement",
                                details=f"Ensure '{token.text}' and '{head.text}' agree in number.",
                                corrected_text=doc.text  # Will be improved with better correction logic
                            ),
                            issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                            confidence=0.9,
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=doc.text,
                            fix=f"Fix subject-verb agreement between '{token.text}' and '{head.text}'."
                        )
                        issues.append(issue)
        
        return issues
    
    def _check_subject_verb_agreement_spacy(self, subject_token, verb_token) -> bool:
        """Check if subject and verb agree in number using spaCy"""
        # Simple heuristic: check if both are singular or both are plural
        subject_is_plural = subject_token.morph.get("Number") == ["Plur"] or subject_token.text.lower() in ["they", "we", "you"]
        verb_is_plural = verb_token.morph.get("Number") == ["Plur"] or verb_token.text.lower() in ["are", "were", "have", "do"]
        
        # Check for common plural subjects
        plural_subjects = ["they", "we", "you", "people", "students", "children", "men", "women"]
        if subject_token.text.lower() in plural_subjects:
            subject_is_plural = True
        
        # Check for common singular subjects
        singular_subjects = ["he", "she", "it", "person", "student", "child", "man", "woman"]
        if subject_token.text.lower() in singular_subjects:
            subject_is_plural = False
        
        # Check for common plural verbs
        plural_verbs = ["are", "were", "have", "do", "go", "come", "say", "take"]
        if verb_token.text.lower() in plural_verbs:
            verb_is_plural = True
        
        # Check for common singular verbs
        singular_verbs = ["is", "was", "has", "does", "goes", "comes", "says", "takes"]
        if verb_token.text.lower() in singular_verbs:
            verb_is_plural = False
        
        # Base form verbs that work with both singular and plural subjects
        base_form_verbs = ["check", "work", "help", "make", "find", "give", "tell", "show", "ask", "try", "use", "get", "put", "call", "look", "want", "need", "feel", "seem", "become", "leave", "keep", "bring", "start", "turn", "move", "play", "run", "walk", "talk", "listen", "read", "write", "think", "know", "see", "hear", "smell", "taste", "touch"]
        if verb_token.text.lower() in base_form_verbs:
            return True  # Base form verbs agree with both singular and plural subjects
        
        return subject_is_plural == verb_is_plural
    
    def _check_ner_issues(self, doc, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for named entity recognition issues (to avoid false positives)"""
        issues = []
        
        # This method helps identify proper names that shouldn't be flagged as grammar errors
        # It's more of a helper method to improve accuracy rather than finding issues
        
        return issues
    
    def _check_pos_issues(self, doc, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for part-of-speech inconsistencies"""
        issues = []
        
        # Check for incorrect article usage
        for token in doc:
            if token.pos_ == "DET" and token.text.lower() in ["a", "an"]:
                next_token = None
                if token.i + 1 < len(doc):
                    next_token = doc[token.i + 1]
                
                if next_token and next_token.pos_ in ["NOUN", "ADJ"]:
                    # Check if article matches the following word
                    if token.text.lower() == "a" and next_token.text.lower().startswith(("a", "e", "i", "o", "u")):
                        # Should be "an" instead of "a"
                        corrected_text = doc.text.replace(f" {token.text} ", f" an ", 1)
                        issue = GrammarIssue(
                            lines=str(line_number),
                            sentences=str(sentence_number),
                            text=doc.text,
                            problem="Article usage",
                            reason=f"Use 'an' before words starting with a vowel sound.",
                            proposed_fix=ProposedFix(
                                action="Fix article usage",
                                details=f"Change 'a' to 'an' before '{next_token.text}'.",
                                corrected_text=corrected_text
                            ),
                            issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                            confidence=0.9,
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=doc.text,
                            fix=f"Change 'a' to 'an' before '{next_token.text}'."
                        )
                        issues.append(issue)
                    elif token.text.lower() == "an" and not next_token.text.lower().startswith(("a", "e", "i", "o", "u")):
                        # Should be "a" instead of "an"
                        corrected_text = doc.text.replace(f" {token.text} ", f" a ", 1)
                        issue = GrammarIssue(
                            lines=str(line_number),
                            sentences=str(sentence_number),
                            text=doc.text,
                            problem="Article usage",
                            reason=f"Use 'a' before words starting with a consonant sound.",
                            proposed_fix=ProposedFix(
                                action="Fix article usage",
                                details=f"Change 'an' to 'a' before '{next_token.text}'.",
                                corrected_text=corrected_text
                            ),
                            issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                            confidence=0.9,
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=doc.text,
                            fix=f"Change 'an' to 'a' before '{next_token.text}'."
                        )
                        issues.append(issue)
        
        return issues
    
    def _check_morphological_issues(self, doc, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check for morphological analysis issues"""
        issues = []
        
        # Check for tense consistency using morphological features
        verbs = [token for token in doc if token.pos_ == "VERB"]
        if len(verbs) > 1:
            tenses = []
            for verb in verbs:
                tense = verb.morph.get("Tense")
                if tense:
                    tenses.extend(tense)
            
            # Check for tense inconsistency
            if len(set(tenses)) > 1 and "Past" in tenses and "Pres" in tenses:
                issue = GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=doc.text,
                    problem="Verb tense consistency",
                    reason="The sentence mixes past and present tense verbs.",
                    proposed_fix=ProposedFix(
                        action="Maintain consistent verb tense",
                        details="Choose either past or present tense and maintain it throughout the sentence.",
                        corrected_text=doc.text  # Will be improved with better correction logic
                    ),
                    issue_type=GrammarIssueType.VERB_TENSE,
                    confidence=0.8,
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=doc.text,
                    fix="Maintain consistent verb tense throughout the sentence."
                )
                issues.append(issue)
        
        return issues
    
    def _create_issue_from_match(self, match, text: str, line_number: int, sentence_number: int) -> Optional[GrammarIssue]:
        """Create a GrammarIssue from a LanguageTool match"""
        try:
            # Extract the problematic text
            problematic_text = text[match.offset:match.offset + match.error_length]
            
            # Get the suggested fix
            corrected_sentence = text
            fix_suggestion = ""
            
            if match.replacements:
                corrected_sentence = text[:match.offset] + match.replacements[0] + text[match.offset + match.error_length:]
                fix_suggestion = match.replacements[0]
            else:
                # Handle cases where no replacement is provided
                if "unpaired" in match.rule_id.lower() or "quotation" in match.rule_id.lower():
                    # For quotation marks, try to determine the fix
                    quote_chars = ['"', '"', "'", "'"]
                    if problematic_text in quote_chars:
                        fix_suggestion = "Remove the quotation mark"
                    else:
                        fix_suggestion = "Fix the punctuation"
                else:
                    fix_suggestion = "Review and correct"
            
            # Create the issue
            issue_type = self._categorize_issue(match.rule_id, match.message)
            
            proposed_fix = ProposedFix(
                action="Grammar correction",
                details=f"Replace \"{problematic_text}\" with \"{fix_suggestion}\".",
                corrected_text=corrected_sentence
            )
            
            # Create a more detailed problem description
            problem_type, reason = self._create_problem_type_and_reason(match, text, match.offset, match.error_length)
            
            return GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=text,
                problem=problem_type,
                reason=reason,
                proposed_fix=proposed_fix,
                issue_type=issue_type,
                confidence=match.confidence,
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=text,
                fix=f"→ \"{fix_suggestion}\""
            )
            
        except Exception as e:
            logger.error(f"Error creating issue from match: {e}")
            return None
    
    async def _check_with_language_tool_hybrid(self, text: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check text using LanguageTool with enhanced filtering"""
        if not self.tool or len(text.strip()) < 3:
            logger.debug("LanguageTool not available or text too short")
            return []
        
        try:
            logger.debug(f"LanguageTool checking text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Limit text length to prevent LanguageTool from processing extremely long sentences
            max_text_length = 1000
            if len(text) > max_text_length:
                truncated_text = text[:max_text_length] + "..."
                logger.debug(f"Text truncated from {len(text)} to {len(truncated_text)} chars")
                matches = await asyncio.to_thread(self.tool.check, truncated_text)
            else:
                matches = await asyncio.to_thread(self.tool.check, text)
            
            logger.debug(f"LanguageTool found {len(matches)} potential issues")
            
            issues = []
            max_issues_per_sentence = 5
            issue_count = 0
            filtered_count = 0
            
            for match in matches:
                if issue_count >= max_issues_per_sentence:
                    logger.debug(f"Reached max issues limit ({max_issues_per_sentence})")
                    break
                
                # Extract the problematic text
                problematic_text = text[match.offset:match.offset + match.errorLength]
                logger.debug(f"Checking potential issue: '{problematic_text}' (rule: {match.ruleId})")
                
                # Enhanced filtering using spaCy if available
                if self.nlp and self._is_proper_name_spacy(problematic_text, text, match.offset):
                    logger.debug(f"Filtered out proper name (spaCy): '{problematic_text}'")
                    filtered_count += 1
                    continue
                
                # Skip if this is a proper name (fallback method)
                if self._is_proper_name(problematic_text, text, match.offset):
                    logger.debug(f"Filtered out proper name (fallback): '{problematic_text}'")
                    filtered_count += 1
                    continue
                
                issue_type = self._categorize_issue(match.ruleId, match.message)
                logger.debug(f"Creating issue: {issue_type} - '{problematic_text}'")
                
                # Get the suggested fix
                corrected_sentence = text
                fix_suggestion = ""
                
                if match.replacements:
                    corrected_sentence = text[:match.offset] + match.replacements[0] + text[match.offset + match.errorLength:]
                    fix_suggestion = match.replacements[0]
                else:
                    # Handle cases where no replacement is provided
                    if "unpaired" in match.ruleId.lower() or "quotation" in match.ruleId.lower():
                        # For quotation marks, try to determine the fix
                        quote_chars = ['"', '"', "'", "'"]
                        if problematic_text in quote_chars:
                            fix_suggestion = "Remove the quotation mark"
                        else:
                            fix_suggestion = "Fix the punctuation"
                    else:
                        fix_suggestion = "Review and correct"
                
                # Create the issue
                proposed_fix = ProposedFix(
                    action="Grammar correction",
                    details=f"Replace \"{problematic_text}\" with \"{fix_suggestion}\".",
                    corrected_text=corrected_sentence
                )
                
                # Create a more detailed problem description
                problem_type, reason = self._create_problem_type_and_reason(match, text, match.offset, match.errorLength)
                
                issues.append(GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=text,
                    problem=problem_type,
                    reason=reason,
                    proposed_fix=proposed_fix,
                    issue_type=issue_type,
                    confidence=0.8,
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=text,
                    fix=f"→ \"{fix_suggestion}\""
                ))
                
                issue_count += 1
            
            logger.debug(f"LanguageTool analysis complete - {len(matches)} matches, {filtered_count} filtered, {len(issues)} issues created")
            return issues
            
        except Exception as e:
            logger.error(f"Error checking with LanguageTool: {e}", exc_info=True)
            return []
    
    def _is_proper_name_spacy(self, text: str, full_sentence: str, offset: int) -> bool:
        """Enhanced proper name detection using spaCy"""
        if not self.nlp:
            return self._is_proper_name(text, full_sentence, offset)
        
        try:
            # Get the token at the offset
            doc = self.nlp(full_sentence)
            for token in doc:
                if token.idx <= offset < token.idx + len(token.text):
                    # Check if it's a named entity
                    if token.ent_type_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART"]:
                        return True
                    
                    # Check if it's a proper noun
                    if token.pos_ == "PROPN":
                        return True
                    
                    break
            
            return False
        except Exception:
            return self._is_proper_name(text, full_sentence, offset)
    
    def _is_proper_name(self, text: str, full_sentence: str, offset: int) -> bool:
        """Fallback proper name detection (from original implementation)"""
        text = text.strip()
        
        if len(text) < 2:
            return False
        
        if not text[0].isupper():
            return False
        
        # Get context around the text
        start_context = max(0, offset - 50)
        end_context = min(len(full_sentence), offset + len(text) + 50)
        context = full_sentence[start_context:end_context]
        
        # Common patterns that indicate proper names
        name_indicators = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b(Dr|Mr|Mrs|Ms|Prof|Professor)\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+(Jr|Sr|III|IV|V)\b',
        ]
        
        for pattern in name_indicators:
            if re.search(pattern, context, re.IGNORECASE):
                return True
        
        return False
    
    def _merge_overlapping_issues(self, all_issues: List[GrammarIssue], spacy_issues: List[GrammarIssue], languagetool_issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Merge overlapping issues from both tools and calculate confidence scores"""
        if not all_issues:
            return []
        
        # Group issues by similar problems
        issue_groups = {}
        for issue in all_issues:
            # Create a key based on problem type and location
            key = (issue.issue_type, issue.problem[:50])  # Use first 50 chars of problem
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)
        
        merged_issues = []
        for group_issues in issue_groups.values():
            if len(group_issues) == 1:
                # Single issue - keep as is
                merged_issues.append(group_issues[0])
            else:
                # Multiple similar issues - merge them
                merged_issue = self._merge_similar_issues(group_issues, spacy_issues, languagetool_issues)
                merged_issues.append(merged_issue)
        
        return merged_issues
    
    def _merge_similar_issues(self, issues: List[GrammarIssue], spacy_issues: List[GrammarIssue], languagetool_issues: List[GrammarIssue]) -> GrammarIssue:
        """Merge similar issues and calculate confidence based on tool agreement"""
        # Calculate confidence based on tool agreement
        spacy_count = sum(1 for issue in issues if issue in spacy_issues)
        lt_count = sum(1 for issue in issues if issue in languagetool_issues)
        
        # Higher confidence if both tools agree
        if spacy_count > 0 and lt_count > 0:
            confidence = 0.95  # Both tools agree
        elif spacy_count > 0 or lt_count > 0:
            confidence = 0.8   # One tool found it
        else:
            confidence = 0.7   # Fallback
        
        # Use the first issue as base and enhance it
        base_issue = issues[0]
        base_issue.confidence = confidence
        
        # Enhance the problem description if multiple tools found it
        if len(issues) > 1:
            base_issue.reason += f" (Confirmed by multiple analysis methods)"
        
        return base_issue
    
    def _consolidate_sentence_issues_hybrid(self, original_sentence: str, issues: List[GrammarIssue], line_number: int, sentence_number: int) -> GrammarIssue:
        """Consolidate multiple issues into a single comprehensive fix using hybrid approach"""
        # Sort issues by priority and confidence
        sorted_issues = sorted(issues, key=lambda x: (self._get_issue_priority(x.issue_type), -x.confidence))
        
        # Create a comprehensive fix
        corrected_sentence = original_sentence
        all_problems = []
        all_reasons = []
        all_actions = []
        all_details = []
        
        for issue in sorted_issues:
            all_problems.append(issue.problem)
            all_reasons.append(issue.reason)
            all_actions.append(issue.proposed_fix.action)
            all_details.append(issue.proposed_fix.details)
            
            # Apply the fix to the sentence
            corrected_sentence = issue.proposed_fix.corrected_text
        
        # Create comprehensive descriptions
        if len(all_problems) == 1:
            problem_type = all_problems[0]
            reason = all_reasons[0]
        else:
            problem_type = "Multiple issues found"
            reason = "; ".join(set(all_reasons))
        
        if len(all_actions) == 1:
            action = all_actions[0]
            details = all_details[0]
        else:
            action = "Multiple corrections needed"
            details = f"Apply all corrections."
        
        proposed_fix = ProposedFix(
            action=action,
            details=details,
            corrected_text=corrected_sentence
        )
        
        # Determine primary issue type
        primary_issue_type = sorted_issues[0].issue_type
        
        # Calculate weighted average confidence
        total_confidence = sum(issue.confidence for issue in issues)
        avg_confidence = total_confidence / len(issues)
        
        # Boost confidence if multiple tools agreed
        if len(issues) > 1:
            avg_confidence = min(0.95, avg_confidence + 0.1)
        
        legacy_fix = f"Multiple corrections needed."
        
        return GrammarIssue(
            lines=str(line_number),
            sentences=str(sentence_number),
            text=original_sentence,
            problem=problem_type,
            reason=reason,
            proposed_fix=proposed_fix,
            issue_type=primary_issue_type,
            confidence=avg_confidence,
            line_number=line_number,
            sentence_number=sentence_number,
            original_text=original_sentence,
            fix=legacy_fix,
            corrected_text=corrected_sentence
        )
    
    def _get_issue_priority(self, issue_type: GrammarIssueType) -> int:
        """Get priority for issue types (lower number = higher priority)"""
        priority_map = {
            GrammarIssueType.GRAMMAR_PUNCTUATION: 1,
            GrammarIssueType.VERB_TENSE: 2,
            GrammarIssueType.REDUNDANCY: 3,
            GrammarIssueType.AWKWARD_PHRASING: 4
        }
        return priority_map.get(issue_type, 5)
    
    def _clean_sentence_prefixes(self, sentence: str) -> str:
        """Remove common prefixes that aren't part of the actual sentence content"""
        prefixes_to_remove = [
            r'^Redundant phrases\s*:\s*',
            r'^Grammar issues\s*:\s*',
            r'^Punctuation errors\s*:\s*',
            r'^Verb tense issues\s*:\s*',
            r'^Awkward phrasing\s*:\s*',
            r'^Issues found\s*:\s*',
            r'^Problems\s*:\s*',
            r'^Errors\s*:\s*',
            r'^Spelling errors\s*:\s*',
            r'^Incorrect prepositions\s*:\s*',
            r'^Preposition errors\s*:\s*',
            r'^Subject-verb agreement\s*:\s*',
            r'^Agreement issues\s*:\s*',
            r'^Capitalization errors\s*:\s*',
            r'^Capitalization issues\s*:\s*',
            r'^Word choice\s*:\s*',
            r'^Word choice issues\s*:\s*',
            r'^Style issues\s*:\s*',
            r'^Style problems\s*:\s*',
            r'^Clarity issues\s*:\s*',
            r'^Clarity problems\s*:\s*',
            r'^Conciseness issues\s*:\s*',
            r'^Conciseness problems\s*:\s*',
            r'^Flow issues\s*:\s*',
            r'^Flow problems\s*:\s*',
            r'^Tone issues\s*:\s*',
            r'^Tone problems\s*:\s*',
            r'^Issue\s*:\s*',
            r'^Problem\s*:\s*',
            r'^Error\s*:\s*',
            r'^Fix\s*:\s*',
            r'^Correction\s*:\s*',
            r'^Note\s*:\s*',
            r'^Comment\s*:\s*',
            r'^Suggestion\s*:\s*',
            r'^Recommendation\s*:\s*',
            r'^\d+\.\s*',
            r'^\(\d+\)\s*',
            r'^[a-zA-Z]\)\s*',
            r'^[ivx]+\.\s*',
        ]
        
        cleaned = sentence
        for prefix_pattern in prefixes_to_remove:
            cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _deduplicate_and_merge_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Remove duplicate issues and merge similar ones"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            # Create a key based on problem and fix content
            key = (issue.problem.strip(), issue.fix.strip(), issue.original_text.strip())
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _categorize_issue(self, rule_id: str, message: str) -> GrammarIssueType:
        """Categorize issues by type"""
        if any(keyword in rule_id.lower() for keyword in ['tense', 'verb']):
            return GrammarIssueType.VERB_TENSE
        elif any(keyword in rule_id.lower() for keyword in ['punctuation', 'comma', 'quotation']):
            return GrammarIssueType.GRAMMAR_PUNCTUATION
        elif any(keyword in message.lower() for keyword in ['awkward', 'wordy', 'unclear']):
            return GrammarIssueType.AWKWARD_PHRASING
        elif any(keyword in message.lower() for keyword in ['redundant', 'repetitive']):
            return GrammarIssueType.REDUNDANCY
        else:
            return GrammarIssueType.GRAMMAR_PUNCTUATION
    
    def _create_problem_type_and_reason(self, match, text: str, offset: int, error_length: int) -> tuple[str, str]:
        """Create problem type and reason for the new format"""
        problematic_text = text[offset:offset + error_length]
        
        # Get context around the error
        start_context = max(0, offset - 30)
        end_context = min(len(text), offset + error_length + 30)
        context = text[start_context:end_context]
        
        # Create problem type and reason based on the rule
        if "tense" in match.ruleId.lower() or "verb" in match.ruleId.lower():
            return f"Tense shift → \"{problematic_text}\" (present) vs. surrounding past tense.", ""
        elif "punctuation" in match.ruleId.lower() or "comma" in match.ruleId.lower():
            return "Extra comma before closing quotation mark.", ""
        elif "unpaired" in match.ruleId.lower() or "quotation" in match.ruleId.lower() or "quote" in match.ruleId.lower():
            return f"Unpaired quotation mark: '{problematic_text}'", "Missing or misplaced quotation mark."
        elif "agreement" in match.ruleId.lower():
            return "Subject-verb disagreement", f"\"{problematic_text}\" doesn't agree with the subject."
        elif "redundant" in match.ruleId.lower() or "wordy" in match.ruleId.lower():
            return "Redundant phrasing", f"\"{problematic_text}\" can be expressed more concisely."
        elif "spelling" in match.ruleId.lower():
            return "Spelling error", f"\"{problematic_text}\" might not be the word you intended."
        elif "capitalization" in match.ruleId.lower():
            return "Capitalization error", f"Capitalization issue with \"{problematic_text}\"."
        else:
            # Handle generic LanguageTool messages
            if "unpaired" in match.message.lower() or "missing" in match.message.lower():
                return f"Punctuation error: '{problematic_text}'", "Missing or misplaced punctuation mark."
            else:
                return f"Grammar issue: {match.message}", f"\"{problematic_text}\" needs attention."
    
    def generate_summary(self, issues: List[GrammarIssue]) -> Dict:
        """Generate summary of all issues found"""
        summary = {
            'verb_tense_consistency': 0,
            'awkward_phrasing': 0,
            'redundancy': 0,
            'grammar_punctuation': 0,
            'total_issues': len(issues)
        }
        
        for issue in issues:
            if issue.issue_type == GrammarIssueType.VERB_TENSE:
                summary['verb_tense_consistency'] += 1
            elif issue.issue_type == GrammarIssueType.AWKWARD_PHRASING:
                summary['awkward_phrasing'] += 1
            elif issue.issue_type == GrammarIssueType.REDUNDANCY:
                summary['redundancy'] += 1
            elif issue.issue_type == GrammarIssueType.GRAMMAR_PUNCTUATION:
                summary['grammar_punctuation'] += 1
        
        return summary
    
    async def _check_with_custom_rules(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check sentence with custom grammar rules to catch errors missed by LanguageTool"""
        issues = []
        
        # Rule 1: Collective nouns with plural verbs (e.g., "The team are working")
        if self.config.custom_rules_enabled.get('collective_nouns', True):
            collective_nouns = [
                'team', 'group', 'committee', 'staff', 'crew', 'band', 'family', 
                'government', 'company', 'organization', 'department', 'board',
                'audience', 'class', 'crowd', 'jury', 'public', 'army', 'navy'
            ]
            
            for noun in collective_nouns:
                # Pattern: "The [collective_noun] are [verb]"
                pattern = rf'\bThe\s+{noun}\s+are\s+(\w+)'
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    verb = match.group(1)
                    corrected = sentence.replace(match.group(0), f"The {noun} is {verb}")
                    
                    issue = GrammarIssue(
                        lines=str(line_number),
                        sentences=str(sentence_number),
                        text=sentence,
                        problem=f"Collective noun '{noun}' with plural verb 'are'",
                        reason=f"Should use singular 'is' instead of 'are'",
                        proposed_fix=ProposedFix(
                            action="Fix subject-verb agreement",
                            details=f"Change 'are' to 'is' for collective noun '{noun}'",
                            corrected_text=corrected
                        ),
                        issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                        confidence=0.9,
                        line_number=line_number,
                        sentence_number=sentence_number,
                        original_text=sentence,
                        fix=f"→ \"{corrected}\"",
                        corrected_text=corrected
                    )
                    issues.append(issue)
                    break  # Only report one collective noun issue per sentence
        
        # Rule 2: Subject-verb disagreement in relative clauses (e.g., "document that contain")
        if self.config.custom_rules_enabled.get('subject_verb_agreement', True):
            # Pattern: "that contain" -> "that contains" (when the subject is singular)
            pattern = r'\bthat\s+contain\b'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                # Look for the subject before "that" - find the last noun before "that"
                before_that = sentence[:match.start()].strip()
                # Simple heuristic: if the last word before "that" is a singular noun
                words_before = before_that.split()
                if words_before:
                    last_word = words_before[-1].lower()
                    singular_words = ['document', 'report', 'paper', 'article', 'book', 'file', 'text', 'content', 'this', 'that', 'it', 'test']
                    if last_word in singular_words or (not last_word.endswith('s') and len(last_word) > 2):
                        corrected = sentence.replace(match.group(0), "that contains")
                        
                        issue = GrammarIssue(
                            lines=str(line_number),
                            sentences=str(sentence_number),
                            text=sentence,
                            problem=f"Singular subject '{last_word}' with plural verb 'contain'",
                            reason=f"Should use singular 'contains' instead of 'contain'",
                            proposed_fix=ProposedFix(
                                action="Fix subject-verb agreement",
                                details=f"Change 'contain' to 'contains' for singular subject '{last_word}'",
                                corrected_text=corrected
                            ),
                            issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                            confidence=0.85,
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=sentence,
                            fix=f"→ \"{corrected}\"",
                            corrected_text=corrected
                        )
                        issues.append(issue)
        
        # Rule 3: Adjective instead of adverb (e.g., "performing good" -> "performing well")
        if self.config.custom_rules_enabled.get('article_usage', True):
            # Pattern: "performing good" -> "performing well"
            pattern = r'\bperforming\s+good\b'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                corrected = sentence.replace(match.group(0), "performing well")
                
                issue = GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="Adjective 'good' instead of adverb 'well'",
                    reason="Use adverb 'well' after verb 'performing'",
                    proposed_fix=ProposedFix(
                        action="Fix adjective/adverb usage",
                        details="Change 'good' to 'well' after the verb 'performing'",
                        corrected_text=corrected
                    ),
                    issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                    confidence=0.9,
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=sentence,
                    fix=corrected
                )
                issues.append(issue)
        
        # Rule 4: "There is" with plural subjects (e.g., "There is many problems")
        if self.config.custom_rules_enabled.get('redundancy_detection', True):
            pattern = r'\bThere\s+is\s+many\b'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                corrected = sentence.replace(match.group(0), "There are many")
                
                issue = GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="Singular 'is' with plural 'many'",
                    reason="Use 'are' with plural 'many' instead of singular 'is'",
                    proposed_fix=ProposedFix(
                        action="Fix subject-verb agreement",
                        details="Change 'There is' to 'There are' with plural 'many'",
                        corrected_text=corrected
                    ),
                    issue_type=GrammarIssueType.GRAMMAR_PUNCTUATION,
                    confidence=0.9,
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=sentence,
                    fix=corrected
                )
                issues.append(issue)
        
        return issues
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self, 'language_tool_server'):
            await self.language_tool_server.close()
        logger.info("Hybrid grammar checker closed")
