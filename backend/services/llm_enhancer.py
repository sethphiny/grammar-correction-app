"""
LLM Enhancement Service for Grammar Corrections

Provides AI-powered enhancement of grammar fixes using OpenAI GPT-4o-mini
Cost-optimized with selective enhancement, batching, and optional caching
"""

import os
import json
import asyncio
import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from models.schemas import GrammarIssue
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Import OpenAI (optional dependency)
try:
    from openai import AsyncOpenAI
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    tiktoken = None
    print("⚠️ Warning: openai package not installed. LLM enhancement will be disabled.")
    print("To enable, run: pip install openai tiktoken")


class LLMEnhancer:
    """
    Enhance grammar fixes using LLM (GPT-4o-mini by default)
    
    Features:
    - Selective enhancement (only complex/uncertain issues)
    - Batch processing for efficiency
    - Cost estimation and tracking
    - Graceful degradation if API unavailable
    """
    
    def __init__(self):
        """Initialize LLM enhancer with configuration from environment"""
        self.enabled = os.getenv("LLM_ENHANCEMENT_ENABLED", "false").lower() == "true"
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.max_cost_per_doc = float(os.getenv("LLM_MAX_COST_PER_DOCUMENT", "0.50"))
        # When true, enhance all issues with no per-document cap
        self.enhance_all = os.getenv("LLM_ENHANCE_ALL", "true").lower() == "true"
        
        # Timeout and retry configuration
        self.request_timeout = int(os.getenv("LLM_REQUEST_TIMEOUT", "60"))  # 60 seconds default
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("LLM_RETRY_DELAY", "2.0"))  # 2 seconds
        
        self.client = None
        self.tokenizer = None
        
        # Initialize if enabled
        if self.enabled:
            if not OPENAI_AVAILABLE:
                print("❌ [LLMEnhancer] Cannot enable - openai package not installed")
                self.enabled = False
            elif self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("⚠️ [LLMEnhancer] LLM enhancement enabled but OPENAI_API_KEY not set")
                    self.enabled = False
                else:
                    try:
                        self.client = AsyncOpenAI(api_key=api_key)
                        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
                        print(f"✅ [LLMEnhancer] Initialized with {self.model}")
                    except Exception as e:
                        print(f"❌ [LLMEnhancer] Failed to initialize: {e}")
                        self.enabled = False
        
        # Cost tracking per model (per 1M tokens)
        self.pricing = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }
        
        # Track costs in memory (in production, use Redis)
        self.total_cost = 0.0
        self.total_issues_enhanced = 0
        
        if not self.enabled:
            print("ℹ️ [LLMEnhancer] LLM enhancement is DISABLED")
    
    async def _make_llm_request_with_retry(self, messages: List[Dict], max_tokens: int, **kwargs):
        """
        Make LLM request with retry logic and timeout handling
        
        Args:
            messages: List of message dictionaries for the API
            max_tokens: Maximum tokens for response
            **kwargs: Additional arguments for the API call
            
        Returns:
            API response object
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                print(f"[LLMEnhancer] Attempt {attempt + 1}/{self.max_retries}")
                
                # Add timeout to the request
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        **kwargs
                    ),
                    timeout=self.request_timeout
                )
                
                print(f"[LLMEnhancer] Request successful on attempt {attempt + 1}")
                return response
                
            except asyncio.TimeoutError:
                last_exception = Exception(f"Request timed out after {self.request_timeout} seconds")
                print(f"⚠️ [LLMEnhancer] Timeout on attempt {attempt + 1}/{self.max_retries}")
                
            except Exception as e:
                last_exception = e
                print(f"⚠️ [LLMEnhancer] Error on attempt {attempt + 1}/{self.max_retries}: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                print(f"[LLMEnhancer] Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
        
        # All retries failed
        print(f"❌ [LLMEnhancer] All {self.max_retries} attempts failed")
        raise last_exception
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate estimated cost for token usage
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if self.model not in self.pricing:
            return 0.0
        
        input_cost = (input_tokens / 1_000_000) * self.pricing[self.model]["input"]
        output_cost = (output_tokens / 1_000_000) * self.pricing[self.model]["output"]
        return input_cost + output_cost
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not self.tokenizer:
            # Rough estimate: ~4 characters per token
            return len(text) // 4
        
        return len(self.tokenizer.encode(text))
    
    def should_enhance_issue(self, issue: GrammarIssue) -> bool:
        """
        Determine if an issue should be enhanced with LLM
        
        Enhanced strategy for ALL categories:
        1. Low confidence issues (< 0.85) - always enhance
        2. Issues without corrected sentences - always enhance
        3. ALL categories now get LLM enhancement regardless of confidence
        
        Args:
            issue: Grammar issue to evaluate
            
        Returns:
            True if issue should be enhanced, False otherwise
        """
        # Always enhance if confidence is low
        if issue.confidence < 0.85:
            return True
        
        # Always enhance if no corrected sentence provided
        if not issue.corrected_sentence:
            return True
        
        # ENHANCE ALL CATEGORIES - Lower thresholds to ensure comprehensive coverage
        # High priority categories (complex context-dependent issues)
        high_priority_categories = {
            'awkward_phrasing',
            'tense_consistency', 
            'parallelism_concision',
            'dialogue',
            'grammar'  # Grammar rules can be context-dependent
        }
        
        # Medium priority categories (benefit from AI refinement)
        medium_priority_categories = {
            'redundancy',
            'capitalisation',
            'article_specificity'
        }
        
        # Lower priority categories (usually straightforward but can benefit from AI)
        lower_priority_categories = {
            'punctuation',
            'spelling'
        }
        
        # Lower confidence thresholds to ensure ALL issues get enhanced
        if issue.category in high_priority_categories:
            return issue.confidence < 0.95  # Enhanced: was 0.90, now 0.95
        elif issue.category in medium_priority_categories:
            return issue.confidence < 0.98  # Enhanced: was 0.95, now 0.98
        elif issue.category in lower_priority_categories:
            return issue.confidence < 0.99  # Enhanced: was 0.98, now 0.99
        
        # Default: enhance if confidence is not extremely high
        return issue.confidence < 0.98  # Enhanced: was 0.95, now 0.98
    
    async def enhance_issue(
        self, 
        issue: GrammarIssue,
        context_before: str = "",
        context_after: str = ""
    ) -> GrammarIssue:
        """
        Enhance a single grammar issue using LLM
        
        Args:
            issue: Grammar issue to enhance
            context_before: Text before the issue (for context)
            context_after: Text after the issue (for context)
            
        Returns:
            Enhanced grammar issue
        """
        if not self.enabled or not self.client:
            return issue
        
        try:
            # Build prompt with context
            prompt = self._build_enhancement_prompt(issue, context_before, context_after)
            
            # Estimate cost
            input_tokens = self.count_tokens(prompt)
            estimated_output = 150
            estimated_cost = self.estimate_cost(input_tokens, estimated_output)
            
            print(f"[LLMEnhancer] Enhancing issue on line {issue.line_number} (est. ${estimated_cost:.4f})")
            
            # Call LLM with retry logic
            response = await self._make_llm_request_with_retry(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional writing coach and grammar expert. Provide contextual, human-like corrections that reference the sentence and explain why the change improves the text. Make your fixes sound natural and conversational, as if you're personally helping someone improve their writing. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Calculate actual cost
            actual_cost = self.estimate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            
            # Track costs
            self.total_cost += actual_cost
            self.total_issues_enhanced += 1
            
            print(f"[LLMEnhancer] Enhanced (actual cost: ${actual_cost:.4f})")
            
            # Apply enhancement
            enhanced_issue = self._apply_enhancement(issue, result)
            return enhanced_issue
            
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower():
                print(f"⚠️ [LLMEnhancer] Timeout enhancing issue on line {issue.line_number} after {self.request_timeout}s with {self.max_retries} retries")
            elif "rate limit" in error_msg.lower():
                print(f"⚠️ [LLMEnhancer] Rate limited enhancing issue on line {issue.line_number}: {error_msg}")
            else:
                print(f"⚠️ [LLMEnhancer] Error enhancing issue on line {issue.line_number}: {error_msg}")
            return issue  # Return original if enhancement fails
    
    async def enhance_issues_batch(
        self,
        issues: List[GrammarIssue],
        document_text: str,
        max_issues: Optional[int] = None
    ) -> Tuple[List[GrammarIssue], float]:
        """
        Enhance multiple issues in a single API call (more cost-efficient)
        
        Args:
            issues: List of all grammar issues
            document_text: Full document text for context
            max_issues: Maximum number of issues to enhance (cost control)
            
        Returns:
            Tuple of (enhanced_issues, total_cost)
        """
        if not self.enabled or not self.client:
            return issues, 0.0
        
        # Decide which issues to enhance
        if self.enhance_all:
            issues_to_enhance = issues
        else:
            issues_to_enhance = [
                issue for issue in issues 
                if self.should_enhance_issue(issue)
            ]
            # Optional cap for cost control when not enhancing all
            if isinstance(max_issues, int) and max_issues > 0:
                issues_to_enhance = issues_to_enhance[:max_issues]
        
        if not issues_to_enhance:
            print("[LLMEnhancer] No issues need enhancement")
            return issues, 0.0
        
        print(f"[LLMEnhancer] Enhancing {len(issues_to_enhance)}/{len(issues)} issues (batch mode)")
        
        # Process in chunks to avoid timeouts
        chunk_size = 10  # Process 10 issues per chunk to avoid timeouts
        total_cost = 0.0
        enhanced_issues = issues.copy()
        
        for i in range(0, len(issues_to_enhance), chunk_size):
            chunk = issues_to_enhance[i:i + chunk_size]
            chunk_number = (i // chunk_size) + 1
            total_chunks = (len(issues_to_enhance) + chunk_size - 1) // chunk_size
            
            print(f"[LLMEnhancer] Processing chunk {chunk_number}/{total_chunks} ({len(chunk)} issues)")
            
            try:
                # Build batch prompt for this chunk
                prompt = self._build_batch_prompt(chunk)
                
                # Estimate cost for this chunk (increase output tokens for enhanced problem descriptions)
                input_tokens = self.count_tokens(prompt)
                estimated_output = len(chunk) * 200  # Increased from 100 to 200 for better problem descriptions
                estimated_cost = self.estimate_cost(input_tokens, estimated_output)
                
                # Check cost limit (skip break when enhance_all is enabled)
                if total_cost + estimated_cost > self.max_cost_per_doc and not self.enhance_all:
                    print(f"⚠️ [LLMEnhancer] Estimated cost ${total_cost + estimated_cost:.2f} exceeds limit ${self.max_cost_per_doc:.2f}")
                    break
                
                print(f"[LLMEnhancer] Chunk {chunk_number} enhancement (est. ${estimated_cost:.4f}, {len(chunk)} issues)")
                
                # Call LLM with retry logic
                response = await self._make_llm_request_with_retry(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional writing coach and grammar expert. Provide contextual, human-like corrections that reference the sentence context and explain why changes improve the text. Make your fixes sound natural and conversational. Return ONLY valid JSON with no additional text."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=estimated_output,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                # Calculate actual cost for this chunk
                actual_cost = self.estimate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                
                # Track costs
                total_cost += actual_cost
                self.total_cost += actual_cost
                self.total_issues_enhanced += len(chunk)
                
                print(f"[LLMEnhancer] Chunk {chunk_number} complete - Actual cost: ${actual_cost:.4f}")
                
                # Parse and apply enhancements for this chunk
                try:
                    results = json.loads(response.choices[0].message.content)
                    enhanced_issues = self._apply_batch_enhancements(enhanced_issues, chunk, results)
                except json.JSONDecodeError as e:
                    print(f"⚠️ [LLMEnhancer] JSON parsing error in chunk {chunk_number}: {e}")
                    print(f"Raw response: {response.choices[0].message.content[:200]}...")
                    continue
            except Exception as e:
                error_msg = str(e)
                if "timed out" in error_msg.lower():
                    print(f"⚠️ [LLMEnhancer] Chunk {chunk_number} timeout after {self.request_timeout}s with {self.max_retries} retries")
                elif "rate limit" in error_msg.lower():
                    print(f"⚠️ [LLMEnhancer] Chunk {chunk_number} rate limited: {error_msg}")
                else:
                    print(f"⚠️ [LLMEnhancer] Chunk {chunk_number} error: {error_msg}")
                continue
        
        print(f"[LLMEnhancer] All chunks complete - Total cost: ${total_cost:.4f}")
        print(f"[LLMEnhancer] Total session cost: ${self.total_cost:.4f}, Enhanced: {self.total_issues_enhanced}")
        
        return enhanced_issues, total_cost
    
    def _build_enhancement_prompt(
        self, 
        issue: GrammarIssue,
        context_before: str,
        context_after: str
    ) -> str:
        """Build prompt for single issue enhancement"""
        # Truncate context to reasonable length
        context_before = context_before[-100:] if len(context_before) > 100 else context_before
        context_after = context_after[:100] if len(context_after) > 100 else context_after
        
        # Category-specific guidance
        category_guidance = self._get_category_guidance(issue.category)
        
        return f"""Improve this {issue.category} correction by providing a more natural, contextual fix:

**Full Sentence Context:**
"{context_before}{issue.original_text}{context_after}"

**Current Issue:**
- Problematic phrase: "{issue.original_text}"
- Current fix: "{issue.fix}"
- Problem: {issue.problem}
- Category: {issue.category}

**Category-Specific Guidance:** {category_guidance}

**IMPORTANT RULES:**
- DO NOT change URLs (https://, http://) - keep them lowercase as they are
- DO NOT capitalize protocol prefixes in URLs (https:// should remain https://)
- URLs should maintain their original formatting

**Task:** Provide a better, more natural correction that fits the sentence context and sounds human-written.

Please provide:
1. improved_problem: A more contextual and helpful problem description that explains why this is an issue in this specific sentence context
2. improved_fix: A more natural, contextual correction that references the full sentence (e.g., "In this sentence, replace 'start off' with 'start' because...")
3. corrected_sentence: The complete sentence with the fix applied
4. explanation: Why this correction improves the text in this specific context (maximum 1 sentence)
5. confidence: Your confidence in this correction (0.0-1.0)

Return ONLY valid JSON (no other text):
{{
    "improved_problem": "The phrase 'a lot of' is unnecessarily wordy and can be simplified to 'many' for more concise writing",
    "improved_fix": "In this sentence, replace 'start off' with 'start' because it's more concise and direct",
    "corrected_sentence": "The complete corrected sentence goes here",
    "explanation": "This makes the sentence more direct and professional",
    "confidence": 0.95
}}"""
    
    def _build_batch_prompt(
        self,
        issues: List[GrammarIssue]
    ) -> str:
        """Build prompt for batch enhancement"""
        issues_text = ""
        for i, issue in enumerate(issues, 1):
            # Truncate long text
            text_preview = issue.original_text[:100]
            if len(issue.original_text) > 100:
                text_preview += "..."
            
            issues_text += f"""
Issue {i}:
- Line {issue.line_number}: "{text_preview}"
- Problem: {issue.problem[:150]}
- Current Fix: {issue.fix[:100]}
- Category: {issue.category}
"""
        
        # Group issues by category for better organization
        category_groups = {}
        for issue in issues:
            if issue.category not in category_groups:
                category_groups[issue.category] = []
            category_groups[issue.category].append(issue)
        
        category_info = ""
        for category, category_issues in category_groups.items():
            guidance = self._get_category_guidance(category)
            category_info += f"\n**{category.upper()} Issues ({len(category_issues)} issues):** {guidance}"
        
        return f"""Analyze and improve these {len(issues)} grammar corrections by providing more natural, contextual fixes.
For each issue, provide a better fix that references the sentence context and sounds human-written.

{issues_text}

{category_info}

**IMPORTANT RULES:**
- DO NOT change URLs (https://, http://) - keep them lowercase as they are
- DO NOT capitalize protocol prefixes in URLs (https:// should remain https://)
- URLs should maintain their original formatting

**Instructions:** For each issue, provide:
1. A more contextual and helpful problem description that explains why this is an issue in the specific sentence context
2. A more natural, contextual fix that references the sentence context and sounds human-written
3. The complete corrected sentence

Make both the problem description and fix more contextual and natural. Instead of generic descriptions like "Awkward phrasing: 'a lot of' can be simplified to 'many'", provide contextual explanations like "The phrase 'a lot of' is unnecessarily wordy in this context and can be simplified to 'many' for more concise writing."

Return ONLY valid JSON (no other text):
{{
    "enhancements": [
        {{
            "issue_id": 1,
            "improved_problem": "The phrase 'a lot of' is unnecessarily wordy and can be simplified to 'many' for more concise writing",
            "improved_fix": "In this sentence, replace 'start off' with 'start' because it's more concise and direct",
            "corrected_sentence": "The complete corrected sentence goes here",
            "explanation": "This makes the sentence more professional and to the point"
        }},
        {{
            "issue_id": 2,
            "improved_problem": "The word 'commence' is overly formal for this context and 'begin' would sound more natural",
            "improved_fix": "In this context, use 'begin' instead of 'commence' for a more natural tone",
            "corrected_sentence": "The complete corrected sentence goes here",
            "explanation": "This improves readability and sounds more conversational"
        }}
    ]
}}"""
    
    def _apply_enhancement(self, issue: GrammarIssue, result: Dict) -> GrammarIssue:
        """
        Apply enhancement results to a single issue
        
        Args:
            issue: Original grammar issue
            result: LLM response result
            
        Returns:
            Enhanced grammar issue
        """
        # Create a copy to avoid modifying original
        enhanced = issue.copy()
        
        # Update fix with improved version
        if "improved_fix" in result and result["improved_fix"]:
            enhanced.fix = result["improved_fix"]
        
        # Set corrected sentence if provided
        if "corrected_sentence" in result and result["corrected_sentence"]:
            enhanced.corrected_sentence = result["corrected_sentence"]
        
        # Enhance the problem description itself
        if "improved_problem" in result and result["improved_problem"]:
            enhanced.problem = result["improved_problem"]
        elif "explanation" in result and result["explanation"]:
            # Fallback to adding explanation if no improved problem provided
            enhanced.problem = f"{enhanced.problem}\nAI Insight: {result['explanation']}"
        
        # Update confidence if provided and higher
        if "confidence" in result:
            try:
                llm_confidence = float(result["confidence"])
                enhanced.confidence = max(enhanced.confidence, llm_confidence)
            except (ValueError, TypeError):
                pass  # Keep original confidence
        
        return enhanced
    
    def _apply_batch_enhancements(
        self,
        all_issues: List[GrammarIssue],
        enhanced_subset: List[GrammarIssue],
        results: Dict
    ) -> List[GrammarIssue]:
        """
        Apply batch enhancement results to issues
        
        Args:
            all_issues: All original issues
            enhanced_subset: Subset that was enhanced
            results: LLM batch response
            
        Returns:
            All issues with enhancements applied
        """
        if "enhancements" not in results:
            print("⚠️ [LLMEnhancer] No 'enhancements' key in response")
            return all_issues
        
        # Create map of issue to enhancement by index
        enhancement_map = {}
        for enh in results["enhancements"]:
            try:
                issue_idx = enh.get("issue_id", 0) - 1  # Convert 1-based to 0-based
                if 0 <= issue_idx < len(enhanced_subset):
                    enhancement_map[id(enhanced_subset[issue_idx])] = enh
            except Exception as e:
                print(f"⚠️ [LLMEnhancer] Error processing enhancement: {e}")
                continue
        
        # Apply enhancements
        enhanced_issues = []
        for issue in all_issues:
            if id(issue) in enhancement_map:
                enh = enhancement_map[id(issue)]
                enhanced = issue.copy()
                
                # Apply improved fix
                if "improved_fix" in enh and enh["improved_fix"]:
                    enhanced.fix = enh["improved_fix"]
                
                # Set corrected sentence if provided
                if "corrected_sentence" in enh and enh["corrected_sentence"]:
                    enhanced.corrected_sentence = enh["corrected_sentence"]
                
                # Enhance the problem description itself
                if "improved_problem" in enh and enh["improved_problem"]:
                    enhanced.problem = enh["improved_problem"]
                elif "explanation" in enh and enh["explanation"]:
                    # Fallback to adding explanation if no improved problem provided
                    enhanced.problem = f"{enhanced.problem}\nAI Insight: {enh['explanation']}"
                
                enhanced_issues.append(enhanced)
            else:
                enhanced_issues.append(issue)
        
        print(f"[LLMEnhancer] Applied {len(enhancement_map)} enhancements")
        return enhanced_issues
    
    def _get_category_guidance(self, category: str) -> str:
        """
        Get category-specific guidance for LLM enhancement
        
        Args:
            category: Grammar issue category
            
        Returns:
            Specific guidance for the category
        """
        guidance_map = {
            'redundancy': 'Focus on eliminating unnecessary words while preserving meaning. Make suggestions more concise and direct.',
            'awkward_phrasing': 'Improve flow and naturalness. Consider alternative phrasings that sound more professional and clear.',
            'punctuation': 'Ensure proper punctuation placement and consider how punctuation affects readability and meaning.',
            'grammar': 'Fix grammatical errors while maintaining the intended meaning. Consider context-dependent grammar rules.',
            'dialogue': 'Improve dialogue formatting, punctuation, and natural speech patterns. Consider character voice and context.',
            'capitalisation': 'Fix capitalization errors while considering proper nouns, titles, and sentence structure.',
            'tense_consistency': 'Ensure consistent verb tense throughout the sentence and maintain narrative flow.',
            'spelling': 'Correct spelling errors while considering context and homophones that might change meaning.',
            'parallelism_concision': 'Improve parallel structure and eliminate redundancy. Focus on clear, concise expression.',
            'article_specificity': 'Fix article usage (a, an, the) and improve specificity by replacing vague language with precise terms. Consider whether definite or indefinite articles are more appropriate.'
        }
        
        return guidance_map.get(category, 'Improve clarity, correctness, and naturalness of the text.')
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get enhancement statistics for current session
        
        Returns:
            Dictionary with cost and usage stats
        """
        return {
            "enabled": self.enabled,
            "total_cost": self.total_cost,
            "total_issues_enhanced": self.total_issues_enhanced,
            "average_cost_per_issue": (
                self.total_cost / self.total_issues_enhanced 
                if self.total_issues_enhanced > 0 
                else 0.0
            ),
            "model": self.model if self.enabled else None,
            "provider": self.provider if self.enabled else None
        }
    
    def reset_statistics(self):
        """Reset cost tracking for new session"""
        self.total_cost = 0.0
        self.total_issues_enhanced = 0
        print("[LLMEnhancer] Statistics reset")


class CostController:
    """
    Manage and enforce LLM cost limits
    
    In production, use Redis to track costs across instances
    For now, uses in-memory tracking
    """
    
    def __init__(self):
        """Initialize cost controller with limits from environment"""
        self.daily_limit = float(os.getenv("DAILY_LLM_COST_LIMIT", "100.0"))
        self.monthly_limit = float(os.getenv("MONTHLY_LLM_COST_LIMIT", "1000.0"))
        
        # In-memory tracking (use Redis in production)
        self.costs = {}
        
        print(f"[CostController] Daily limit: ${self.daily_limit}, Monthly limit: ${self.monthly_limit}")
    
    async def can_process(self, estimated_cost: float) -> Tuple[bool, str]:
        """
        Check if processing is within budget
        
        Args:
            estimated_cost: Estimated cost for operation
            
        Returns:
            Tuple of (can_process, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        # Get current spending
        daily_spent = self.costs.get(f"daily:{today}", 0.0)
        monthly_spent = self.costs.get(f"monthly:{month}", 0.0)
        
        # Check daily limit
        if daily_spent + estimated_cost > self.daily_limit:
            return False, f"Daily budget exceeded: ${daily_spent:.2f}/${self.daily_limit:.2f}"
        
        # Check monthly limit
        if monthly_spent + estimated_cost > self.monthly_limit:
            return False, f"Monthly budget exceeded: ${monthly_spent:.2f}/${self.monthly_limit:.2f}"
        
        return True, "OK"
    
    async def record_cost(self, actual_cost: float):
        """
        Record actual spending
        
        Args:
            actual_cost: Actual cost incurred
        """
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        # Increment counters
        daily_key = f"daily:{today}"
        monthly_key = f"monthly:{month}"
        
        self.costs[daily_key] = self.costs.get(daily_key, 0.0) + actual_cost
        self.costs[monthly_key] = self.costs.get(monthly_key, 0.0) + actual_cost
        
        daily_spent = self.costs[daily_key]
        monthly_spent = self.costs[monthly_key]
        
        # Check for threshold alerts
        if daily_spent > self.daily_limit * 0.8:
            print(f"⚠️ [CostController] Daily budget at {(daily_spent/self.daily_limit)*100:.1f}%")
        
        if monthly_spent > self.monthly_limit * 0.8:
            print(f"⚠️ [CostController] Monthly budget at {(monthly_spent/self.monthly_limit)*100:.1f}%")
    
    def get_spending(self) -> Dict[str, float]:
        """Get current spending statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        return {
            "today": self.costs.get(f"daily:{today}", 0.0),
            "month": self.costs.get(f"monthly:{month}", 0.0),
            "daily_limit": self.daily_limit,
            "monthly_limit": self.monthly_limit
        }
