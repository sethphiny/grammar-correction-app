#!/usr/bin/env python3
"""
Test script to run the line-specific grammar checker on test.docx
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
from models.schemas import DocumentLine

async def test_with_docx():
    """Test the line-specific grammar checker with test.docx"""
    
    # Initialize the document parser and grammar checker
    parser = DocumentParser()
    grammar_checker = LineSpecificGrammarChecker()
    
    # Path to the test.docx file (assuming it's in the parent directory)
    test_docx_path = backend_dir.parent / "test.docx"
    
    if not test_docx_path.exists():
        print(f"Error: {test_docx_path} not found!")
        print("Available files in parent directory:")
        for file in backend_dir.parent.iterdir():
            if file.is_file():
                print(f"  - {file.name}")
        return
    
    print(f"=== Testing Line-Specific Grammar Checker with {test_docx_path.name} ===")
    print()
    
    try:
        # Parse the document
        print("1. Parsing document...")
        lines = await parser.parse_document(str(test_docx_path))
        print(f"   ✓ Parsed {len(lines)} lines from document")
        print()
        
        # Display the document content
        print("2. Document content:")
        print("-" * 60)
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            if line.content.strip():
                print(f"Line {line.line_number}: {line.content}")
                if line.sentences:
                    for j, sentence in enumerate(line.sentences):
                        if sentence.strip():
                            print(f"  Sentence {j+1}: {sentence}")
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
        print("-" * 60)
        print()
        
        # Run grammar checking on each line
        print("3. Running line-specific grammar checker...")
        total_issues = 0
        
        for line in lines:
            if line.content.strip():  # Only check non-empty lines
                issues = await grammar_checker.check_line_specific_issues(line)
                if issues:
                    total_issues += len(issues)
                    print(f"\n📝 Line {line.line_number}: {line.content}")
                    for issue in issues:
                        print(f"   🔍 Issue: {issue.problem}")
                        print(f"      Reason: {issue.reason}")
                        print(f"      Fix: {issue.fix}")
                        print(f"      Corrected: {issue.corrected_text}")
                        print()
        
        print(f"4. Summary:")
        print(f"   ✓ Processed {len(lines)} lines")
        print(f"   ✓ Found {total_issues} grammar issues")
        
        # Show a breakdown by issue type
        if total_issues > 0:
            print("\n5. Issue breakdown:")
            issue_types = {}
            for line in lines:
                if line.content.strip():
                    issues = await grammar_checker.check_line_specific_issues(line)
                    for issue in issues:
                        issue_type = issue.issue_type.value
                        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in issue_types.items():
                print(f"   - {issue_type.replace('_', ' ').title()}: {count} issues")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_docx())

