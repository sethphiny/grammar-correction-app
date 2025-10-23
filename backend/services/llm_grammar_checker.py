"""
Full LLM-Based Grammar Checker

This is a pure AI-powered grammar checker that uses LLM for both detection and correction.
Much more accurate than pattern-based approaches, with full context awareness.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Callable
from models.schemas import DocumentData, GrammarIssue
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Import OpenAI
try:
    from openai import AsyncOpenAI
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    tiktoken = None
    print("⚠️ Warning: openai package not installed. LLM grammar checking will be disabled.")


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
    
    def __init__(self):
        """Initialize LLM grammar checker"""
        self.enabled = os.getenv("LLM_ENHANCEMENT_ENABLED", "false").lower() == "true"
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.client = None
        self.tokenizer = None
        
        # Initialize if enabled
        if self.enabled and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = AsyncOpenAI(api_key=api_key)
                    self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
                    print(f"✅ [LLMGrammarChecker] Initialized with {self.model}")
                except Exception as e:
                    print(f"❌ [LLMGrammarChecker] Failed to initialize: {e}")
                    self.enabled = False
            else:
                print("⚠️ [LLMGrammarChecker] OPENAI_API_KEY not set")
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
            'possessive': 'possessive forms',
            'contrast': 'contrast and comparison expressions',
            'coordination': 'coordination and conjunctions',
            'register': 'appropriate formality level',
            'repetition': 'unnecessary repetition',
            'compounds': 'compound word formation and usage',
            'pronoun_reference': 'pronoun reference and antecedent clarity',
        }
        
        # All available categories
        self.all_categories = list(self.category_mapping.keys())
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self.tokenizer:
            return len(text) // 4
        return len(self.tokenizer.encode(text))
    
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
                print(f"⚠️ [LLMGrammarChecker] No matching categories, using all")
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

REMEMBER: NO quotation marks in problem/fix fields, and British/American spellings are BOTH valid!"""
            
            # Estimate tokens
            prompt_tokens = self.count_tokens(prompt)
            max_response_tokens = min(1000, max(300, len(paragraph_text) // 2))
            
            print(f"[LLMGrammarChecker] Checking paragraph {paragraph_number} ({len(paragraph_text)} chars)")
            
            # Call LLM
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert grammar checker. Only flag genuine errors. Preserve writer's voice and style. DO NOT flag proper nouns, official names, or British/American spelling variants. Be conservative. Return ONLY valid JSON with properly escaped quotes."
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
                timeout=30.0
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ [LLMGrammarChecker] JSON parsing error: {e}")
                print(f"   Response preview: {response_text[:300]}...")
                
                # Try multiple JSON repair strategies
                repaired = False
                
                # Strategy 1: Remove markdown code blocks
                if "```json" in response_text:
                    try:
                        import re
                        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
                        if json_match:
                            response_text = json_match.group(1).strip()
                            result = json.loads(response_text)
                            print(f"✅ [LLMGrammarChecker] Fixed JSON by removing markdown blocks")
                            repaired = True
                    except json.JSONDecodeError:
                        pass
                
                # Strategy 2: Try to fix unescaped quotes in problem/fix fields
                if not repaired:
                    try:
                        import re
                        # Replace unescaped quotes in "problem" and "fix" fields
                        # Pattern: "problem": "text with "quotes" in it"
                        def fix_quotes(match):
                            field = match.group(1)
                            content = match.group(2)
                            # Remove or replace internal quotes
                            fixed_content = content.replace('"', '')
                            return f'"{field}": "{fixed_content}"'
                        
                        fixed_text = re.sub(
                            r'"(problem|fix)"\s*:\s*"([^"]*?"[^"]*?)"',
                            fix_quotes,
                            response_text
                        )
                        result = json.loads(fixed_text)
                        print(f"✅ [LLMGrammarChecker] Fixed JSON by removing internal quotes")
                        repaired = True
                    except (json.JSONDecodeError, Exception):
                        pass
                
                # Strategy 3: Last resort - skip this paragraph
                if not repaired:
                    print(f"❌ [LLMGrammarChecker] Could not fix JSON, skipping paragraph")
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
                    print(f"   ⚠️ Filtered out British/American variant issue: {issue_data['problem'][:60]}...")
                    continue
                
                # CRITICAL: Validate that the issue makes sense
                # Check if the original_text actually appears in the paragraph being analyzed
                original_text_clean = issue_data["original_text"].strip()
                
                # Normalize whitespace for comparison (multiple spaces -> single space)
                import re
                paragraph_normalized = re.sub(r'\s+', ' ', paragraph_text.strip())
                original_normalized = re.sub(r'\s+', ' ', original_text_clean)
                
                # Check for exact match or substantial overlap (at least 70% of words match)
                if original_normalized not in paragraph_normalized:
                    # Try fuzzy matching - check if most words are present
                    original_words = set(original_normalized.lower().split())
                    paragraph_words = set(paragraph_normalized.lower().split())
                    
                    if len(original_words) > 0:
                        overlap = len(original_words & paragraph_words) / len(original_words)
                        if overlap < 0.7:  # Less than 70% word overlap
                            print(f"   ⚠️ Filtered out hallucinated issue: original_text not found in paragraph")
                            print(f"      Claimed: '{original_text_clean[:60]}...'")
                            continue
                
                # Check if corrected_text is substantially different from original
                corrected_text_clean = issue_data["corrected_text"].strip()
                if len(original_text_clean) > 0 and len(corrected_text_clean) > 0:
                    # More lenient length check - allow up to 3x difference for legitimate corrections
                    length_ratio = len(corrected_text_clean) / len(original_text_clean)
                    if length_ratio < 0.3 or length_ratio > 3.0:
                        print(f"   ⚠️ Filtered out suspicious issue: correction length mismatch (ratio: {length_ratio:.2f})")
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
            
            print(f"[LLMGrammarChecker] Found {len(grammar_issues)} issues in paragraph {paragraph_number}")
            return grammar_issues
            
        except asyncio.TimeoutError:
            print(f"⚠️ [LLMGrammarChecker] Timeout checking paragraph {paragraph_number}")
            return []
        except Exception as e:
            print(f"⚠️ [LLMGrammarChecker] Error checking paragraph {paragraph_number}: {e}")
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
        
        print(f"[LLMGrammarChecker] 🤖 Starting full LLM-based grammar check")
        
        # Show which categories are being checked
        if enabled_categories:
            valid_cats = [c for c in enabled_categories if c in self.category_mapping]
            print(f"[LLMGrammarChecker] Checking categories: {valid_cats}")
        else:
            print(f"[LLMGrammarChecker] Checking ALL categories")
        
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
                    paragraphs.append({
                        "text": " ".join(current_paragraph),
                        "start_line": current_start_line,
                        "lines": current_paragraph
                    })
                    current_paragraph = []
        
        # Add last paragraph if exists
        if current_paragraph:
            paragraphs.append({
                "text": " ".join(current_paragraph),
                "start_line": current_start_line,
                "lines": current_paragraph
            })
        
        print(f"[LLMGrammarChecker] Processing {len(paragraphs)} paragraphs")
        
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
            
            # Update progress
            if progress_callback:
                progress = int(((idx + 1) / len(paragraphs)) * 100)
                await progress_callback(idx + 1, len(paragraphs), len(all_issues))
        
        metadata = {
            "llm_enabled": True,
            "mode": "full_llm",
            "paragraphs_processed": len(paragraphs),
            "total_issues": len(all_issues),
            "model": self.model
        }
        
        print(f"[LLMGrammarChecker] ✅ Complete - Found {len(all_issues)} issues")
        
        return all_issues, metadata
    
    def get_available_categories(self) -> List[Dict[str, Any]]:
        """Get list of available grammar checking categories"""
        return [
            {'id': cat, 'name': cat.replace('_', ' ').title()}
            for cat in self.all_categories
        ]

