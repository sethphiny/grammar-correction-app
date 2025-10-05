#!/usr/bin/env python3
"""
Comprehensive test script to run the line-specific grammar checker on test.docx
and also test with examples that match our specific patterns
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.document_parser import DocumentParser
from services.line_specific_grammar_checker import LineSpecificGrammarChecker
from services.grammar_checker import GrammarChecker
from models.schemas import DocumentLine

async def test_with_docx():
    """Test the line-specific grammar checker with test.docx and custom examples"""
    
    # Initialize the document parser and grammar checkers
    parser = DocumentParser()
    line_specific_checker = LineSpecificGrammarChecker()
    general_checker = GrammarChecker()
    
    print(f"=== Comprehensive Grammar Checker Testing ===")
    print()
    
    # First, test with the actual test.docx
    test_docx_path = backend_dir.parent / "test.docx"
    
    if test_docx_path.exists():
        print("1. Testing with test.docx:")
        print("-" * 60)
        
        try:
            # Parse the document
            lines = await parser.parse_document(str(test_docx_path))
            print(f"   ✓ Parsed {len(lines)} lines from document")
            
            # Show some key lines that have grammar issues
            print("\n   Key lines with potential issues:")
            for line in lines:
                if line.content.strip() and any(keyword in line.content.lower() for keyword in ['contain', 'go to', 'buy some', 'there is many']):
                    print(f"   Line {line.line_number}: {line.content}")
            
            print("\n   Running line-specific grammar checker...")
            total_issues = 0
            for line in lines:
                if line.content.strip():
                    issues = await line_specific_checker.check_line_specific_issues(line)
                    if issues:
                        total_issues += len(issues)
                        print(f"\n   📝 Line {line.line_number}: {line.content}")
                        for issue in issues:
                            print(f"      🔍 Issue: {issue.problem}")
                            print(f"         Reason: {issue.reason}")
                            print(f"         Fix: {issue.fix}")
            
            print(f"\n   ✓ Found {total_issues} issues with line-specific checker")
            
        except Exception as e:
            print(f"   Error parsing test.docx: {e}")
    
    print("\n" + "="*60)
    print("2. Testing with examples that match our specific patterns:")
    print("-" * 60)
    
    # Test with examples that should trigger our specific patterns
    test_examples = [
        {
            'name': 'Tense shift example (like your Line 13-15)',
            'content': "Even in retirement, he carried the image of a railing set in stone, the kind that never moved. New boys come to him to watch him measure so they can learn."
        },
        {
            'name': 'Extra comma before quotation (like your Line 24)',
            'content': "...then laughed, 'My mind's only rearranging its filing cabinet,'."
        },
        {
            'name': 'Awkward word choice for laughter (like your Line 44)',
            'content': "...He laughed, but it wasn't his usual gut-deep guffaw. This one was thin, tentative."
        },
        {
            'name': 'Awkward phrasing (like your Line 59)',
            'content': "...One morning, he lost his cup out of his hands…"
        },
        {
            'name': 'Subject-verb agreement (like your Line 83)',
            'content': "...'the good news is that long-term memory—the birthdays, family names, history facts, is still intact.'"
        },
        {
            'name': 'Test document tense issue',
            'content': "Yesterday I go to the store and buy some groceries."
        },
        {
            'name': 'Test document subject-verb issue',
            'content': "There is many people who think this is a good idea."
        }
    ]
    
    for i, example in enumerate(test_examples, 1):
        print(f"\n   Example {i}: {example['name']}")
        print(f"   Original: {example['content']}")
        
        # Create a DocumentLine for this example
        line = DocumentLine(
            line_number=i,
            content=example['content'],
            sentences=[example['content']]
        )
        
        # Test with line-specific checker
        issues = await line_specific_checker.check_line_specific_issues(line)
        if issues:
            print(f"   🔍 Line-specific checker found {len(issues)} issue(s):")
            for issue in issues:
                print(f"      • {issue.problem}: {issue.reason}")
                print(f"        Fix: {issue.fix}")
                print(f"        Corrected: {issue.corrected_text}")
        else:
            print(f"   ✓ Line-specific checker: No issues found")
        
        # Also test with general grammar checker for comparison
        try:
            general_issues = await general_checker.check_line(line, i)
            if general_issues:
                print(f"   📝 General checker found {len(general_issues)} issue(s):")
                for issue in general_issues:
                    print(f"      • {issue.problem}: {issue.reason}")
            else:
                print(f"   ✓ General checker: No issues found")
        except Exception as e:
            print(f"   ⚠ General checker error: {e}")
    
    print("\n" + "="*60)
    print("3. Summary:")
    print("   The line-specific grammar checker is designed to detect very specific patterns")
    print("   like the examples you provided. It may not catch all general grammar issues")
    print("   but excels at the targeted patterns it was designed for.")

if __name__ == "__main__":
    asyncio.run(test_with_docx())

