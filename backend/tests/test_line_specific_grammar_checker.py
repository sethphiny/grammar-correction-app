import pytest
import asyncio
from services.line_specific_grammar_checker import LineSpecificGrammarChecker
from models.schemas import DocumentLine, GrammarIssueType

class TestLineSpecificGrammarChecker:
    """Test the line-specific grammar checker with the exact examples provided"""
    
    @pytest.fixture
    def checker(self):
        return LineSpecificGrammarChecker()
    
    @pytest.mark.asyncio
    async def test_tense_shift_detection(self, checker):
        """Test tense shift detection - 'come' vs 'came' in past tense context"""
        # Line 13-15 example
        line = DocumentLine(
            line_number=13,
            content="Even in retirement, he carried the image of a railing set in stone, the kind that never moved. New boys come to him to watch him measure so they can learn.",
            sentences=["Even in retirement, he carried the image of a railing set in stone, the kind that never moved.", "New boys come to him to watch him measure so they can learn."]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect tense shift: "come" should be "came" in past tense context
        tense_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.VERB_TENSE]
        assert len(tense_issues) > 0, "Should detect tense shift issue"
        
        # Check that the issue is about "come" vs "came"
        come_issue = None
        for issue in tense_issues:
            if "come" in issue.original_text.lower() and "came" in issue.fix.lower():
                come_issue = issue
                break
        
        assert come_issue is not None, "Should detect 'come' vs 'came' tense shift"
        assert "Tense shift" in come_issue.problem
        assert "came" in come_issue.corrected_text
    
    @pytest.mark.asyncio
    async def test_extra_comma_quotation(self, checker):
        """Test extra comma before closing quotation mark"""
        # Line 24 example
        line = DocumentLine(
            line_number=24,
            content="...then laughed, 'My mind's only rearranging its filing cabinet,'.",
            sentences=["...then laughed, 'My mind's only rearranging its filing cabinet,'."]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect extra comma before closing quotation mark
        punctuation_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.GRAMMAR_PUNCTUATION]
        assert len(punctuation_issues) > 0, "Should detect punctuation issue"
        
        # Check that the issue is about extra comma
        comma_issue = None
        for issue in punctuation_issues:
            if "comma" in issue.problem.lower() and "quotation" in issue.problem.lower():
                comma_issue = issue
                break
        
        assert comma_issue is not None, "Should detect extra comma before quotation mark"
        assert "Extra comma" in comma_issue.problem
        assert "," not in comma_issue.corrected_text or comma_issue.corrected_text.count(",") < line.content.count(",")
    
    @pytest.mark.asyncio
    async def test_awkward_word_choice(self, checker):
        """Test awkward word choice - 'tentative' for laughter"""
        # Line 44 example
        line = DocumentLine(
            line_number=44,
            content="...He laughed, but it wasn't his usual gut-deep guffaw. This one was thin, tentative.",
            sentences=["...He laughed, but it wasn't his usual gut-deep guffaw.", "This one was thin, tentative."]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect awkward word choice
        awkward_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.AWKWARD_PHRASING]
        assert len(awkward_issues) > 0, "Should detect awkward phrasing issue"
        
        # Check that the issue is about "tentative" for laughter
        tentative_issue = None
        for issue in awkward_issues:
            if "tentative" in issue.original_text.lower() and ("uncertain" in issue.fix.lower() or "hesitant" in issue.fix.lower()):
                tentative_issue = issue
                break
        
        assert tentative_issue is not None, "Should detect 'tentative' as awkward word choice"
        assert "Awkward word choice" in tentative_issue.problem
        assert "tentative" not in tentative_issue.corrected_text or "uncertain" in tentative_issue.corrected_text or "hesitant" in tentative_issue.corrected_text
    
    @pytest.mark.asyncio
    async def test_awkward_phrasing(self, checker):
        """Test awkward phrasing - 'lost his cup out of his hands'"""
        # Line 59 example
        line = DocumentLine(
            line_number=59,
            content="...One morning, he lost his cup out of his hands…",
            sentences=["...One morning, he lost his cup out of his hands…"]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect awkward phrasing
        awkward_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.AWKWARD_PHRASING]
        assert len(awkward_issues) > 0, "Should detect awkward phrasing issue"
        
        # Check that the issue is about the awkward phrasing
        phrasing_issue = None
        for issue in awkward_issues:
            if "lost" in issue.original_text.lower() and "slipped" in issue.fix.lower():
                phrasing_issue = issue
                break
        
        assert phrasing_issue is not None, "Should detect awkward phrasing with 'lost'"
        assert "Awkward phrasing" in phrasing_issue.problem
        assert "slipped" in phrasing_issue.corrected_text
    
    @pytest.mark.asyncio
    async def test_subject_verb_agreement_complex(self, checker):
        """Test subject-verb agreement in complex sentences"""
        # Line 83 example
        line = DocumentLine(
            line_number=83,
            content="...'the good news is that long-term memory—the birthdays, family names, history facts, is still intact.'",
            sentences=["...'the good news is that long-term memory—the birthdays, family names, history facts, is still intact.'"]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect subject-verb agreement issue
        verb_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.VERB_TENSE]
        assert len(verb_issues) > 0, "Should detect verb agreement issue"
        
        # Check that the issue is about subject-verb agreement
        agreement_issue = None
        for issue in verb_issues:
            if "agreement" in issue.problem.lower() and ("is" in issue.original_text.lower() and "are" in issue.fix.lower()):
                agreement_issue = issue
                break
        
        assert agreement_issue is not None, "Should detect subject-verb agreement issue"
        assert "Subject–verb agreement" in agreement_issue.problem
        assert "are" in agreement_issue.corrected_text
    
    @pytest.mark.asyncio
    async def test_multiple_issues_in_line(self, checker):
        """Test that multiple issues can be detected in a single line"""
        # Create a line with multiple issues
        line = DocumentLine(
            line_number=1,
            content="Yesterday, he come to see me, and said, 'Hello there,'.",
            sentences=["Yesterday, he come to see me, and said, 'Hello there,'."]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        # Should detect multiple issues
        assert len(issues) >= 2, "Should detect multiple issues in the line"
        
        # Check for tense shift
        tense_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.VERB_TENSE]
        assert len(tense_issues) > 0, "Should detect tense shift"
        
        # Check for punctuation issue
        punctuation_issues = [issue for issue in issues if issue.issue_type == GrammarIssueType.GRAMMAR_PUNCTUATION]
        assert len(punctuation_issues) > 0, "Should detect punctuation issue"
    
    def test_tense_context_detection(self, checker):
        """Test that tense context is correctly detected"""
        # Test past tense context
        past_sentence = "Yesterday, he went to the store and bought some milk."
        past_context = checker._determine_tense_context(past_sentence)
        assert past_context == "past", "Should detect past tense context"
        
        # Test present tense context
        present_sentence = "Today, he goes to the store and buys some milk."
        present_context = checker._determine_tense_context(present_sentence)
        assert present_context == "present", "Should detect present tense context"
    
    def test_verb_finding(self, checker):
        """Test that verbs are correctly identified in sentences"""
        sentence = "He went to the store and bought some milk."
        verbs = checker._find_verbs_in_sentence(sentence)
        
        # Should find "went" and "bought"
        verb_words = [verb_info['verb'] for verb_info in verbs]
        assert "went" in verb_words, "Should find 'went'"
        assert "bought" in verb_words, "Should find 'bought'"

if __name__ == "__main__":
    # Run a simple test
    async def run_test():
        checker = LineSpecificGrammarChecker()
        
        # Test the tense shift example
        line = DocumentLine(
            line_number=13,
            content="Even in retirement, he carried the image of a railing set in stone, the kind that never moved. New boys come to him to watch him measure so they can learn.",
            sentences=["Even in retirement, he carried the image of a railing set in stone, the kind that never moved.", "New boys come to him to watch him measure so they can learn."]
        )
        
        issues = await checker.check_line_specific_issues(line)
        
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"- Line {issue.line_number}: {issue.problem}")
            print(f"  Reason: {issue.reason}")
            print(f"  Fix: {issue.fix}")
            print(f"  Corrected: {issue.corrected_text}")
            print()
    
    asyncio.run(run_test())
