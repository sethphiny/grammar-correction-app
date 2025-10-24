"""
Full LLM-Based Grammar Checker

This is a pure AI-powered grammar checker that uses LLM for both detection and correction.
Much more accurate than pattern-based approaches, with full context awareness.
"""

import os
import json
import asyncio
import logging
import inspect
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from difflib import SequenceMatcher
from models.schemas import DocumentData, GrammarIssue
from dotenv import load_dotenv

# Configure structured logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Import OpenAI
try:
    from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    tiktoken = None
    logger.warning("openai package not installed. LLM grammar checking will be disabled.")

# Import json-repair for robust JSON parsing
try:
    from json_repair import repair_json
    JSON_REPAIR_AVAILABLE = True
except ImportError:
    JSON_REPAIR_AVAILABLE = False
    logger.warning("json-repair package not installed. Falling back to basic JSON repair.")


class LLMGrammarChecker:
    """
    Pure LLM-based grammar checker using GPT-4o-mini or GPT-4.
    
    Advantages over pattern-based:
    - Context-aware detection
    - Understands writer's intent and style
    - Natural, accurate corrections
    - No false positives from rigid rules
    - Handles complex grammar issues
    """
    
    # Model context window sizes (in tokens)
    MODEL_CONTEXT_WINDOWS = {
        "gpt-4o-mini": 128000,
        "gpt-4o": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16385,
    }
    
    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # seconds
    MAX_RETRY_DELAY = 10.0  # seconds
    
    def __init__(self):
        """Initialize LLM grammar checker"""
        self.enabled = os.getenv("LLM_ENHANCEMENT_ENABLED", "false").lower() == "true"
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.client = None
        self.tokenizer = None
        self.context_window = self.MODEL_CONTEXT_WINDOWS.get(self.model, 128000)
        
        # Initialize if enabled
        if self.enabled and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = AsyncOpenAI(api_key=api_key)
                    # Fix: Use self.model instead of hardcoded model name
                    try:
                        self.tokenizer = tiktoken.encoding_for_model(self.model)
                    except KeyError:
                        # Fallback to cl100k_base encoding if model not found
                        logger.warning(f"Model {self.model} not found in tiktoken, using cl100k_base encoding")
                        self.tokenizer = tiktoken.get_encoding("cl100k_base")
                    
                    logger.info(f"LLMGrammarChecker initialized with {self.model} (context window: {self.context_window} tokens)")
                except Exception as e:
                    logger.error(f"Failed to initialize LLMGrammarChecker: {e}", exc_info=True)
                    self.enabled = False
            else:
                logger.warning("OPENAI_API_KEY not set")
                self.enabled = False
        
        # Map pattern-based categories to LLM checking instructions
        # This ensures Ultra Mode can check the same categories as pattern mode
        self.category_mapping = {
            # Core Grammar
            'grammar': 'general grammar errors, verb tenses, sentence structure',
            'agreement': 'subject-verb agreement, pronoun-antecedent agreement',
            'tense_consistency': 'verb tense consistency and narrative flow',
            
            # Style & Clarity
            'awkward_phrasing': 'awkward or unnatural phrasing',
            'redundancy': 'redundant words and phrases',
            'clarity': 'unclear or confusing expressions',
            'word_order': 'incorrect word order',
            'parallelism_concision': 'parallel structure and conciseness',
            
            # Mechanics
            'spelling': 'spelling errors (NOT proper nouns or British/American variants)',
            'punctuation': 'punctuation errors',
            'capitalisation': 'capitalization errors',
            'dialogue': 'dialogue formatting and punctuation',
            'ellipsis': 'ellipsis usage and formatting',
            'hyphenation': 'hyphenation and compound word formation',
            'missing_period': 'missing periods at end of sentences',
            'number_style': 'number formatting and consistency',
            'broken_quote': 'broken or improperly formatted quotations',
            
            # Advanced
            'ambiguous_pronouns': 'ambiguous pronoun references',
            'dangling_clause': 'dangling modifiers and clauses',
            'fragment': 'sentence fragments',
            'run_on': 'run-on sentences',
            'comma_splice': 'comma splices',
            'split_line': 'improperly split lines or sentences',
            
            # Additional
            'article_specificity': 'article usage (a, an, the)',
            'preposition': 'preposition usage',
            'possessive': "possessive forms (ONLY flag if apostrophe is missing, incorrectly placed, or used for simple plurals - DO NOT flag valid possessives like 'attacks' or 'children's')",
            'contrast': 'contrast and comparison expressions',
            'coordination': 'coordination and conjunctions',
            'register': 'appropriate formality level',
            'repetition': 'unnecessary repetition',
            'compounds': 'compound word formation and usage',
            'pronoun_reference': 'pronoun reference and antecedent clarity',
        }
        
        # All available categories
        self.all_categories = list(self.category_mapping.keys())
    
    async def cleanup(self):
        """Cleanup resources (close client if needed)"""
        if self.client:
            try:
                await self.client.close()
                logger.info("AsyncOpenAI client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing AsyncOpenAI client: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self.tokenizer:
            return len(text) // 4
        return len(self.tokenizer.encode(text))
    
    def _check_token_limit(self, prompt_tokens: int, max_response_tokens: int) -> bool:
        """
        Check if prompt + response tokens fit within model's context window.
        
        Returns:
            True if within limit, False otherwise
        """
        total_tokens = prompt_tokens + max_response_tokens
        if total_tokens > self.context_window:
            logger.warning(
                f"Token limit exceeded: {total_tokens} > {self.context_window} "
                f"(prompt: {prompt_tokens}, response: {max_response_tokens})"
            )
            return False
        return True
    
    def _fuzzy_match_ratio(self, str1: str, str2: str) -> float:
        """
        Calculate fuzzy match ratio between two strings using SequenceMatcher.
        
        Returns:
            Float between 0.0 and 1.0, where 1.0 is a perfect match
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    async def _call_with_progress(
        self,
        callback: Optional[Callable],
        *args,
        **kwargs
    ):
        """
        Call progress callback, handling both sync and async callables.
        """
        if callback is None:
            return
        
        try:
            if inspect.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                # Run sync callback in executor to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: callback(*args, **kwargs))
        except Exception as e:
            logger.warning(f"Error in progress callback: {e}")
    
    async def _call_llm_with_retry(
        self,
        prompt: str,
        max_response_tokens: int,
        timeout: float = 30.0
    ) -> str:
        """
        Call LLM with exponential backoff retry logic.
        
        Args:
            prompt: The prompt to send
            max_response_tokens: Maximum tokens for response
            timeout: Timeout for each request
            
        Returns:
            Response text from LLM
            
        Raises:
            Exception: If all retries fail
        """
        retry_delay = self.INITIAL_RETRY_DELAY
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert grammar checker. Only flag genuine errors. Preserve writer's voice and style. DO NOT flag proper nouns, official names, British/American spelling variants, or any names (people, places, companies, products) as spelling errors. DO NOT remove apostrophes from valid possessive forms (e.g., 'attacks' mysterious nature' is correct plural possessive). Be conservative - when in doubt, don't flag it. Return ONLY valid JSON with properly escaped quotes."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=max_response_tokens,
                        temperature=0.0,  # Most deterministic for proper JSON
                        response_format={"type": "json_object"}
                    ),
                    timeout=timeout
                )
                
                return response.choices[0].message.content.strip()
                
            except (RateLimitError, APITimeoutError) as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    logger.warning(
                        f"API call failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {type(e).__name__}. "
                        f"Retrying in {retry_delay:.1f}s..."
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, self.MAX_RETRY_DELAY)
                else:
                    logger.error(f"API call failed after {self.MAX_RETRIES} attempts: {e}")
                    raise
                    
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"API call timeout (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, self.MAX_RETRY_DELAY)
                
            except Exception as e:
                logger.error(f"Unexpected error in API call: {e}", exc_info=True)
                raise
        
        if last_exception:
            raise last_exception
    
    def _repair_json(self, json_text: str) -> dict:
        """
        Attempt to repair malformed JSON using json_repair library or fallback methods.
        
        Args:
            json_text: The potentially malformed JSON string
            
        Returns:
            Parsed JSON as dict
            
        Raises:
            json.JSONDecodeError: If JSON cannot be repaired
        """
        # Try standard parsing first
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        # Try json_repair library if available
        if JSON_REPAIR_AVAILABLE:
            try:
                repaired = repair_json(json_text)
                result = json.loads(repaired)
                logger.info("Successfully repaired JSON using json_repair library")
                return result
            except Exception as e:
                logger.warning(f"json_repair failed: {e}")
        
        # Fallback: Try to remove markdown code blocks
        if "```json" in json_text or "```" in json_text:
            try:
                import re
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_text)
                if json_match:
                    cleaned = json_match.group(1).strip()
                    result = json.loads(cleaned)
                    logger.info("Repaired JSON by removing markdown blocks")
                    return result
            except json.JSONDecodeError:
                pass
        
        # If all fails, raise the original error
        raise json.JSONDecodeError("Could not repair JSON", json_text, 0)
    
    async def check_paragraph(
        self,
        paragraph_text: str,
        paragraph_number: int,
        starting_line_number: int,
        context_before: str = "",
        context_after: str = "",
        enabled_categories: Optional[List[str]] = None
    ) -> List[GrammarIssue]:
        """
        Check a paragraph using LLM for grammar issues.
        
        Args:
            paragraph_text: The paragraph to check
            paragraph_number: Paragraph number in document
            starting_line_number: Line number where paragraph starts
            context_before: Text before this paragraph (for context)
            context_after: Text after this paragraph (for context)
            enabled_categories: Optional list of categories to check
            
        Returns:
            List of grammar issues found
        """
        if not self.enabled or not self.client:
            return []
        
        # Filter categories based on user selection
        if enabled_categories:
            # Use only the categories selected by the user
            categories_to_check = [c for c in enabled_categories if c in self.category_mapping]
            if not categories_to_check:
                # If none match, fall back to all categories
                logger.warning("No matching categories found, using all categories")
                categories_to_check = self.all_categories
        else:
            # If no categories specified, check all
            categories_to_check = self.all_categories
        
        try:
            # Build context section
            context_section = ""
            if context_before or context_after:
                context_section = "\n\n**Context (for reference):**"
                if context_before:
                    context_section += f"\n[Previous paragraph]: {context_before[-200:]}"
                if context_after:
                    context_section += f"\n[Next paragraph]: {context_after[:200]}"
            
            # Build category descriptions for the prompt
            category_descriptions = []
            for cat in categories_to_check:
                desc = self.category_mapping.get(cat, cat)
                category_descriptions.append(f"- {cat}: {desc}")
            
            categories_text = '\n'.join(category_descriptions)
            
            prompt = f"""Analyze the following paragraph ONLY for the specific issue types listed below.

**Paragraph to Analyze:**
{paragraph_text}
{context_section}

**Categories to Check (ONLY THESE):**
{categories_text}

⚠️ CRITICAL: ONLY report issues that fall into the categories listed above.
⚠️ If you find an issue that is NOT in the above categories, DO NOT report it.
⚠️ The "category" field in your response MUST be one of: {', '.join(categories_to_check)}

**SPELLING CATEGORY RULES (EXTREMELY IMPORTANT):**
- British spellings (colour, flavour, honour, behaviour, etc.) are CORRECT - do NOT flag them
- American spellings (color, flavor, honor, behavior, etc.) are CORRECT - do NOT flag them
- ONLY flag actual misspellings, NOT regional spelling variants
- Proper nouns and official names are ALWAYS correct (Labour Party, Organisation, etc.)
- Technical terms, brand names, and specialized vocabulary are correct
- **NEVER flag names as spelling errors:**
  * Personal names (first names, last names, full names) - ALWAYS correct
  * Place names (cities, countries, regions, streets) - ALWAYS correct
  * Company/organization names - ALWAYS correct
  * Product/brand names - ALWAYS correct
  * Character names in fiction/stories - ALWAYS correct
  * Any capitalized words that could be names - assume they are correct
- When in doubt if something is a name, DO NOT flag it as a spelling error

**POSSESSIVE APOSTROPHE RULES (EXTREMELY IMPORTANT):**
- Singular possessive: attack's mysterious nature (belonging to one attack) - CORRECT
- Plural possessive: attacks' mysterious nature (belonging to multiple attacks) - CORRECT
- Plural possessive for words ending in s: James' book OR James's book - BOTH CORRECT
- **DO NOT remove apostrophes from valid possessives:**
  * "the attacks' mysterious nature" is GRAMMATICALLY CORRECT (plural possessive)
  * "the children's toys" is CORRECT (irregular plural possessive)
  * "the boss's office" or "the boss' office" are BOTH CORRECT
- Only flag possessive issues if:
  * Apostrophe is missing where needed (the dogs bone → the dog's bone)
  * Apostrophe is used for simple plurals (apple's and orange's → apples and oranges)
  * Wrong possessive form is used (the dog's are barking → the dogs are barking)
- **NEVER suggest removing apostrophes from valid possessive forms**
- If a possessive form is grammatically valid, DO NOT flag it even if you could rewrite it differently

**CRITICAL RULES:**
1. Only report ACTUAL errors in the specified categories, NOT style preferences
2. Preserve the writer's voice - don't impose formal style on casual writing
3. Context matters - use surrounding text to understand intent
4. Be conservative - when in doubt, don't flag it
5. DO NOT make up or hallucinate issues - only report what you actually see
6. For each issue, provide:
   - The EXACT problematic text from the paragraph (must be word-for-word quote)
   - The "original_text" field MUST contain text that actually appears in the paragraph above
   - Clear explanation WITHOUT using quotation marks or apostrophes
   - The corrected version (should be similar length to original, only fixing the specific issue)
   - Category MUST be one from the list above
   - Confidence level (0.0-1.0)

**CRITICAL JSON FORMATTING:**
- NEVER use quotation marks or apostrophes in the problem or fix fields
- Instead of: Change "word" to "other"
- Write: Change word to other
- Instead of: The word "example" should be
- Write: The word example should be
- Use descriptive text without quoting

Return ONLY valid JSON (no markdown blocks, no extra text):
{{
    "issues": [
        {{
            "original_text": "Copy the EXACT text from the paragraph that has the error",
            "problem": "Brief explanation without quotation marks describing what is wrong",
            "fix": "Brief suggestion without quotation marks on how to fix it",
            "corrected_text": "The same sentence with ONLY the error fixed, keeping everything else identical",
            "category": "MUST be one of: {', '.join(categories_to_check)}",
            "confidence": 0.95
        }}
    ]
}}

IMPORTANT:
- "original_text" must be copied EXACTLY from the paragraph above
- "corrected_text" should be nearly identical to "original_text" with only the specific error fixed
- If you cannot find a genuine error, return: {{"issues": []}}

REMEMBER: 
- NO quotation marks in problem/fix fields
- British/American spellings are BOTH valid
- NEVER flag names (people, places, companies, products) as spelling errors
- NEVER remove apostrophes from valid possessive forms (attacks' nature is CORRECT)!"""
            
            # Estimate tokens and check context window
            prompt_tokens = self.count_tokens(prompt)
            max_response_tokens = min(1000, max(300, len(paragraph_text) // 2))
            
            # Check token limit before making API call
            if not self._check_token_limit(prompt_tokens, max_response_tokens):
                logger.error(
                    f"Skipping paragraph {paragraph_number}: token limit would be exceeded"
                )
                return []
            
            logger.debug(
                f"Checking paragraph {paragraph_number} ({len(paragraph_text)} chars, "
                f"{prompt_tokens} prompt tokens, {max_response_tokens} max response tokens)"
            )
            
            # Call LLM with retry logic
            response_text = await self._call_llm_with_retry(
                prompt=prompt,
                max_response_tokens=max_response_tokens,
                timeout=30.0
            )
            
            try:
                result = self._repair_json(response_text)
            except json.JSONDecodeError as e:
                logger.error(
                    f"JSON parsing error in paragraph {paragraph_number}: {e}. "
                    f"Response preview: {response_text[:200]}..."
                )
                return []
            
            if "issues" not in result or not isinstance(result["issues"], list):
                return []
            
            # Convert to GrammarIssue objects
            grammar_issues = []
            for issue_data in result["issues"]:
                # Validate required fields
                if not all(key in issue_data for key in ["original_text", "problem", "fix", "corrected_text", "category", "confidence"]):
                    continue
                
                # Filter by confidence
                if issue_data["confidence"] < 0.7:
                    continue
                
                # Map category
                category = issue_data["category"]
                if category not in self.all_categories:
                    category = "grammar"  # Default fallback
                
                # CRITICAL: Filter by enabled categories
                # If user selected specific categories, only include issues from those categories
                if enabled_categories and category not in categories_to_check:
                    # Skip this issue - it's not in the requested categories
                    continue
                
                # CRITICAL: Filter out British/American spelling variant issues
                # Only filter if the problem explicitly mentions British/American variants
                problem_lower = issue_data["problem"].lower()
                
                # More targeted detection - must explicitly mention variants
                is_variant_issue = (
                    ('british' in problem_lower and 'american' in problem_lower) or
                    ('variant' in problem_lower and ('spelling' in problem_lower or 'convention' in problem_lower)) or
                    'spelling convention' in problem_lower
                )
                
                if is_variant_issue:
                    logger.debug(f"Filtered out British/American variant issue: {issue_data['problem'][:60]}...")
                    continue
                
                # CRITICAL: Validate that the issue makes sense
                # Check if the original_text actually appears in the paragraph being analyzed
                original_text_clean = issue_data["original_text"].strip()
                
                # Normalize whitespace for comparison (multiple spaces -> single space)
                import re
                paragraph_normalized = re.sub(r'\s+', ' ', paragraph_text.strip())
                original_normalized = re.sub(r'\s+', ' ', original_text_clean)
                
                # Check for exact match or use fuzzy matching with sequence similarity
                if original_normalized not in paragraph_normalized:
                    # Use fuzzy string matching for better hallucination detection
                    fuzzy_ratio = self._fuzzy_match_ratio(original_normalized, paragraph_normalized)
                    
                    # If similarity is too low, this is likely a hallucination
                    if fuzzy_ratio < 0.6:  # Less than 60% similarity
                        logger.debug(
                            f"Filtered out hallucinated issue (similarity: {fuzzy_ratio:.2f}): "
                            f"'{original_text_clean[:60]}...'"
                        )
                        continue
                
                # Check if corrected_text is substantially different from original
                corrected_text_clean = issue_data["corrected_text"].strip()
                if len(original_text_clean) > 0 and len(corrected_text_clean) > 0:
                    # More lenient length check - allow up to 3x difference for legitimate corrections
                    length_ratio = len(corrected_text_clean) / len(original_text_clean)
                    if length_ratio < 0.3 or length_ratio > 3.0:
                        logger.debug(f"Filtered out suspicious issue: correction length mismatch (ratio: {length_ratio:.2f})")
                        continue
                
                issue = GrammarIssue(
                    line_number=starting_line_number,
                    sentence_number=1,
                    original_text=issue_data["original_text"],
                    problem=issue_data["problem"],
                    fix=issue_data["fix"],
                    category=category,
                    confidence=min(float(issue_data["confidence"]), 0.95),
                    corrected_sentence=issue_data["corrected_text"]
                )
                
                # Validate that correction actually changes something
                if issue.corrected_sentence.strip() != issue.original_text.strip():
                    grammar_issues.append(issue)
            
            logger.info(f"Found {len(grammar_issues)} issues in paragraph {paragraph_number}")
            return grammar_issues
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout checking paragraph {paragraph_number}")
            return []
        except Exception as e:
            logger.error(f"Error checking paragraph {paragraph_number}: {e}", exc_info=True)
            return []
    
    async def check_document(
        self,
        document_data: DocumentData,
        progress_callback: Optional[Callable] = None,
        enabled_categories: Optional[List[str]] = None,
        chunk_size: int = 5
    ) -> Tuple[List[GrammarIssue], Dict[str, Any]]:
        """
        Check entire document using LLM.
        
        Strategy: Process paragraphs in chunks for efficiency and context.
        
        Args:
            document_data: Document to check
            progress_callback: Optional progress callback
            enabled_categories: Optional list of categories to check
            chunk_size: Number of lines to process as one paragraph
            
        Returns:
            Tuple of (issues, metadata)
        """
        if not self.enabled or not self.client:
            return [], {
                "llm_enabled": False,
                "error": "LLM not enabled or not available"
            }
        
        logger.info("Starting full LLM-based grammar check")
        
        # Show which categories are being checked
        if enabled_categories:
            valid_cats = [c for c in enabled_categories if c in self.category_mapping]
            logger.info(f"Checking categories: {valid_cats}")
        else:
            logger.info("Checking ALL categories")
        
        all_issues = []
        total_lines = len(document_data.lines)
        
        # Group lines into paragraphs (empty lines separate paragraphs)
        paragraphs = []
        current_paragraph = []
        current_start_line = 1
        
        for i, line in enumerate(document_data.lines, 1):
            if line.content.strip():
                if not current_paragraph:
                    current_start_line = i
                current_paragraph.append(line.content)
            else:
                if current_paragraph:
                    # Preserve line breaks by using '\n'.join() instead of ' '.join()
                    paragraphs.append({
                        "text": "\n".join(current_paragraph),
                        "start_line": current_start_line,
                        "lines": current_paragraph
                    })
                    current_paragraph = []
        
        # Add last paragraph if exists
        if current_paragraph:
            # Preserve line breaks by using '\n'.join() instead of ' '.join()
            paragraphs.append({
                "text": "\n".join(current_paragraph),
                "start_line": current_start_line,
                "lines": current_paragraph
            })
        
        logger.info(f"Processing {len(paragraphs)} paragraphs")
        
        # Process each paragraph
        for idx, para in enumerate(paragraphs):
            # Get context
            context_before = ""
            context_after = ""
            
            if idx > 0:
                context_before = paragraphs[idx - 1]["text"]
            
            if idx < len(paragraphs) - 1:
                context_after = paragraphs[idx + 1]["text"]
            
            # Check paragraph
            issues = await self.check_paragraph(
                paragraph_text=para["text"],
                paragraph_number=idx + 1,
                starting_line_number=para["start_line"],
                context_before=context_before,
                context_after=context_after,
                enabled_categories=enabled_categories
            )
            
            all_issues.extend(issues)
            
            # Update progress (supports both sync and async callbacks)
            if progress_callback:
                await self._call_with_progress(
                    progress_callback,
                    idx + 1,
                    len(paragraphs),
                    len(all_issues)
                )
        
        metadata = {
            "llm_enabled": True,
            "mode": "full_llm",
            "paragraphs_processed": len(paragraphs),
            "total_issues": len(all_issues),
            "model": self.model
        }
        
        logger.info(f"Complete - Found {len(all_issues)} issues across {len(paragraphs)} paragraphs")
        
        return all_issues, metadata
    
    def get_available_categories(self) -> List[Dict[str, Any]]:
        """Get list of available grammar checking categories"""
        return [
            {'id': cat, 'name': cat.replace('_', ' ').title()}
            for cat in self.all_categories
        ]

