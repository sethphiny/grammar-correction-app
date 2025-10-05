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

class HybridGrammarChecker:
    """Hybrid grammar checker using spaCy and LanguageTool for enhanced accuracy"""
    
    def __init__(self):
        self.spacy_model = None
        self.language_tool = None
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
            except OSError:
                print("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
                self.spacy_model = None
            
            # Initialize LanguageTool
            languagetool_url = os.getenv("LANGUAGETOOL_URL", "http://localhost:8081")
            try:
                self.language_tool = LanguageTool('en-US', remote_server=languagetool_url)
            except Exception as e:
                print(f"Failed to connect to LanguageTool server: {e}")
                # Fallback to local LanguageTool
                try:
                    self.language_tool = LanguageTool('en-US')
                except Exception as e2:
                    print(f"Failed to initialize local LanguageTool: {e2}")
                    self.language_tool = None
                    
        except Exception as e:
            print(f"Error initializing grammar checker: {e}")
    
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
        
        # Check with spaCy
        spacy_issues = await self._check_with_spacy(sentence, line_number, sentence_number)
        issues.extend(spacy_issues)
        
        # Check with LanguageTool
        languagetool_issues = await self._check_with_languagetool(sentence, line_number, sentence_number)
        issues.extend(languagetool_issues)
        
        # Cross-validate and merge similar issues
        merged_issues = self._merge_similar_issues(issues)
        
        return merged_issues
    
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
                
                issue = GrammarIssue(
                    line_number=line_number,
                    sentence_number=sentence_number,
                    original_text=problematic_text,
                    problem=match.message,
                    fix=fix_text,
                    category=category,
                    confidence=0.8  # LanguageTool confidence
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
        
        # Find all verbs and their tenses
        verbs = [token for token in doc if token.pos_ == "VERB"]
        tenses = {}
        
        for verb in verbs:
            tense = verb.morph.get("Tense")
            if tense:
                tenses[verb.text.lower()] = tense[0]
        
        # Check for tense inconsistencies
        if len(set(tenses.values())) > 1:
            # Multiple tenses found - potential issue
            issue = GrammarIssue(
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=sentence,
                problem="Tense inconsistency detected - multiple verb tenses in the same sentence",
                fix="Consider using consistent tense throughout the sentence",
                category="tense_consistency",
                confidence=0.7
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
                if verb.pos_ == "VERB":
                    # Check if subject and verb agree in number
                    subject_number = token.morph.get("Number")
                    verb_number = verb.morph.get("Number")
                    
                    if subject_number and verb_number:
                        if subject_number[0] != verb_number[0]:
                            issue = GrammarIssue(
                                line_number=line_number,
                                sentence_number=sentence_number,
                                original_text=f"{token.text} {verb.text}",
                                problem=f"Subject-verb disagreement: {token.text} ({subject_number[0]}) and {verb.text} ({verb_number[0]})",
                                fix=f"Use {verb.text} with {subject_number[0]} subject",
                                category="subject_verb_agreement",
                                confidence=0.8
                            )
                            issues.append(issue)
        
        return issues
    
    def _check_awkward_phrasing(
        self, 
        doc, 
        sentence: str, 
        line_number: int, 
        sentence_number: int
    ) -> List[GrammarIssue]:
        """Check for awkward phrasing patterns"""
        issues = []
        
        # Check for passive voice overuse
        passive_verbs = [token for token in doc if token.tag_ == "VBN" and token.dep_ == "auxpass"]
        if len(passive_verbs) > 0:
            issue = GrammarIssue(
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=sentence,
                problem="Passive voice detected - consider using active voice for clarity",
                fix="Rewrite using active voice where possible",
                category="awkward_phrasing",
                confidence=0.6
            )
            issues.append(issue)
        
        # Check for overly long sentences
        if len(doc) > 30:  # Arbitrary threshold
            issue = GrammarIssue(
                line_number=line_number,
                sentence_number=sentence_number,
                original_text=sentence,
                problem="Sentence is quite long - consider breaking it into shorter sentences",
                fix="Split into multiple sentences for better readability",
                category="awkward_phrasing",
                confidence=0.5
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
        
        # Common redundant phrases
        redundant_patterns = [
            (r'\b(and then)\b', 'then'),
            (r'\b(and they)\b', 'they'),
            (r'\b(and it)\b', 'it'),
            (r'\b(and he)\b', 'he'),
            (r'\b(and she)\b', 'she'),
            (r'\b(and we)\b', 'we'),
            (r'\b(and you)\b', 'you'),
            (r'\b(and I)\b', 'I'),
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
                    confidence=0.7
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
