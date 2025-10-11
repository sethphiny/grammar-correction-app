"""
LLM Enhancement Service for Grammar Corrections

Provides AI-powered enhancement of grammar fixes using OpenAI GPT-4o-mini
Cost-optimized with selective enhancement, batching, and optional caching
"""

import os
import json
import asyncio
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
        
        Only enhance:
        1. Low confidence issues (< 0.85)
        2. Complex categories that benefit from context
        3. Issues without corrected sentences
        
        Args:
            issue: Grammar issue to evaluate
            
        Returns:
            True if issue should be enhanced, False otherwise
        """
        # Enhance if confidence is low
        if issue.confidence < 0.85:
            return True
        
        # Enhance complex categories
        complex_categories = {
            'awkward_phrasing',
            'tense_consistency',
            'parallelism_concision',
            'dialogue'
        }
        
        if issue.category in complex_categories:
            return True
        
        # Enhance if no corrected sentence provided
        if not issue.corrected_sentence:
            return True
        
        return False
    
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
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional grammar expert. Provide clear, concise corrections with brief explanations. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=150,
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
            print(f"⚠️ [LLMEnhancer] Error enhancing issue on line {issue.line_number}: {e}")
            return issue  # Return original if enhancement fails
    
    async def enhance_issues_batch(
        self,
        issues: List[GrammarIssue],
        document_text: str,
        max_issues: int = 20
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
        
        # Filter issues that need enhancement
        issues_to_enhance = [
            issue for issue in issues 
            if self.should_enhance_issue(issue)
        ][:max_issues]  # Limit to avoid excessive costs
        
        if not issues_to_enhance:
            print("[LLMEnhancer] No issues need enhancement")
            return issues, 0.0
        
        print(f"[LLMEnhancer] Enhancing {len(issues_to_enhance)}/{len(issues)} issues (batch mode)")
        
        try:
            # Build batch prompt
            prompt = self._build_batch_prompt(issues_to_enhance)
            
            # Estimate cost
            input_tokens = self.count_tokens(prompt)
            estimated_output = len(issues_to_enhance) * 100
            estimated_cost = self.estimate_cost(input_tokens, estimated_output)
            
            # Check cost limit
            if estimated_cost > self.max_cost_per_doc:
                print(f"⚠️ [LLMEnhancer] Estimated cost ${estimated_cost:.2f} exceeds limit ${self.max_cost_per_doc:.2f}")
                return issues, 0.0
            
            print(f"[LLMEnhancer] Batch enhancement (est. ${estimated_cost:.4f}, {len(issues_to_enhance)} issues)")
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional grammar expert. Analyze and improve grammar corrections. Return ONLY valid JSON with no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=estimated_output,
                response_format={"type": "json_object"}
            )
            
            # Calculate actual cost
            actual_cost = self.estimate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            
            # Track costs
            self.total_cost += actual_cost
            self.total_issues_enhanced += len(issues_to_enhance)
            
            print(f"[LLMEnhancer] Batch complete - Actual cost: ${actual_cost:.4f}")
            print(f"[LLMEnhancer] Total session cost: ${self.total_cost:.4f}, Enhanced: {self.total_issues_enhanced}")
            
            # Parse and apply enhancements
            results = json.loads(response.choices[0].message.content)
            enhanced_issues = self._apply_batch_enhancements(issues, issues_to_enhance, results)
            
            return enhanced_issues, actual_cost
            
        except json.JSONDecodeError as e:
            print(f"⚠️ [LLMEnhancer] Failed to parse LLM response: {e}")
            return issues, 0.0
        except Exception as e:
            print(f"⚠️ [LLMEnhancer] Batch enhancement error: {e}")
            return issues, 0.0
    
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
        
        return f"""Improve this grammar correction:

Context Before: "{context_before}"
**Issue Text**: "{issue.original_text[:200]}"
Context After: "{context_after}"

Current Analysis:
- Problem: {issue.problem}
- Current Fix: {issue.fix}
- Category: {issue.category}
- Confidence: {issue.confidence}

Please provide:
1. improved_fix: A better, more natural correction (keep concise)
2. explanation: Why this correction improves the text (maximum 1 sentence)
3. confidence: Your confidence in this correction (0.0-1.0)

Return ONLY valid JSON (no other text):
{{
    "improved_fix": "your improved correction here",
    "explanation": "why this is better",
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
        
        return f"""Analyze and improve these {len(issues)} grammar corrections.
For each issue, provide a better fix and brief explanation.

{issues_text}

Return ONLY valid JSON (no other text):
{{
    "enhancements": [
        {{
            "issue_id": 1,
            "improved_fix": "better correction here",
            "explanation": "why it's better (1 sentence max)"
        }},
        {{
            "issue_id": 2,
            "improved_fix": "better correction here",
            "explanation": "why it's better (1 sentence max)"
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
            enhanced.fix = f"✨ {result['improved_fix']}"
        
        # Add explanation to problem
        if "explanation" in result and result["explanation"]:
            enhanced.problem = f"{enhanced.problem}\n💡 AI Insight: {result['explanation']}"
        
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
                    enhanced.fix = f"✨ {enh['improved_fix']}"
                
                # Add explanation
                if "explanation" in enh and enh["explanation"]:
                    enhanced.problem = f"{enhanced.problem}\n💡 AI Insight: {enh['explanation']}"
                
                enhanced_issues.append(enhanced)
            else:
                enhanced_issues.append(issue)
        
        print(f"[LLMEnhancer] Applied {len(enhancement_map)} enhancements")
        return enhanced_issues
    
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
