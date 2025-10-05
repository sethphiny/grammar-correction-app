import asyncio
import logging
from typing import List, Dict, Optional, AsyncGenerator
import language_tool_python
from models.schemas import GrammarIssue, GrammarIssueType, ProposedFix, DocumentLine
from .enhanced_grammar_checker import EnhancedGrammarChecker
from .line_specific_grammar_checker import LineSpecificGrammarChecker

logger = logging.getLogger(__name__)

class StreamingGrammarChecker:
    """
    Streaming grammar checker that processes sentences individually and yields results progressively.
    Skips timeout-prone sentences instead of retrying to prevent hanging.
    """
    
    def __init__(self, use_server_mode: bool = False, server_url: Optional[str] = None):
        self.use_server_mode = use_server_mode
        self.server_url = server_url
        
        # Initialize enhanced grammar checker
        self.enhanced_checker = EnhancedGrammarChecker(use_server_mode, server_url)
        
        # Initialize line-specific grammar checker
        self.line_specific_checker = LineSpecificGrammarChecker()
        
        # Keep the original tool for backward compatibility
        try:
            if use_server_mode and server_url:
                # Use public API for better performance and reliability
                self.tool = language_tool_python.LanguageToolPublicAPI('en-US')
                logger.info(f"Streaming grammar checker: Connected to LanguageTool server at {server_url}")
            else:
                # Use local instance with optimized settings
                self.tool = language_tool_python.LanguageTool('en-US')
                # Configure for better performance
                if hasattr(self.tool, 'disabled_rules'):
                    # Disable some slow rules that often cause timeouts
                    self.tool.disabled_rules = [
                        'WHITESPACE_RULE',  # Often causes issues with complex text
                        'EN_QUOTES',        # Can be slow with complex punctuation
                        'COMMA_PARENTHESIS_WHITESPACE'  # Often triggers on complex sentences
                    ]
                logger.info("Streaming grammar checker: LanguageTool initialized (local mode with optimizations)")
        except Exception as e:
            logger.error(f"Could not initialize LanguageTool: {e}")
            self.tool = None
    
    async def process_document_streaming(
        self, 
        lines: List[DocumentLine], 
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process document line by line, yielding results as they're completed.
        
        Args:
            lines: List of DocumentLine objects to process
            progress_callback: Optional callback for progress updates
            
        Yields:
            Dict with processing results and progress information
        """
        total_lines = len(lines)
        processed_lines = 0
        total_issues = 0
        skipped_sentences = 0
        
        logger.info(f"Starting streaming processing of {total_lines} lines")
        
        for line_idx, line in enumerate(lines):
            line_issues = []
            
            # First, run line-specific checker for targeted issue detection
            try:
                line_specific_issues = await self.line_specific_checker.check_line_specific_issues(line)
                line_issues.extend(line_specific_issues)
            except Exception as e:
                logger.error(f"Error in line-specific checker: {e}")
            
            # Process each sentence in the line
            for sentence_idx, sentence in enumerate(line.sentences):
                if not sentence.strip():
                    continue
                
                # Preprocess sentence to break up very long sentences
                processed_sentences = self._preprocess_sentence(sentence)
                
                for sub_sentence_idx, processed_sentence in enumerate(processed_sentences):
                    if not processed_sentence.strip():
                        continue
                    
                    try:
                        # Process sentence with enhanced checker
                        sentence_issues = await asyncio.wait_for(
                            self.enhanced_checker.check_sentence(processed_sentence, line.line_number, sentence_idx + 1),
                            timeout=120  # 120 second timeout per sentence
                        )
                        line_issues.extend(sentence_issues)
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"Sentence timed out, skipping: '{processed_sentence[:50]}...'")
                        skipped_sentences += 1
                        continue
                    except Exception as e:
                        logger.error(f"Error processing sentence: {e}")
                        skipped_sentences += 1
                        continue
            
            # Update progress
            processed_lines += 1
            total_issues += len(line_issues)
            
            # Calculate progress percentage
            progress = int((processed_lines / total_lines) * 100)
            
            # Yield results for this line
            yield {
                'type': 'line_completed',
                'line_number': line.line_number,
                'issues': line_issues,
                'progress': progress,
                'processed_lines': processed_lines,
                'total_lines': total_lines,
                'total_issues': total_issues,
                'skipped_sentences': skipped_sentences
            }
            
            # Call progress callback if provided
            if progress_callback:
                await progress_callback(progress, processed_lines, total_lines, total_issues)
        
        # Final completion message
        yield {
            'type': 'processing_complete',
            'total_issues': total_issues,
            'processed_lines': processed_lines,
            'skipped_sentences': skipped_sentences,
            'progress': 100
        }
        
        logger.info(f"Streaming processing complete: {total_issues} issues found, {skipped_sentences} sentences skipped")
    
    async def _check_sentence(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check a single sentence for grammar issues with timeout protection"""
        if not self.tool:
            return []
        
        try:
            # Skip very short text
            if len(sentence.strip()) < 3:
                return []
            
            # Clean sentence
            clean_sentence = self._extract_clean_sentence(sentence)
            if len(clean_sentence) < 3:
                return []
            
            # Optimize text length - preprocessed sentences should already be reasonable length
            max_text_length = 1500  # Increased from 1000 since we're preprocessing
            if len(clean_sentence) > max_text_length:
                clean_sentence = clean_sentence[:max_text_length] + "..."
            
            # Additional optimization: skip sentences that are likely to timeout
            if len(clean_sentence) > 1000 and clean_sentence.count(',') > 10:
                logger.info(f"Skipping complex sentence with many commas: {clean_sentence[:50]}...")
                return []
            
            # Check with LanguageTool using optimized settings
            matches = await asyncio.to_thread(self._check_with_optimizations, clean_sentence)
            
            if not matches:
                return []
            
            # Convert matches to issues
            issues = self._convert_matches_to_issues(matches, sentence, clean_sentence, line_number, sentence_number)
            
            return issues
            
        except Exception as e:
            logger.error(f"Error checking sentence: {e}")
            return []
    
    def _check_with_optimizations(self, text: str):
        """Check text with LanguageTool using optimized settings"""
        try:
            # Use check method with optimized parameters
            if hasattr(self.tool, 'check'):
                return self.tool.check(text)
            else:
                return []
        except Exception as e:
            logger.warning(f"LanguageTool check failed: {e}")
            return []
    
    def _extract_clean_sentence(self, sentence: str) -> str:
        """Extract clean sentence text by removing numbering and formatting"""
        import re
        
        # Remove common numbering patterns
        cleaned = re.sub(r'^\s*\d+\.\s*', '', sentence)  # Remove "1. ", "2. ", etc.
        cleaned = re.sub(r'^\s*[a-zA-Z]\.\s*', '', cleaned)  # Remove "a. ", "b. ", etc.
        cleaned = re.sub(r'^\s*[ivx]+\.\s*', '', cleaned, flags=re.IGNORECASE)  # Remove "i. ", "ii. ", etc.
        
        return cleaned.strip()
    
    def _preprocess_sentence(self, sentence: str) -> List[str]:
        """Preprocess sentence to break up very long or complex sentences"""
        import re
        
        # If sentence is reasonably short, return as-is
        if len(sentence) <= 200:
            return [sentence]
        
        # Break up very long sentences by common delimiters
        sentences = []
        
        # Split by semicolons first (often separate independent clauses)
        if ';' in sentence:
            parts = sentence.split(';')
            for part in parts:
                part = part.strip()
                if len(part) > 3:
                    sentences.append(part)
            return sentences
        
        # Split by conjunctions (and, but, or, so, yet, for, nor)
        conjunctions = r'\b(and|but|or|so|yet|for|nor)\b'
        if re.search(conjunctions, sentence, re.IGNORECASE):
            parts = re.split(conjunctions, sentence, flags=re.IGNORECASE)
            current_sentence = ""
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                if i % 2 == 0:  # Even indices are sentence parts
                    current_sentence = part
                else:  # Odd indices are conjunctions
                    if current_sentence and len(current_sentence) > 3:
                        sentences.append(current_sentence)
                    current_sentence = ""
            if current_sentence and len(current_sentence) > 3:
                sentences.append(current_sentence)
            return sentences if sentences else [sentence]
        
        # Split by commas if sentence is very long (>500 chars)
        if len(sentence) > 500 and ',' in sentence:
            parts = sentence.split(',')
            current_sentence = ""
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if len(current_sentence + part) > 300:
                    if current_sentence and len(current_sentence) > 3:
                        sentences.append(current_sentence)
                    current_sentence = part
                else:
                    current_sentence += (", " + part) if current_sentence else part
            if current_sentence and len(current_sentence) > 3:
                sentences.append(current_sentence)
            return sentences if sentences else [sentence]
        
        # If still too long, force split at reasonable length
        if len(sentence) > 800:
            words = sentence.split()
            current_sentence = ""
            for word in words:
                if len(current_sentence + word) > 400:
                    if current_sentence and len(current_sentence) > 3:
                        sentences.append(current_sentence.strip())
                    current_sentence = word
                else:
                    current_sentence += (" " + word) if current_sentence else word
            if current_sentence and len(current_sentence) > 3:
                sentences.append(current_sentence.strip())
            return sentences if sentences else [sentence]
        
        return [sentence]
    
    def _convert_matches_to_issues(self, matches, original_sentence: str, clean_sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Convert LanguageTool matches to GrammarIssue objects"""
        issues = []
        
        # Filter out proper names and collect valid matches
        valid_matches = []
        for match in matches:
            problematic_text = clean_sentence[match.offset:match.offset + match.errorLength]
            if not self._is_proper_name(problematic_text, clean_sentence, match.offset):
                valid_matches.append(match)
        
        if not valid_matches:
            return []
        
        # Group matches by issue type
        issue_groups = {}
        for match in valid_matches:
            issue_type = self._categorize_issue(match.ruleId, match.message)
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(match)
        
        # Create one issue per issue type
        for issue_type, type_matches in issue_groups.items():
            type_matches.sort(key=lambda x: x.offset)
            
            # Build comprehensive fix
            corrected_sentence = clean_sentence
            fix_details = []
            
            # Apply fixes in reverse order
            for match in reversed(type_matches):
                if match.replacements:
                    original_text = clean_sentence[match.offset:match.offset + match.errorLength]
                    replacement = match.replacements[0]
                    
                    corrected_sentence = corrected_sentence[:match.offset] + replacement + corrected_sentence[match.offset + match.errorLength:]
                    fix_details.append(f'Replace "{original_text}" with "{replacement}"')
            
            # Create consolidated fix description
            fix_description = '; '.join(fix_details) if len(fix_details) > 1 else fix_details[0] if fix_details else "Apply suggested corrections"
            
            proposed_fix = ProposedFix(
                action="Grammar correction",
                details=f"{fix_description}.",
                corrected_text=corrected_sentence
            )
            
            main_message = type_matches[0].message if len(type_matches) == 1 else f"Multiple {issue_type.value.replace('_', ' ')} issues found"
            
            issues.append(GrammarIssue(
                lines=str(line_number),
                sentences=str(sentence_number),
                text=original_sentence,
                problem=f"Grammar issue ({issue_type.value.replace('_', ' ')})",
                reason=main_message,
                proposed_fix=proposed_fix,
                issue_type=issue_type,
                confidence=0.8,
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=original_sentence,
                fix=f"{fix_description}.",
                corrected_text=corrected_sentence
            ))
        
        return issues
    
    def _categorize_issue(self, rule_id: str, message: str) -> GrammarIssueType:
        """Categorize issues by type"""
        rule_id_upper = rule_id.upper()
        message_lower = message.lower()
        
        # Check against category map
        if any(keyword in rule_id_upper for keyword in ['TENSE', 'VERB', 'VB']):
            return GrammarIssueType.VERB_TENSE
        elif any(keyword in rule_id_upper for keyword in ['PUNCTUATION', 'COMMA', 'QUOTATION']):
            return GrammarIssueType.GRAMMAR_PUNCTUATION
        elif any(keyword in message_lower for keyword in ['awkward', 'wordy', 'unclear']):
            return GrammarIssueType.AWKWARD_PHRASING
        elif any(keyword in message_lower for keyword in ['redundant', 'repetitive']):
            return GrammarIssueType.REDUNDANCY
        else:
            return GrammarIssueType.GRAMMAR_PUNCTUATION
    
    def _is_proper_name(self, text: str, full_sentence: str, offset: int) -> bool:
        """Check if text is likely a proper name"""
        import re
        
        text = text.strip()
        
        if len(text) < 2 or not text[0].isupper():
            return False
        
        # Get context around the text
        start_context = max(0, offset - 50)
        end_context = min(len(full_sentence), offset + len(text) + 50)
        context = full_sentence[start_context:end_context]
        
        # Common patterns that indicate proper names
        name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b',
            r'\b(Dr|Mr|Mrs|Ms|Prof|Professor)\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+(Jr|Sr|III|IV|V)\b',
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True
        
        return False
    
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
