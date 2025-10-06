"""
Hybrid grammar checker combining spaCy NLP and LanguageTool
"""

import os
import re
import asyncio
from typing import List, Dict, Any, Optional, Callable
import spacy
from language_tool_python import LanguageTool
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

    # 5️⃣ Optionally normalize curly quotes and dashes
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace("–", "-").replace("—", "-")

    return text

def convert_passive_to_active(sentence: str, doc) -> Optional[str]:
    """
    Convert passive voice sentence to active voice where possible.
    
    Args:
        sentence: The original sentence
        doc: spaCy document object
        
    Returns:
        Converted sentence in active voice, or None if conversion not possible
    """
    try:
        # Find passive constructions - look for VBN verbs with auxpass children
        passive_verbs = []
        for token in doc:
            if token.tag_ == "VBN":  # Past participle
                # Check if this verb has an auxiliary verb with auxpass dependency
                for child in token.children:
                    if child.dep_ == "auxpass":
                        passive_verbs.append(token)
                        break
        
        if not passive_verbs:
            return None
            
        # Get the main passive verb
        passive_verb = passive_verbs[0]
        
        # Find the auxiliary verb (usually "was", "were", "is", "are", etc.)
        aux_verb = None
        for child in passive_verb.children:
            if child.dep_ == "auxpass":
                aux_verb = child
                break
        
        if not aux_verb:
            return None
            
        # Find the agent (the "by" phrase)
        agent_phrase = None
        for child in passive_verb.children:
            if child.dep_ == "agent":
                # Get the full agent phrase (including "by")
                agent_phrase = child
                break
        
        # Find the subject (what was acted upon)
        subject = None
        for child in passive_verb.children:
            if child.dep_ == "nsubjpass":
                subject = child
                break
        
        if not subject:
            return None
            
        # Build the active voice sentence
        if agent_phrase:
            # Extract the agent without "by"
            agent_text = ""
            for token in agent_phrase.subtree:
                if token.text.lower() != "by":
                    agent_text += token.text + " "
            new_subject = agent_text.strip()
        else:
            # If no agent, use a generic subject
            new_subject = "the author"
        
        # Get the main verb and determine the correct tense
        main_verb = passive_verb.lemma_
        
        # Check for negation
        has_negation = any(token.dep_ == "neg" and token.head == passive_verb for token in doc)
        
        # Determine the tense based on the auxiliary verb
        aux_verb_text = aux_verb.text.lower()
        if aux_verb_text in ["is", "are"]:
            # Present tense passive -> present tense active
            if main_verb == "written":
                active_verb = "writes"
            elif main_verb == "taken":
                active_verb = "takes"
            elif main_verb == "given":
                active_verb = "gives"
            elif main_verb == "seen":
                active_verb = "sees"
            elif main_verb == "done":
                active_verb = "does"
            elif main_verb == "made":
                active_verb = "makes"
            elif main_verb == "said":
                active_verb = "says"
            elif main_verb == "told":
                active_verb = "tells"
            elif main_verb == "known":
                active_verb = "knows"
            elif main_verb == "thought":
                active_verb = "thinks"
            else:
                active_verb = main_verb + "s" if not main_verb.endswith("s") else main_verb
        else:
            # Past tense passive -> past tense active
            irregular_verbs = {
                "written": "wrote",
                "taken": "took", 
                "given": "gave",
                "seen": "saw",
                "done": "did",
                "made": "made",
                "said": "said",
                "told": "told",
                "known": "knew",
                "thought": "thought",
                "completed": "completed",
                "reviewed": "reviewed",
                "accepted": "accepted",
                "sent": "sent",
                "built": "built",
                "created": "created"
            }
            active_verb = irregular_verbs.get(main_verb, main_verb + "ed")
            
            # Handle negation in past tense
            if has_negation:
                active_verb = f"did not {main_verb}"
        
        # For complex sentences, use a more sophisticated approach
        # Find the passive construction span - start from the subject, end at the verb
        passive_start = subject.i  # Start from the subject (e.g., "it")
        passive_end = passive_verb.i  # End at the passive verb (e.g., "written")
        
        # Extend to include the "by" phrase if it exists
        if agent_phrase:
            for token in agent_phrase.subtree:
                passive_end = max(passive_end, token.i)
        
        # Build the new sentence by replacing the passive construction
        new_sentence_parts = []
        
        # Add everything before the passive construction
        for i in range(passive_start):
            new_sentence_parts.append(doc[i].text)
        
        # For the active construction, we need to be more careful about the structure
        # If there's an agent phrase, use it as the subject and keep the original object
        if agent_phrase:
            # Extract the agent without "by"
            agent_text = ""
            for token in agent_phrase.subtree:
                if token.text.lower() != "by":
                    agent_text += token.text + " "
            new_subject = agent_text.strip()
            
            # Add the new subject and verb
            new_sentence_parts.append(new_subject)
            new_sentence_parts.append(active_verb)
            
            # Add the original subject as the object
            new_sentence_parts.append(subject.text)
        else:
            # No agent phrase - use generic subject
            new_sentence_parts.append(new_subject)
            new_sentence_parts.append(active_verb)
        
        # Handle other modifiers (negation is now included in the verb)
        for token in doc:
            if token.head == passive_verb and token.dep_ in ["advmod"] and token.dep_ != "neg":
                # Add adverbs that modify the verb (but not negation, as it's in the verb)
                new_sentence_parts.append(token.text)
        
        # Add everything after the passive construction
        for i in range(passive_end + 1, len(doc)):
            new_sentence_parts.append(doc[i].text)
        
        # Join and clean up
        result = " ".join(new_sentence_parts)
        
        # Clean up spacing around punctuation
        import re
        result = re.sub(r'\s+([,.!?;:])', r'\1', result)  # Remove space before punctuation
        result = re.sub(r'([,.!?;:])\s*([,.!?;:])', r'\1\2', result)  # Remove space between punctuation
        result = " ".join(result.split())  # Clean up multiple spaces
        
        # Ensure proper capitalization
        if result:
            result = result[0].upper() + result[1:]
        
        return result
        
    except Exception as e:
        print(f"Error converting passive to active voice: {e}")
        return None

def fix_tense_consistency(sentence: str, doc) -> Optional[str]:
    """
    Fix tense consistency issues by converting all verbs to the same tense.
    
    Args:
        sentence: The original sentence
        doc: spaCy document object
        
    Returns:
        Corrected sentence with consistent tense, or None if correction not possible
    """
    try:
        # Find all finite verbs (main verbs with tense information)
        finite_verbs = []
        for token in doc:
            if token.pos_ == "VERB" and token.tag_ in ["VBD", "VBP", "VBZ"]:  # Past, Present, Present 3rd person
                finite_verbs.append(token)
        
        if len(finite_verbs) < 2:
            return None  # Need at least 2 finite verbs to fix consistency
        
        # Determine the most common tense to use as the target
        tense_counts = {}
        for verb in finite_verbs:
            tense_values = verb.morph.get("Tense")
            if tense_values:
                tense = tense_values[0] if isinstance(tense_values, list) else tense_values
                tense_counts[tense] = tense_counts.get(tense, 0) + 1
        
        # Choose the most common tense, defaulting to present if tied
        target_tense = max(tense_counts.items(), key=lambda x: (x[1], x[0] == 'Pres'))[0]
        
        # Convert all verbs to the target tense
        corrected_tokens = []
        for token in doc:
            if token in finite_verbs:
                # Convert verb to target tense
                if target_tense == 'Pres':
                    # Convert to present tense
                    if token.tag_ == "VBD":  # Past tense
                        # Simple past to present conversion
                        if token.lemma_ == "be":
                            corrected_tokens.append("is" if token.text.lower() in ["was"] else "are")
                        elif token.lemma_ == "have":
                            corrected_tokens.append("has" if token.text.lower() in ["had"] else "have")
                        else:
                            # Handle irregular verbs first
                            irregular_present = {
                                "go": "goes",
                                "do": "does", 
                                "have": "has",
                                "be": "is",
                                "say": "says",
                                "get": "gets",
                                "make": "makes",
                                "know": "knows",
                                "think": "thinks",
                                "see": "sees",
                                "come": "comes",
                                "want": "wants",
                                "look": "looks",
                                "use": "uses",
                                "find": "finds",
                                "give": "gives",
                                "tell": "tells",
                                "work": "works",
                                "call": "calls",
                                "try": "tries",
                                "ask": "asks",
                                "need": "needs",
                                "feel": "feels",
                                "become": "becomes",
                                "leave": "leaves",
                                "put": "puts",
                                "mean": "means",
                                "keep": "keeps",
                                "let": "lets",
                                "begin": "begins",
                                "seem": "seems",
                                "help": "helps",
                                "talk": "talks",
                                "turn": "turns",
                                "start": "starts",
                                "show": "shows",
                                "hear": "hears",
                                "play": "plays",
                                "run": "runs",
                                "move": "moves",
                                "live": "lives",
                                "believe": "believes",
                                "hold": "holds",
                                "bring": "brings",
                                "happen": "happens",
                                "write": "writes",
                                "provide": "provides",
                                "sit": "sits",
                                "stand": "stands",
                                "lose": "loses",
                                "pay": "pays",
                                "meet": "meets",
                                "include": "includes",
                                "continue": "continues",
                                "set": "sets",
                                "learn": "learns",
                                "change": "changes",
                                "lead": "leads",
                                "understand": "understands",
                                "watch": "watches",
                                "follow": "follows",
                                "stop": "stops",
                                "create": "creates",
                                "speak": "speaks",
                                "read": "reads",
                                "allow": "allows",
                                "add": "adds",
                                "spend": "spends",
                                "grow": "grows",
                                "open": "opens",
                                "walk": "walks",
                                "win": "wins",
                                "offer": "offers",
                                "remember": "remembers",
                                "love": "loves",
                                "consider": "considers",
                                "appear": "appears",
                                "buy": "buys",
                                "wait": "waits",
                                "serve": "serves",
                                "die": "dies",
                                "send": "sends",
                                "expect": "expects",
                                "build": "builds",
                                "stay": "stays",
                                "fall": "falls",
                                "cut": "cuts",
                                "reach": "reaches",
                                "kill": "kills",
                                "remain": "remains",
                                "suggest": "suggests",
                                "raise": "raises",
                                "pass": "passes",
                                "sell": "sells",
                                "require": "requires",
                                "report": "reports",
                                "decide": "decides",
                                "pull": "pulls"
                            }
                            
                            base_form = token.lemma_
                            if base_form in irregular_present:
                                corrected_tokens.append(irregular_present[base_form])
                            else:
                                # For regular verbs, use base form + s for 3rd person
                                if base_form.endswith(('s', 'sh', 'ch', 'x', 'z')):
                                    corrected_tokens.append(base_form + "es")
                                elif base_form.endswith('y') and len(base_form) > 1 and base_form[-2] not in 'aeiou':
                                    corrected_tokens.append(base_form[:-1] + "ies")
                                else:
                                    corrected_tokens.append(base_form + "s")
                    else:
                        corrected_tokens.append(token.text)
                elif target_tense == 'Past':
                    # Convert to past tense
                    if token.tag_ in ["VBP", "VBZ"]:  # Present tense
                        if token.lemma_ == "be":
                            corrected_tokens.append("was" if token.text.lower() in ["is"] else "were")
                        elif token.lemma_ == "have":
                            corrected_tokens.append("had")
                        else:
                            # For regular verbs, add -ed with proper spelling rules
                            base_form = token.lemma_
                            if base_form.endswith('e'):
                                corrected_tokens.append(base_form + "d")
                            elif base_form.endswith(('y') and len(base_form) > 1 and base_form[-2] not in 'aeiou'):
                                corrected_tokens.append(base_form[:-1] + "ied")
                            elif len(base_form) > 2 and base_form[-1] in 'bcdfghjklmnpqrstvwxyz' and base_form[-2] in 'aeiou' and base_form[-3] not in 'aeiou':
                                # Double the final consonant
                                corrected_tokens.append(base_form + base_form[-1] + "ed")
                            else:
                                corrected_tokens.append(base_form + "ed")
                    else:
                        corrected_tokens.append(token.text)
                else:
                    corrected_tokens.append(token.text)
            else:
                corrected_tokens.append(token.text)
        
        # Join and clean up
        result = " ".join(corrected_tokens)
        result = " ".join(result.split())  # Clean up multiple spaces
        
        return result if result != sentence else None
        
    except Exception as e:
        print(f"Error fixing tense consistency: {e}")
        return None

def fix_style_clarity(sentence: str, doc) -> Optional[str]:
    """
    Fix common style and clarity issues.
    
    Args:
        sentence: The original sentence
        doc: spaCy document object
        
    Returns:
        Corrected sentence with improved style and clarity, or None if no fixes needed
    """
    try:
        # Common style improvements
        improvements = []
        
        # Fix "a" vs "an" issues
        words = sentence.split()
        for i, word in enumerate(words):
            if word.lower() == "a" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word.startswith(('a', 'e', 'i', 'o', 'u')):
                    words[i] = "an"
                    improvements.append(f"Changed 'a' to 'an' before '{words[i + 1]}'")
        
        # Fix double negatives
        if "not" in sentence.lower() and any(neg in sentence.lower() for neg in ["no", "never", "nothing", "nobody", "nowhere"]):
            # This is a complex fix, so we'll just flag it for now
            pass
        
        # Fix redundant phrases
        redundant_phrases = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
            ("in the event that", "if"),
            ("for the purpose of", "to"),
            ("with regard to", "about"),
            ("in the case of", "if"),
            ("as a result of", "because of"),
            ("in spite of the fact that", "although"),
            ("in the near future", "soon")
        ]
        
        for phrase, replacement in redundant_phrases:
            if phrase in sentence.lower():
                # Replace the phrase (case-insensitive)
                import re
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                sentence = pattern.sub(replacement, sentence)
                improvements.append(f"Replaced '{phrase}' with '{replacement}'")
        
        # Clean up spacing
        sentence = " ".join(sentence.split())
        
        return sentence if improvements else None
        
    except Exception as e:
        print(f"Error fixing style and clarity: {e}")
        return None

class HybridGrammarChecker:
    """Hybrid grammar checker using spaCy and LanguageTool for enhanced accuracy"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.spacy_model = None
        self.language_tool = None
        self.confidence_threshold = confidence_threshold
        self._initialize_models()
        
        # Grammar issue categories
        self.categories = {
            'tense_consistency': 'Verb tense consistency issues',
            'subject_verb_agreement': 'Subject-verb agreement',
            'punctuation': 'Grammar/punctuation (commas, quotation marks)',
            'awkward_phrasing': 'Awkward phrasing',
            'redundancy': 'Redundancy',
            'style': 'Style and clarity',
            'spelling': 'Spelling errors'
        }
    
    def _initialize_models(self):
        """Initialize spaCy and LanguageTool models"""
        try:
            # Load spaCy model (download if not present)
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
                print("✓ spaCy model loaded successfully")
            except OSError as e:
                print(f"✗ spaCy model not found: {e}")
                print("Please install with: python -m spacy download en_core_web_sm")
                self.spacy_model = None
            except Exception as e:
                print(f"✗ Error loading spaCy model: {e}")
                self.spacy_model = None
            
            # Initialize LanguageTool
            languagetool_url = os.getenv("LANGUAGETOOL_URL", "http://localhost:8081")
            try:
                self.language_tool = LanguageTool('en-US', remote_server=languagetool_url)
                print("✓ LanguageTool connected to remote server")
            except Exception as e:
                print(f"✗ Failed to connect to LanguageTool server: {e}")
                # Fallback to local LanguageTool
                try:
                    self.language_tool = LanguageTool('en-US')
                    print("✓ LanguageTool initialized locally")
                except Exception as e2:
                    print(f"✗ Failed to initialize local LanguageTool: {e2}")
                    self.language_tool = None
                    
        except Exception as e:
            print(f"✗ Error initializing grammar checker: {e}")
            self.spacy_model = None
            self.language_tool = None
    
    async def check_document(
        self, 
        document_data: DocumentData, 
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> List[GrammarIssue]:
        """
        Check entire document for grammar issues using hybrid approach
        
        Args:
            document_data: Parsed document data
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of grammar issues found
        """
        all_issues = []
        total_lines = len(document_data.lines)
        
        for i, line in enumerate(document_data.lines):
            # Update progress
            if progress_callback:
                progress = int((i / total_lines) * 100)
                progress_callback(progress)
            
            # Check each sentence in the line
            for sentence_idx, sentence in enumerate(line.sentences):
                if sentence.strip():
                    issues = await self._check_sentence(
                        sentence, 
                        line.line_number, 
                        sentence_idx + 1,
                        document_data.lines
                    )
                    all_issues.extend(issues)
            
            # Small delay to prevent overwhelming the API
            await asyncio.sleep(0.01)
        
        # Final progress update
        if progress_callback:
            progress_callback(100)
        
        return all_issues
    
    async def _check_sentence(
        self, 
        sentence: str, 
        line_number: int, 
        sentence_number: int,
        all_lines: List[DocumentLine]
    ) -> List[GrammarIssue]:
        """
        Check a single sentence for grammar issues
        
        Args:
            sentence: Sentence to check
            line_number: Line number where sentence appears
            sentence_number: Sentence number within the line
            all_lines: All document lines for context
            
        Returns:
            List of grammar issues found in the sentence
        """
        issues = []
        
        # Sanitize the sentence before processing to prevent spaCy/LanguageTool issues
        sanitized_sentence = sanitize_text(sentence)
        if not sanitized_sentence:
            return issues  # Skip empty sentences after sanitization
        
        # Check with spaCy
        spacy_issues = await self._check_with_spacy(sanitized_sentence, line_number, sentence_number)
        issues.extend(spacy_issues)
        
        # Check with LanguageTool
        languagetool_issues = await self._check_with_languagetool(sanitized_sentence, line_number, sentence_number)
        issues.extend(languagetool_issues)
        
        # Cross-validate and merge similar issues
        merged_issues = self._merge_similar_issues(issues)
        
        # Filter by confidence threshold
        filtered_issues = self._filter_by_confidence(merged_issues)
        
        return filtered_issues
    
    async def _check_with_spacy(
        self, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check sentence using spaCy NLP"""
        issues = []
        
        if not self.spacy_model:
            return issues
        
        try:
            doc = self.spacy_model(sentence)
            
            # Check for tense consistency
            tense_issues = self._check_tense_consistency(doc, sentence, line_number, sentence_number)
            issues.extend(tense_issues)
            
            # Check for subject-verb agreement
            agreement_issues = self._check_subject_verb_agreement(doc, sentence, line_number, sentence_number)
            issues.extend(agreement_issues)
            
            # Check for awkward phrasing
            phrasing_issues = self._check_awkward_phrasing(doc, sentence, line_number, sentence_number)
            issues.extend(phrasing_issues)
            
            # Check for style and clarity issues
            style_issues = self._check_style_clarity(doc, sentence, line_number, sentence_number)
            issues.extend(style_issues)
            
            # Check for redundancy
            redundancy_issues = self._check_redundancy(doc, sentence, line_number, sentence_number)
            issues.extend(redundancy_issues)
            
        except Exception as e:
            print(f"Error in spaCy analysis: {e}")
        
        return issues
    
    async def _check_with_languagetool(
        self, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check sentence using LanguageTool"""
        issues = []
        
        if not self.language_tool:
            return issues
        
        try:
            matches = self.language_tool.check(sentence)
            
            for match in matches:
                # Map LanguageTool categories to our categories
                category = self._map_languagetool_category(match.ruleId)
                
                # Extract the problematic text
                start_pos = match.offset
                end_pos = match.offset + match.errorLength
                problematic_text = sentence[start_pos:end_pos]
                
                # Get suggested fixes
                fixes = match.replacements[:3]  # Limit to 3 suggestions
                fix_text = fixes[0] if fixes else problematic_text
                
                # Generate corrected sentence for various issue types
                corrected_sentence = None
                if category == 'spelling' and fixes:
                    corrected_sentence = sentence[:start_pos] + fix_text + sentence[end_pos:]
                elif category == 'style':
                    # For style issues, try to generate a corrected sentence
                    corrected_sentence = fix_style_clarity(sentence, None)  # We don't have doc here, so pass None
                
                issue = GrammarIssue(
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=problematic_text,
                    problem=match.message,
                    fix=fix_text,
                    category=category,
                    confidence=0.8,  # LanguageTool confidence
                    corrected_sentence=corrected_sentence
                )
                
                issues.append(issue)
                
        except Exception as e:
            print(f"Error in LanguageTool analysis: {e}")
        
        return issues
    
    def _check_tense_consistency(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for tense consistency issues using spaCy"""
        issues = []
        
        # Find all finite verbs (main verbs with tense information)
        finite_verbs = []
        for token in doc:
            if token.pos_ == "VERB" and token.tag_ in ["VBD", "VBP", "VBZ"]:  # Past, Present, Present 3rd person
                finite_verbs.append(token)
        
        if len(finite_verbs) < 2:
            return issues  # Need at least 2 finite verbs to check consistency
        
        # Extract tenses from finite verbs
        tenses = []
        for verb in finite_verbs:
            tense_values = verb.morph.get("Tense")
            if tense_values:
                tense = tense_values[0] if isinstance(tense_values, list) else tense_values
                tenses.append((verb.text, tense, verb.tag_))
        
        # Check for tense inconsistencies
        unique_tenses = set(tense for _, tense, _ in tenses)
        if len(unique_tenses) > 1:
            # Check if the tenses are actually inconsistent
            # Group tenses by their base form
            tense_groups = {
                'Pres': ['Pres'],
                'Past': ['Past'], 
                'Fut': ['Fut']
            }
            
            base_tenses = set()
            for _, tense, _ in tenses:
                for base, variants in tense_groups.items():
                    if tense in variants:
                        base_tenses.add(base)
                        break
                else:
                    base_tenses.add(tense)  # Unknown tense, treat as unique
            
            # Only flag as inconsistent if we have different base tenses
            # AND the sentence doesn't contain common tense-shifting indicators
            if len(base_tenses) > 1:
                # Check for legitimate tense shifts
                tense_shift_indicators = [
                    'when', 'while', 'after', 'before', 'since', 'until', 'as soon as',
                    'if', 'unless', 'provided that', 'supposing', 'in case',
                    'because', 'since', 'as', 'so that', 'in order that',
                    'although', 'though', 'even though', 'whereas', 'while',
                    'used to', 'would', 'could', 'might', 'should'
                ]
                
                # Check if sentence contains tense shift indicators
                sentence_lower = sentence.lower()
                has_tense_shift_indicator = any(indicator in sentence_lower for indicator in tense_shift_indicators)
                
                # Check for quoted speech (which often has different tense)
                has_quotes = '"' in sentence or "'" in sentence
                
                # Check for time expressions that justify tense shifts
                time_expressions = [
                    'yesterday', 'today', 'tomorrow', 'now', 'then', 'ago', 'last', 'next',
                    'in the past', 'in the future', 'currently', 'previously', 'recently'
                ]
                has_time_expression = any(expr in sentence_lower for expr in time_expressions)
                
                # Only flag if no legitimate reason for tense shift
                if not (has_tense_shift_indicator or has_quotes or has_time_expression):
                    # Try to generate a corrected sentence
                    corrected_sentence = fix_tense_consistency(sentence, doc)
                    
                    verb_tense_pairs = [f"{verb} ({tense})" for verb, tense, _ in tenses]
                    issue = GrammarIssue(
                        line_number=line_number,
                        sentence_number=sentence_number,
                        original_text=sentence,
                        problem=f"Tense inconsistency detected: {', '.join(verb_tense_pairs)}",
                        fix="Consider using consistent tense throughout the sentence",
                        category="tense_consistency",
                        confidence=0.6,  # Lower confidence since this is more subjective
                        corrected_sentence=corrected_sentence
                    )
                    issues.append(issue)
        
        return issues
    
    def _check_subject_verb_agreement(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for subject-verb agreement issues"""
        issues = []
        
        # Find subject-verb pairs
        for token in doc:
            if token.dep_ == "nsubj":  # Subject
                verb = token.head
                
                # Skip if this is part of a contraction
                if self._is_part_of_contraction(token, verb, doc):
                    continue
                
                if verb.pos_ == "VERB":
                    # Get subject number information
                    subject_number_values = token.morph.get("Number")
                    subject_number = subject_number_values[0] if subject_number_values and isinstance(subject_number_values, list) else subject_number_values
                    
                    # Check verb agreement based on verb form and subject number
                    verb_agreement_issue = self._check_verb_agreement_with_subject(token, verb, subject_number)
                    
                    if verb_agreement_issue:
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=sentence_number,
                            original_text=f"{token.text} {verb.text}",
                            problem=verb_agreement_issue["problem"],
                            fix=verb_agreement_issue["fix"],
                            category="subject_verb_agreement",
                            confidence=0.8,
                            corrected_sentence=None
                        )
                        issues.append(issue)
                
                # Also check auxiliary verbs that are children of the subject's head
                elif verb.pos_ == "AUX":  # The subject's head is an auxiliary verb
                    # Find the main verb that this auxiliary is helping
                    main_verbs = [child for child in verb.children if child.pos_ == "VERB" and child.dep_ == "ROOT"]
                    if main_verbs:
                        main_verb = main_verbs[0]
                        # Get subject number information
                        subject_number_values = token.morph.get("Number")
                        subject_number = subject_number_values[0] if subject_number_values and isinstance(subject_number_values, list) else subject_number_values
                        
                        # Check auxiliary verb agreement
                        aux_agreement_issue = self._check_auxiliary_agreement(token, verb, subject_number)
                        
                        if aux_agreement_issue:
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=sentence_number,
                                original_text=f"{token.text} {verb.text} {main_verb.text}",
                                problem=aux_agreement_issue["problem"],
                                fix=aux_agreement_issue["fix"],
                                category="subject_verb_agreement",
                                confidence=0.8,
                                corrected_sentence=None
                            )
                            issues.append(issue)
        
        return issues
    
    def _is_part_of_contraction(self, subject_token, verb_token, doc):
        """
        Check if the subject-verb pair is part of a contraction.
        This handles cases where spaCy splits contractions like "it's" into separate tokens.
        """
        # Check if the verb is a contraction part
        if verb_token.text in ["'s", "'m", "'re", "'ve", "'ll", "'d", "'t"]:
            return True
        
        # Check if the subject and verb are adjacent and form a contraction
        if (subject_token.i + 1 == verb_token.i and 
            verb_token.text.startswith("'") and
            len(verb_token.text) > 1):
            return True
        
        # Check for common contraction patterns in the original sentence
        # Look for patterns like "it's", "he's", "she's", "we're", "they're", etc.
        subject_text = subject_token.text.lower()
        verb_text = verb_token.text.lower()
        
        # Common contraction patterns
        contraction_patterns = [
            ("it", "'s"),      # it's
            ("he", "'s"),      # he's  
            ("she", "'s"),     # she's
            ("we", "'re"),     # we're
            ("they", "'re"),   # they're
            ("you", "'re"),    # you're
            ("i", "'m"),       # I'm
            ("i", "'ve"),      # I've
            ("i", "'ll"),      # I'll
            ("i", "'d"),       # I'd
            ("we", "'ve"),     # we've
            ("we", "'ll"),     # we'll
            ("we", "'d"),      # we'd
            ("they", "'ve"),   # they've
            ("they", "'ll"),   # they'll
            ("they", "'d"),    # they'd
            ("you", "'ve"),    # you've
            ("you", "'ll"),    # you'll
            ("you", "'d"),     # you'd
            ("he", "'ll"),     # he'll
            ("he", "'d"),      # he'd
            ("she", "'ll"),    # she'll
            ("she", "'d"),     # she'd
            ("it", "'ll"),     # it'll
            ("it", "'d"),      # it'd
        ]
        
        for subject_pattern, verb_pattern in contraction_patterns:
            if (subject_text == subject_pattern and 
                verb_text == verb_pattern and
                subject_token.i + 1 == verb_token.i):
                return True
        
        return False
    
    def _check_verb_agreement_with_subject(self, subject_token, verb_token, subject_number):
        """Check if verb agrees with subject number"""
        # Skip contractions and pronouns that are part of contractions
        if "'" in verb_token.text or verb_token.text in ["'s", "'m", "'re", "'ve", "'ll", "'d"]:
            return None
            
        # Skip if subject is a pronoun that's part of a contraction
        if "'" in subject_token.text:
            return None
        
        # Get the actual subject person (1st, 2nd, 3rd)
        subject_person = self._get_subject_person(subject_token)
        
        # Common subject-verb agreement patterns
        if subject_number == "Sing":
            # For 3rd person singular subjects (he, she, it, singular nouns)
            if subject_person == 3:
                # 3rd person singular should use VBZ (goes, is, has)
                if verb_token.tag_ in ["VBP"]:  # Non-3rd person form (go, am, are)
                    if verb_token.lemma_ == "be":
                        return {
                            "problem": f"Subject-verb disagreement: {subject_token.text} (3rd person singular) with {verb_token.text} (non-3rd person form)",
                            "fix": f"Use 'is' instead of '{verb_token.text}'"
                        }
                    else:
                        return {
                            "problem": f"Subject-verb disagreement: {subject_token.text} (3rd person singular) with {verb_token.text} (non-3rd person form)",
                            "fix": f"Use '{verb_token.lemma_}s' instead of '{verb_token.text}'"
                        }
            # For 1st and 2nd person singular (I, you), VBP is correct
            elif subject_person in [1, 2]:
                # These should use VBP, so no error here
                pass
                
        elif subject_number == "Plur":
            # Plural subjects should use VBP (go, are, have)
            if verb_token.tag_ in ["VBZ"]:  # 3rd person singular form (goes, is, has)
                if verb_token.lemma_ == "be":
                    return {
                        "problem": f"Subject-verb disagreement: {subject_token.text} (plural) with {verb_token.text} (3rd person singular form)",
                        "fix": f"Use 'are' instead of '{verb_token.text}'"
                    }
                else:
                    return {
                        "problem": f"Subject-verb disagreement: {subject_token.text} (plural) with {verb_token.text} (3rd person singular form)",
                        "fix": f"Use '{verb_token.lemma_}' instead of '{verb_token.text}'"
                    }
        
        return None
    
    def _get_subject_person(self, subject_token):
        """Get the grammatical person (1st, 2nd, 3rd) of a subject"""
        subject_text = subject_token.text.lower()
        
        # 1st person
        if subject_text in ["i", "me", "my", "mine", "myself"]:
            return 1
        # 2nd person  
        elif subject_text in ["you", "your", "yours", "yourself", "yourselves"]:
            return 2
        # 3rd person
        else:
            return 3
    
    def _check_auxiliary_agreement(self, subject_token, aux_token, subject_number):
        """Check if auxiliary verb agrees with subject number"""
        # Skip contractions - use the same logic as the main method
        if self._is_part_of_contraction(subject_token, aux_token, None):
            return None
            
        # Skip if subject is a pronoun that's part of a contraction
        if "'" in subject_token.text:
            return None
        
        # Get the actual subject person (1st, 2nd, 3rd)
        subject_person = self._get_subject_person(subject_token)
        
        if aux_token.lemma_ == "be":
            if subject_number == "Sing":
                # For 3rd person singular subjects (he, she, it, singular nouns)
                if subject_person == 3:
                    # 3rd person singular should use "is" (VBZ)
                    if aux_token.tag_ in ["VBP"]:  # "are" form
                        return {
                            "problem": f"Subject-auxiliary disagreement: {subject_token.text} (3rd person singular) with '{aux_token.text}' (non-3rd person form)",
                            "fix": f"Use 'is' instead of '{aux_token.text}'"
                        }
                # For 1st and 2nd person singular (I, you), VBP is correct
                elif subject_person in [1, 2]:
                    # These should use VBP, so no error here
                    pass
                    
            elif subject_number == "Plur":
                # Plural subjects should use "are" (VBP)
                if aux_token.tag_ in ["VBZ"]:  # "is" form
                    return {
                        "problem": f"Subject-auxiliary disagreement: {subject_token.text} (plural) with '{aux_token.text}' (3rd person singular form)",
                        "fix": f"Use 'are' instead of '{aux_token.text}'"
                    }
        
        return None
    
    def _get_correct_verb_form(self, verb_token, subject_number):
        """Get the correct verb form based on subject number"""
        # This is a simplified approach - in practice, you'd need more sophisticated logic
        # to handle irregular verbs and different tenses
        
        if subject_number == "Sing":
            # For singular subjects, use base form or appropriate singular form
            if verb_token.tag_ in ["VBZ"]:  # Already singular
                return verb_token.text
            elif verb_token.tag_ in ["VBP"]:  # Plural form
                # Try to convert to singular (this is simplified)
                if verb_token.text.endswith(('s', 'es')):
                    return verb_token.text[:-2] if verb_token.text.endswith('es') else verb_token.text[:-1]
                return verb_token.text
            else:
                return verb_token.lemma_  # Use base form
        elif subject_number == "Plur":
            # For plural subjects, use appropriate plural form
            if verb_token.tag_ in ["VBP"]:  # Already plural
                return verb_token.text
            elif verb_token.tag_ in ["VBZ"]:  # Singular form
                # Try to convert to plural (this is simplified)
                if verb_token.text.endswith(('s', 'x', 'z', 'ch', 'sh')):
                    return verb_token.text + 'es'
                else:
                    return verb_token.text + 's'
            else:
                return verb_token.lemma_  # Use base form
        
        return verb_token.text  # Fallback
    
    def _check_awkward_phrasing(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for awkward phrasing patterns"""
        issues = []
        
        # Check for passive voice overuse - look for VBN verbs with auxpass children
        passive_verbs = []
        for token in doc:
            if token.tag_ == "VBN":  # Past participle
                # Check if this verb has an auxiliary verb with auxpass dependency
                for child in token.children:
                    if child.dep_ == "auxpass":
                        passive_verbs.append(token)
                        break
        if len(passive_verbs) > 0:
            # Try to convert to active voice
            corrected_sentence = convert_passive_to_active(sentence, doc)
            
            issue = GrammarIssue(
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=sentence,
                problem="Passive voice detected - consider using active voice for clarity",
                fix="Rewrite using active voice where possible",
                category="awkward_phrasing",
                confidence=0.6,
                corrected_sentence=corrected_sentence
            )
            issues.append(issue)
        
        # Long sentence detection removed per user request
        
        return issues
    
    def _check_style_clarity(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for style and clarity issues"""
        issues = []
        
        # Check for "a" vs "an" issues
        words = sentence.split()
        for i, word in enumerate(words):
            if word.lower() == "a" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word.startswith(('a', 'e', 'i', 'o', 'u')):
                    # Generate corrected sentence
                    corrected_words = words.copy()
                    corrected_words[i] = "an"
                    corrected_sentence = " ".join(corrected_words)
                    
                    issue = GrammarIssue(
                        line_number=line_number,
                        sentence_number=sentence_number,
                        original_text=f"a {words[i + 1]}",
                        problem=f"Use 'an' before words starting with a vowel sound: '{words[i + 1]}'",
                        fix="Change 'a' to 'an'",
                        category="style",
                        confidence=0.9,
                        corrected_sentence=corrected_sentence
                    )
                    issues.append(issue)
        
        # Check for redundant phrases
        redundant_phrases = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
            ("in the event that", "if"),
            ("for the purpose of", "to"),
            ("with regard to", "about"),
            ("in the case of", "if"),
            ("as a result of", "because of"),
            ("in spite of the fact that", "although"),
            ("in the near future", "soon")
        ]
        
        for phrase, replacement in redundant_phrases:
            if phrase in sentence.lower():
                # Generate corrected sentence
                import re
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                corrected_sentence = pattern.sub(replacement, sentence)
                
                issue = GrammarIssue(
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=phrase,
                    problem=f"Redundant phrase: '{phrase}' can be simplified",
                    fix=f"Replace with '{replacement}'",
                    category="style",
                    confidence=0.8,
                    corrected_sentence=corrected_sentence
                )
                issues.append(issue)
        
        return issues
    
    def _check_redundancy(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for redundant words and phrases"""
        issues = []
        
        # Only check for truly redundant phrases, not normal conjunctions
        redundant_patterns = [
            (r'\b(and then)\b', 'then'),
            (r'\b(and also)\b', 'also'),
            (r'\b(and as well)\b', 'as well'),
            (r'\b(and in addition)\b', 'in addition'),
            (r'\b(and furthermore)\b', 'furthermore'),
            (r'\b(and moreover)\b', 'moreover'),
            (r'\b(and plus)\b', 'plus'),
            (r'\b(and additionally)\b', 'additionally'),
        ]
        
        for pattern, replacement in redundant_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                issue = GrammarIssue(
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=sentence,
                    problem=f"Redundant phrase detected: '{pattern}'",
                    fix=f"Remove redundant words: '{replacement}'",
                    category="redundancy",
                    confidence=0.7,
                    corrected_sentence=None
                )
                issues.append(issue)
        
        return issues
    
    def _map_languagetool_category(self, rule_id: str) -> str:
        """Map LanguageTool rule IDs to our categories"""
        category_mapping = {
            'EN_TENSE_SELECTION': 'tense_consistency',
            'SUBJECT_VERB_AGREEMENT': 'subject_verb_agreement',
            'COMMA_PARENTHESIS_WHITESPACE': 'punctuation',
            'WHITESPACE_RULE': 'punctuation',
            'DOUBLE_PUNCTUATION': 'punctuation',
            'MORFOLOGIK_RULE_EN_US': 'spelling',
            'EN_A_VS_AN': 'style',
            'EN_UNPAIRED_BRACKETS': 'punctuation',
        }
        
        return category_mapping.get(rule_id, 'style')
    
    def _merge_similar_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Merge similar issues to avoid duplicates"""
        if not issues:
            return issues
        
        merged = []
        seen_positions = set()
        
        for issue in issues:
            position_key = (issue.line_number, issue.sentence_number, issue.original_text)
            
            if position_key not in seen_positions:
                merged.append(issue)
                seen_positions.add(position_key)
            else:
                # Find existing issue and merge if they're similar
                for existing in merged:
                    if (existing.line_number == issue.line_number and 
                        existing.sentence_number == issue.sentence_number and
                        existing.original_text == issue.original_text):
                        
                        # Merge categories and increase confidence
                        if issue.category != existing.category:
                            existing.category += f", {issue.category}"
                        existing.confidence = max(existing.confidence, issue.confidence)
                        break
        
        return merged
    
    def _filter_by_confidence(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Filter issues by confidence threshold"""
        return [issue for issue in issues if issue.confidence >= self.confidence_threshold]
    
    def get_issues_summary(self, issues: List[GrammarIssue]) -> Dict[str, Any]:
        """Generate summary of all issues found"""
        if not issues:
            return {
                'total_issues': 0,
                'categories': {},
                'lines_with_issues': 0,
                'sentences_with_issues': 0
            }
        
        # Count by category
        category_counts = {}
        for issue in issues:
            category = issue.category
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
        # Count unique lines and sentences
        lines_with_issues = len(set(issue.line_number for issue in issues))
        sentences_with_issues = len(set((issue.line_number, issue.sentence_number) for issue in issues))
        
        return {
            'total_issues': len(issues),
            'categories': category_counts,
            'lines_with_issues': lines_with_issues,
            'sentences_with_issues': sentences_with_issues
        }
