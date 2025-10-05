import re
import asyncio
import logging
from typing import List, Dict, Optional
import language_tool_python
from models.schemas import GrammarIssue, GrammarIssueType, ProposedFix, DocumentLine

# Set up logger
logger = logging.getLogger(__name__)

class GrammarChecker:
    """Simple grammar checker using LanguageTool"""
    
    def __init__(self):
            try:
                self.tool = language_tool_python.LanguageTool('en-US')
                print("Grammar checker: LanguageTool initialized")
            except Exception as e:
                print(f"Warning: Could not initialize LanguageTool: {e}")
                self.tool = None
    
    async def check_line(self, line: DocumentLine, line_number: int) -> List[GrammarIssue]:
        """Check a line for grammar issues"""
        issues = []
        
        for sentence_idx, sentence in enumerate(line.sentences):
            if not sentence.strip():
                continue
                
            # Check sentence for grammar issues
            sentence_issues = await self._check_sentence(sentence, line_number, sentence_idx + 1)
            issues.extend(sentence_issues)
        
        return issues
    
    async def check_text_chunk(self, chunk_text: str, chunk_lines: List[DocumentLine], start_line_number: int) -> List[GrammarIssue]:
        """Check a chunk of text for grammar issues"""
        logger.info(f"Starting chunk analysis - Start line: {start_line_number}, Chunk length: {len(chunk_text)} chars")
        
        if not self.tool:
            logger.warning("LanguageTool not available - returning empty results")
            return []
        
        if not chunk_text.strip():
            logger.info("Empty chunk text - returning empty results")
            return []
        
        try:
            # Split chunk into sentences
            sentences = self._split_into_sentences(chunk_text)
            logger.info(f"Split chunk into {len(sentences)} sentences")
            
            issues = []
            current_line = start_line_number
            
            for sentence_idx, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                logger.debug(f"Processing sentence {sentence_idx + 1}: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
                
                # Check the sentence
                sentence_issues = await self._check_sentence(sentence, current_line, sentence_idx + 1)
                issues.extend(sentence_issues)
                    
                # Estimate line progression (rough approximation)
                if '\n' in sentence:
                    current_line += sentence.count('\n')
                else:
                    current_line += 1
            
            logger.info(f"Chunk analysis complete - Found {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Error in chunk analysis: {e}", exc_info=True)
            return []
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple regex"""
        # Simple sentence splitting
        sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_endings, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    async def _check_sentence(self, sentence: str, line_number: int, sentence_number: int) -> List[GrammarIssue]:
        """Check a single sentence for grammar issues"""
        if not self.tool:
            return []
        
        try:
            # Skip very short text
            if len(sentence.strip()) < 3:
                return []
            
            # Limit text length to prevent processing issues
            max_text_length = 1000
            if len(sentence) > max_text_length:
                sentence = sentence[:max_text_length] + "..."
            
            # Run LanguageTool check
            matches = await asyncio.to_thread(self.tool.check, sentence)
            
            issues = []
            
            # Limit number of issues per sentence
            max_issues_per_sentence = 5
            issue_count = 0
            
            for match in matches:
                if issue_count >= max_issues_per_sentence:
                    break
                    
                # Extract the problematic text
                problematic_text = sentence[match.offset:match.offset + match.errorLength]
                
                # Skip if this is a proper name
                if self._is_proper_name(problematic_text, sentence, match.offset):
                    continue
                
                # Get the suggested fix
                corrected_sentence = sentence
                if match.replacements:
                    corrected_sentence = sentence[:match.offset] + match.replacements[0] + sentence[match.offset + match.errorLength:]
                
                # Create issue
                issue_type = self._categorize_issue(match.ruleId, match.message)
                
                proposed_fix = ProposedFix(
                    action="Grammar correction",
                    details=f"Replace \"{problematic_text}\" with \"{match.replacements[0] if match.replacements else '[suggestion needed]'}\".\nThe corrected sentence would be: \"{corrected_sentence}\"",
                    corrected_text=corrected_sentence
                )
                
                issues.append(GrammarIssue(
                    lines=str(line_number),
                    sentences=str(sentence_number),
                    text=sentence,
                    problem="Grammar issue",
                    reason=match.message,
                    proposed_fix=proposed_fix,
                    issue_type=issue_type,
                    confidence=0.8,
                    # Legacy fields for backward compatibility
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=sentence,
                    fix=f"Replace \"{problematic_text}\" with \"{match.replacements[0] if match.replacements else '[suggestion needed]'}\".\nThe corrected sentence would be: \"{corrected_sentence}\""
                ))
                
                issue_count += 1
            
            return issues
            
        except Exception as e:
            logger.error(f"Error checking sentence: {e}")
            return []
    
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
    
    def _is_proper_name(self, text: str, full_sentence: str, offset: int) -> bool:
        """Check if the flagged text is likely a proper name"""
        text = text.strip()
        
        # Skip empty or very short text
        if len(text) < 2:
            return False
        
        # Check if it starts with a capital letter
        if not text[0].isupper():
            return False
        
        # Get context around the text
        start_context = max(0, offset - 50)
        end_context = min(len(full_sentence), offset + len(text) + 50)
        context = full_sentence[start_context:end_context]
        
        # Simple name patterns
        name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\b(Dr|Mr|Mrs|Ms|Prof)\s+[A-Z][a-z]+\b',  # Title + Name
        ]
        
        # Check if the text matches name patterns
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