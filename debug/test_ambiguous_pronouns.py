#!/usr/bin/env python3
"""
Test script for ambiguous_pronouns category implementation
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.grammar_checker import GrammarChecker
from models.schemas import DocumentData, DocumentLine

# Test cases for ambiguous pronouns
test_cases = [
    # Should be flagged (ambiguous)
    ("It seems like a good idea.", "Vague 'it'"),
    ("It appears that we should go.", "Vague 'it'"),
    ("The book was on the table and it was moved.", "Simple - OK"),  # Actually has clear referent
    ("When I looked at the car, it had a dent, and it was rusty, and it smelled bad.", "Multiple 'it'"),
    ("This is important.", "Vague 'this'"),
    ("That would be nice.", "Vague 'that'"),
    ("These are the issues.", "Vague 'these'"),
    ("Those could work.", "Vague 'those'"),
    ("They say it's going to rain.", "Ambiguous 'they'"),
    ("One must do what one can, but one should not overdo it when one is tired.", "Multiple 'one'"),
    ("He bought a car and a bike, which was expensive.", "Ambiguous 'which'"),
    
    # Should NOT be flagged (clear reference or idiomatic)
    ("It is raining today.", "Weather - idiomatic"),
    ("It is 5 o'clock.", "Time - idiomatic"),
    ("The solution is clear.", "No pronoun issue"),
    ("She went to the store.", "Clear pronoun"),
    ("The report shows that sales increased.", "No vague pronoun"),
    ("This approach is better.", "'This' + noun - clear"),
    ("That method works well.", "'That' + noun - clear"),
]

async def test_ambiguous_pronouns():
    print("=" * 70)
    print("TESTING AMBIGUOUS_PRONOUNS CATEGORY")
    print("=" * 70)
    
    checker = GrammarChecker()
    
    # Check if ambiguous_pronoun_patterns exist
    print(f"\n✓ Ambiguous pronoun patterns loaded: {len(checker.ambiguous_pronoun_patterns)} patterns")
    
    # Test each case
    for i, (test_text, description) in enumerate(test_cases, 1):
        # Create a simple document
        doc = DocumentData(
            filename="test.txt",
            lines=[DocumentLine(line_number=1, content=test_text, sentences=[])],
            total_lines=1,
            total_sentences=1
        )
        
        # Check with only ambiguous_pronouns category enabled
        issues, _ = await checker.check_document(
            doc, 
            enabled_categories=['ambiguous_pronouns']
        )
        
        status = "🟡 FLAGGED" if issues else "✅ OK"
        print(f"\n{i}. {status} - {description}")
        print(f"   Text: {test_text}")
        
        if issues:
            for issue in issues:
                print(f"   Issue: {issue.problem}")
                print(f"   Fix: {issue.fix}")
                print(f"   Confidence: {issue.confidence}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNote: Ambiguous pronoun detection is conservative and")
    print("flags potential issues for manual review. Some false positives")
    print("are expected due to the subjective nature of pronoun clarity.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ambiguous_pronouns())

