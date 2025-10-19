"""
Grammar checker with modular category-based architecture

Refactored from monolithic design (2691 lines) to use modular category files.
Each grammar category now lives in its own file under services/categories/.
"""

import re
import os
import asyncio
from typing import List, Dict, Any, Optional, Callable, Tuple
from models.schemas import DocumentData, DocumentLine, GrammarIssue

# Import all category classes
from .categories import (
    RedundancyCategory,
    AwkwardPhrasingCategory,
    PunctuationCategory,
    GrammarCategory,
    DialogueCategory,
    CapitalisationCategory,
    TenseConsistencyCategory,
    SpellingCategory,
    ParallelismConcisionCategory,
    ArticleSpecificityCategory,
    AgreementCategory,
    AmbiguousPronounsCategory,
    DanglingClauseCategory,
    FragmentCategory,
    RunOnCategory,
    SplitLineCategory,
    WordOrderCategory,
    ContrastCategory,
    ClarityCategory,
    PrepositionCategory,
    RegisterCategory,
    RepetitionCategory,
    CommaSpliceCategory,
    CoordinationCategory,
    EllipsisCategory,
    HyphenationCategory,
    MissingPeriodCategory,
    NumberStyleCategory,
    PossessiveCategory,
    BrokenQuoteCategory,
    CompoundsCategory,
    PronounReferenceCategory,
)

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
    
    # 5️⃣.5 Fix hyphenated contractions
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
    """
    Grammar checker using modular category-based architecture.
    
    Each grammar category is defined in its own file under services/categories/.
    This makes the code more maintainable, testable, and extensible.
    """
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        
        # Initialize LLM enhancer (optional feature)
        if LLM_ENHANCER_AVAILABLE:
            self.llm_enhancer = LLMEnhancer()
        else:
            self.llm_enhancer = None
        
        # Initialize all category instances
        self.category_instances = {
            'redundancy': RedundancyCategory(),
            'awkward_phrasing': AwkwardPhrasingCategory(),
            'punctuation': PunctuationCategory(),
            'grammar': GrammarCategory(),
            'dialogue': DialogueCategory(),
            'capitalisation': CapitalisationCategory(),
            'tense_consistency': TenseConsistencyCategory(),
            'spelling': SpellingCategory(),
            'parallelism_concision': ParallelismConcisionCategory(),
            'article_specificity': ArticleSpecificityCategory(),
            'agreement': AgreementCategory(),
            'ambiguous_pronouns': AmbiguousPronounsCategory(),
            'dangling_clause': DanglingClauseCategory(),
            'fragment': FragmentCategory(),
            'run_on': RunOnCategory(),
            'split_line': SplitLineCategory(),
            'word_order': WordOrderCategory(),
            'contrast': ContrastCategory(),
            'clarity': ClarityCategory(),
            'preposition': PrepositionCategory(),
            'register': RegisterCategory(),
            'repetition': RepetitionCategory(),
            'comma_splice': CommaSpliceCategory(),
            'coordination': CoordinationCategory(),
            'ellipsis': EllipsisCategory(),
            'hyphenation': HyphenationCategory(),
            'missing_period': MissingPeriodCategory(),
            'number_style': NumberStyleCategory(),
            'possessive': PossessiveCategory(),
            'broken_quote': BrokenQuoteCategory(),
            'compounds': CompoundsCategory(),
            'pronoun_reference': PronounReferenceCategory(),
        }
        
        # Build categories dict from instances
        self.categories = {
            cat_id: instance.get_display_name()
            for cat_id, instance in self.category_instances.items()
        }
        
        # Passive voice context (for spaCy detection)
        self.intentional_passive_starters = [
            'it was', 'it is', 'it has been', 'it had been', 'it will be',
            'there was', 'there is', 'there has been', 'there had been', 'there will be'
        ]
        
        self.passive_voice_context_words = [
            'framework', 'method', 'methodology', 'algorithm', 'system',
            'approach', 'technique', 'process', 'procedure', 'experiment',
            'study', 'research', 'analysis', 'model', 'protocol'
        ]
    
    async def _check_line_content(
        self,
        line_content: str,
        line_number: int,
        enabled_categories: Optional[List[str]] = None
    ) -> List[GrammarIssue]:
        """
        Check a single line for grammar issues using the modular category system.
        
        This unified method replaces the old approach of checking each category separately.
        It iterates through all enabled categories and applies their rules.
        
        Args:
            line_content: The line text to check
            line_number: The line number in the document
            enabled_categories: Optional list of category names to check
        
        Returns:
            List of GrammarIssue objects found in this line
        """
        # Helper function to check if category is enabled
        def is_category_enabled(cat_name):
            if enabled_categories is None:
                return True
            return cat_name in enabled_categories
        
        issues = []
        sanitized_lower = line_content.lower()
        
        # Iterate through all categories
        for cat_id, category in self.category_instances.items():
            if not is_category_enabled(cat_id):
                continue
            
            # DICTIONARY-BASED CATEGORIES (redundancy, awkward_phrasing, spelling)
            if category.get_dictionary():
                dictionary = category.get_dictionary()
                
                for phrase, replacement in dictionary.items():
                    phrase_lower = phrase.lower()
                    if phrase_lower in sanitized_lower:
                        start_idx = sanitized_lower.find(phrase_lower)
                        original_phrase = line_content[start_idx:start_idx+len(phrase)]
                        
                        # Preserve capitalization
                        if original_phrase and original_phrase[0].isupper():
                            replacement_fixed = replacement.capitalize()
                        else:
                            replacement_fixed = replacement
                        
                        corrected_line = (
                            line_content[:start_idx] + 
                            replacement_fixed + 
                            line_content[start_idx+len(phrase):]
                        )
                        
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=line_content,
                            problem=f"{category.get_display_name()}: '{original_phrase}' can be simplified",
                            fix=f"'{original_phrase}' → '{replacement_fixed}'",
                            category=cat_id,
                            confidence=category.get_confidence(),
                            corrected_sentence=corrected_line
                        )
                        issues.append(issue)
            
            # PATTERN-BASED CATEGORIES (all others)
            elif category.get_patterns():
                for idx, (pattern, description, fix_func) in enumerate(category.get_patterns()):
                    try:
                        matches = list(re.finditer(pattern, line_content, re.IGNORECASE))
                    except re.error:
                        # Skip invalid patterns
                        continue
                    
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        original_text = line_content[start_pos:end_pos]
                        
                        if fix_func is not None:
                            try:
                                suggested_fix = fix_func(match, line_content)
                                if original_text.lower() == suggested_fix.lower():
                                    continue
                                
                                # Preserve capitalization
                                if original_text and original_text[0].isupper() and suggested_fix:
                                    suggested_fix = suggested_fix[0].upper() + suggested_fix[1:]
                                
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
                                    category=cat_id,
                                    confidence=category.get_confidence(idx),
                                    corrected_sentence=corrected_line
                                )
                                issues.append(issue)
                            except Exception as e:
                                # Skip patterns that fail to execute
                                continue
                        else:
                            # No auto-fix available
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=1,
                                original_text=line_content,
                                problem=f"{description}",
                                fix="Review and revise as needed",
                                category=cat_id,
                                confidence=category.get_confidence(idx),
                                corrected_sentence=None
                            )
                            issues.append(issue)
        
        # Special handling for parallelism_concision passive voice (spaCy-based)
        if is_category_enabled('parallelism_concision') and SPACY_AVAILABLE and nlp:
            passive_issues = self._detect_passive_voice_spacy(line_content, line_number)
            issues.extend(passive_issues)
        
        return issues
    
    def _detect_passive_voice_spacy(self, text: str, line_number: int) -> List[GrammarIssue]:
        """
        Detect true passive voice using spaCy dependency parsing.
        
        This method uses linguistic analysis to identify actual passive voice constructions
        and skips false positives like linking verbs with adjectives.
        """
        if not SPACY_AVAILABLE or nlp is None:
            return []
        
        issues = []
        
        try:
            doc = nlp(text)
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                sentence_lower = sentence_text.lower()
                
                # Skip if sentence starts with common intentional passive indicators
                if any(sentence_lower.startswith(starter) for starter in self.intentional_passive_starters):
                    continue
                
                # Skip if technical/academic context
                if any(word in sentence_lower for word in self.passive_voice_context_words):
                    continue
                
                # Find passive voice constructions
                for token in sent:
                    # Look for passive auxiliary (was, were, been, be, is, are) + past participle
                    if token.dep_ == "auxpass":  # Passive auxiliary
                        # Find the past participle it's attached to
                        for child in token.head.children:
                            if child.dep_ in ("nsubjpass", "csubjpass"):  # Passive subject
                                passive_phrase = sent.text[token.idx - sent.start_char:token.head.idx - sent.start_char + len(token.head.text)]
                                
                                # Generate active voice suggestion
                                fix_suggestion = f"Consider rephrasing in active voice"
                        
                        issue = GrammarIssue(
                            line_number=line_number,
                            sentence_number=1,
                            original_text=text,
                                    problem=f"Passive voice detected: '{passive_phrase}' - Consider using active voice for clarity",
                            fix=fix_suggestion,
                            category='parallelism_concision',
                            confidence=0.75,
                            corrected_sentence=None
                        )
                        
                        issues.append(issue)
                        break
        except Exception as e:
            # If spaCy processing fails, silently skip
            pass
        
        return issues
    
    async def _llm_detect_complex_issues(
        self,
        line_content: str,
        line_number: int,
        categories: Optional[List[str]],
        context_before: str = "",
        context_after: str = ""
    ) -> List[GrammarIssue]:
        """
        Use LLM to detect subtle, context-dependent grammar issues.
        
        This is supplementary to pattern-based detection and catches edge cases
        that are difficult to detect with regex patterns alone.
        """
        if not self.llm_enhancer or not self.llm_enhancer.enabled:
            return []
        
        # Only check sentences with 3+ words
        if len(line_content.split()) < 3:
            return []
        
        # Top categories for LLM checking
        top_categories = ['ambiguous_pronouns', 'dangling_clause', 'clarity']
        check_categories = [cat for cat in (categories or []) if cat in top_categories][:3]
        
        if not check_categories:
            return []
        
        # Build context section
        context_section = ""
        if context_before or context_after:
            context_section = "\n**Context (for reference):**"
            if context_before:
                context_section += f"\nPrevious: ...{context_before}"
            if context_after:
                context_section += f"\nNext: {context_after}..."
        
        prompt = f"""Analyze this sentence for subtle grammar issues using surrounding context. Return ONLY valid JSON.

**Current Sentence to Analyze:** "{line_content}"
{context_section}

**Check for:** {', '.join(check_categories)}

**CRITICAL RULES:**
1. Use context to understand tense shifts, pronoun references, and logical flow
2. Only report issues that ACTUALLY EXIST in the current sentence
3. Quote the exact problematic phrase from the current sentence
4. Be conservative - when in doubt, don't report
5. Verify the error is real, not imagined
6. PRESERVE writer's style - DO NOT flag casual/conversational language
7. Only flag objective grammar errors, NOT style preferences
8. Use context to determine if tense shifts, pronoun references, or transitions are appropriate

Return JSON array (ONLY JSON, no other text):
[{{"category": "category_name", "problem": "The phrase 'exact phrase' has this issue", "fix": "suggestion", "confidence": 0.75}}]

If no issues, return: []"""
        
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            response = await self.llm_enhancer.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a grammar expert. Return ONLY valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                timeout=10.0
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                import re as re_module
                json_match = re_module.search(r'```json\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    response_text = json_match.group(1).strip()
            elif "```" in response_text:
                response_text = response_text.replace("```", "").strip()
            
            response_text = response_text.strip()
            
            if not response_text or response_text == "[]":
                return []
            
            # Parse JSON
            import json
            try:
                detected_issues = json.loads(response_text)
            except json.JSONDecodeError:
                    return []
            
            if not isinstance(detected_issues, list):
                return []
            
            # Convert to GrammarIssue objects
            grammar_issues = []
            for issue_data in detected_issues:
                if not all(key in issue_data for key in ['category', 'problem', 'fix', 'confidence']):
                    continue
                
                min_confidence = 0.75 if issue_data['category'] == 'agreement' else 0.65
                if issue_data['confidence'] < min_confidence:
                    continue
                
                if categories and issue_data['category'] not in categories:
                            continue
                
                issue = GrammarIssue(
                    line_number=line_number,
                    sentence_number=1,
                    original_text=line_content,
                    problem=f"[AI] {issue_data['problem']}",
                    fix=issue_data['fix'],
                    category=issue_data['category'],
                    confidence=min(issue_data['confidence'], 0.85),
                    corrected_sentence=None
                )
                grammar_issues.append(issue)
            
            return grammar_issues
            
        except Exception:
            return []
    
    async def check_document(
        self, 
        document_data: DocumentData, 
        progress_callback: Optional[Callable] = None,
        enabled_categories: Optional[List[str]] = None,
        use_llm_enhancement: bool = False,
        use_llm_detection: bool = False,
        enhancement_progress_callback: Optional[Callable] = None
    ) -> Tuple[List[GrammarIssue], Dict[str, Any]]:
        """
        Check entire document for grammar issues.
        
        Strategy: Check at LINE level using modular categories.
        Optionally enhance with LLM for better suggestions.
        """
        if enabled_categories is None:
            print(f"[GrammarChecker] Checking ALL categories")
        else:
            print(f"[GrammarChecker] Checking categories: {enabled_categories}")
        
        if use_llm_enhancement:
            print(f"[GrammarChecker] ✨ LLM enhancement ENABLED")
        
        if use_llm_detection:
            print(f"[GrammarChecker] 🔍 LLM detection ENABLED")
        
        all_issues = []
        total_lines = len(document_data.lines)
        llm_detection_count = 0
        
        for i, line in enumerate(document_data.lines, 1):
            if not line.content or not line.content.strip():
                continue
            
            full_line_content = sanitize_text(line.content)
            
            # STAGE 1: Pattern-based detection
            line_issues = await self._check_line_content(
                full_line_content,
                line.line_number,
                enabled_categories
            )
            
            all_issues.extend(line_issues)
            
            # STAGE 2: LLM-based detection (supplementary)
            if use_llm_detection and self.llm_enhancer and len(full_line_content.split()) >= 8:
                word_count = len(full_line_content.split())
                pattern_issues_on_line = len(line_issues)
                
                should_use_llm = (
                    (word_count >= 15) or
                    (word_count >= 8 and pattern_issues_on_line <= 1)
                )
                
                if should_use_llm:
                    # Get context
                    context_before = ""
                    context_after = ""
                    
                    if i > 0:
                        prev_lines = []
                        chars_collected = 0
                        for prev_i in range(i - 1, max(-1, i - 5), -1):
                            prev_content = document_data.lines[prev_i].content.strip()
                            if prev_content:
                                prev_lines.insert(0, prev_content)
                                chars_collected += len(prev_content)
                                if chars_collected >= 150:
                                    break
                        if prev_lines:
                            context_before = " ".join(prev_lines)[-150:]
                    
                    if i < total_lines - 1:
                        next_lines = []
                        chars_collected = 0
                        for next_i in range(i + 1, min(total_lines, i + 6)):
                            next_content = document_data.lines[next_i].content.strip()
                            if next_content:
                                next_lines.append(next_content)
                                chars_collected += len(next_content)
                                if chars_collected >= 150:
                                    break
                        if next_lines:
                            context_after = " ".join(next_lines)[:150]
                    
                    llm_issues = await self._llm_detect_complex_issues(
                        full_line_content,
                        line.line_number,
                        enabled_categories,
                        context_before,
                        context_after
                    )
                    if llm_issues:
                        llm_detection_count += len(llm_issues)
                        all_issues.extend(llm_issues)
            
            # Update progress
            if progress_callback:
                import inspect
                if inspect.iscoroutinefunction(progress_callback):
                    await progress_callback(i, total_lines, len(all_issues))
                else:
                    progress = int((i / total_lines) * 100)
                    progress_callback(progress)
        
        # Merge similar issues
        all_issues = self._merge_similar_issues(all_issues)
        
        # Enhancement metadata
        enhancement_metadata = {
            "llm_enabled": False,
            "llm_detection_enabled": use_llm_detection,
            "issues_detected_by_llm": llm_detection_count,
            "issues_enhanced": 0,
            "cost": 0.0,
            "warning": None
        }
        
        # Optional: Enhance with LLM
        if use_llm_enhancement and all_issues and self.llm_enhancer and self.llm_enhancer.enabled:
            print(f"[GrammarChecker] Enhancing {len(all_issues)} issues with LLM...")
            
            if enhancement_progress_callback:
                await enhancement_progress_callback({
                    "type": "enhancement_start",
                    "total_issues": len(all_issues),
                    "message": f"Starting AI enhancement of {len(all_issues)} issues..."
                })
            
            full_text = "\n".join(line.content for line in document_data.lines)
            
            enhanced_issues, cost = await self.llm_enhancer.enhance_issues_batch(
                all_issues,
                full_text,
                max_issues=None,
                progress_callback=enhancement_progress_callback
            )
            
            if enhancement_progress_callback:
                await enhancement_progress_callback({
                    "type": "enhancement_complete",
                    "enhanced_issues": len(enhanced_issues),
                    "cost": cost,
                    "message": f"AI enhancement complete"
                })
            
            enhancement_metadata = {
                "llm_enabled": True,
                "llm_detection_enabled": use_llm_detection,
                "issues_detected_by_llm": llm_detection_count,
                "issues_enhanced": len(enhanced_issues),
                "cost": cost,
                "warning": None
            }
            
            return enhanced_issues, enhancement_metadata
        
        return all_issues, enhancement_metadata
    
    def _merge_similar_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """
        Merge duplicate or very similar issues to reduce noise.
        
        Two issues are considered duplicates if they:
        - Are on the same line
        - Have the same category
        - Have similar problem descriptions
        """
        if not issues:
            return []
        
        merged = []
        seen = set()
        
        for issue in issues:
            key = (issue.line_number, issue.category, issue.problem[:50])
            if key not in seen:
                merged.append(issue)
                seen.add(key)
        
        # Additional deduplication: merge issues that fix the same text
        final_merged = []
        line_issues = {}
        
        for issue in merged:
            if issue.line_number not in line_issues:
                line_issues[issue.line_number] = []
            line_issues[issue.line_number].append(issue)
        
        for line_num, line_issue_list in line_issues.items():
            processed_issues = []
            for issue in line_issue_list:
                is_duplicate = False
                for processed in processed_issues:
                    if (issue.original_text == processed.original_text and 
                        issue.line_number == processed.line_number and
                        issue.fix == processed.fix):
                        if issue.confidence > processed.confidence:
                            processed.category = f"{processed.category}/{issue.category}"
                            processed.confidence = issue.confidence
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    processed_issues.append(issue)
            
            final_merged.extend(processed_issues)
        
        return final_merged
    
    def get_available_categories(self) -> List[Dict[str, Any]]:
        """Get list of available grammar checking categories."""
        return [
            {'id': category_id, 'name': category_name}
            for category_id, category_name in self.categories.items()
        ]
    
    def get_issues_summary(self, issues: List[GrammarIssue]) -> Dict[str, Any]:
        """Generate a summary of issues found."""
        if not issues:
            return {
                'total_issues': 0,
                'categories': {},
                'lines_with_issues': 0,
                'sentences_with_issues': 0
            }
        
        categories = {}
        for issue in issues:
            category = issue.category
            categories[category] = categories.get(category, 0) + 1
        
        lines_with_issues = len(set(issue.line_number for issue in issues))
        sentences_with_issues = len(set((issue.line_number, issue.sentence_number) for issue in issues))
        
        return {
            'total_issues': len(issues),
            'categories': categories,
            'lines_with_issues': lines_with_issues,
            'sentences_with_issues': sentences_with_issues
        }

