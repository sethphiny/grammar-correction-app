#!/usr/bin/env python3
"""
Test script for agreement category implementation
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.grammar_checker import GrammarChecker
from models.schemas import DocumentData, DocumentLine

# Test cases for agreement
test_cases = [
    # Should be caught
    "They is going to the store.",           # they is -> they are
    "He don't like it.",                     # he don't -> he doesn't
    "She have a book.",                      # she have -> she has
    "We was there yesterday.",               # we was -> we were
    "I is happy.",                           # I is -> I am
    "It are broken.",                        # it are -> it is
    "There is many people.",                 # there is many -> there are many
    "He walk to school every day.",          # he walk to -> he walks to
    "People is coming.",                     # people is -> people are
    
    # Should NOT be caught (correct grammar)
    "They are going to the store.",
    "He doesn't like it.",
    "She has a book.",
    "We were there yesterday.",
    "I am happy.",
    "He walks to school every day.",
    
    # Should NOT be caught (complex cases to avoid false positives)
    "Would it feel good?",                   # Modal - correct
    "Did it go well?",                       # Auxiliary - correct
    "Let him go.",                           # Causative - correct
]

async def test_agreement():
    print("=" * 70)
    print("TESTING AGREEMENT CATEGORY")
    print("=" * 70)
    
    checker = GrammarChecker()
    
    # Check if agreement patterns exist
    print(f"\n✓ Agreement patterns loaded: {len(checker.agreement_patterns)} patterns")
    
    # Test each case
    for i, test_text in enumerate(test_cases, 1):
        # Create a simple document
        doc = DocumentData(
            filename="test.txt",
            lines=[DocumentLine(line_number=1, content=test_text, sentences=[])],
            total_lines=1,
            total_sentences=1
        )
        
        # Check with only agreement category enabled
        issues, _ = await checker.check_document(
            doc, 
            enabled_categories=['agreement']
        )
        
        status = "🔴 ERROR FOUND" if issues else "✅ OK"
        print(f"\n{i}. {status}")
        print(f"   Text: {test_text}")
        
        if issues:
            for issue in issues:
                print(f"   Issue: {issue.problem}")
                print(f"   Fix: {issue.fix}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agreement())

