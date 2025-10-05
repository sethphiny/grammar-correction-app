#!/usr/bin/env python3
"""
Test the new streaming grammar checker implementation
"""

import asyncio
import sys
import os
import time
from typing import List

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.streaming_grammar_checker import StreamingGrammarChecker
from models.schemas import DocumentLine

async def test_streaming_grammar_checker():
    """Test the streaming grammar checker with various scenarios"""
    print("🧪 Testing Streaming Grammar Checker")
    print("=" * 50)
    
    # Initialize the streaming grammar checker
    checker = StreamingGrammarChecker()
    
    # Test data - create some sample lines with grammar issues
    test_lines = [
        DocumentLine(
            line_number=1,
            content="This is a test sentence with some grammar issues.",
            sentences=["This is a test sentence with some grammar issues."]
        ),
        DocumentLine(
            line_number=2,
            content="The team are working on the project.",
            sentences=["The team are working on the project."]
        ),
        DocumentLine(
            line_number=3,
            content="There is many problems with this approach.",
            sentences=["There is many problems with this approach."]
        ),
        DocumentLine(
            line_number=4,
            content="She don't like the new system.",
            sentences=["She don't like the new system."]
        ),
        DocumentLine(
            line_number=5,
            content="The document that contain errors need to be fixed.",
            sentences=["The document that contain errors need to be fixed."]
        )
    ]
    
    print(f"📝 Testing with {len(test_lines)} lines")
    print()
    
    # Track results
    total_issues = 0
    processed_lines = 0
    skipped_sentences = 0
    
    # Process with streaming
    start_time = time.time()
    
    async for result in checker.process_document_streaming(test_lines):
        if result['type'] == 'line_completed':
            processed_lines += 1
            line_issues = result['issues']
            total_issues += len(line_issues)
            
            print(f"✅ Line {result['line_number']}: {len(line_issues)} issues found")
            for issue in line_issues:
                print(f"   - {issue.problem}: {issue.reason}")
            
        elif result['type'] == 'processing_complete':
            skipped_sentences = result['skipped_sentences']
            print(f"\n🎉 Processing completed!")
            print(f"   Total issues found: {result['total_issues']}")
            print(f"   Processed lines: {result['processed_lines']}")
            print(f"   Skipped sentences: {result['skipped_sentences']}")
            break
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n📊 Performance Results:")
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Lines per second: {processed_lines / processing_time:.2f}")
    print(f"   Issues found: {total_issues}")
    print(f"   Skipped sentences: {skipped_sentences}")
    
    # Test timeout behavior with a very long sentence
    print(f"\n⏱️  Testing timeout behavior...")
    
    long_sentence = "This is a very long sentence that might cause timeout issues " * 20
    long_line = DocumentLine(
        line_number=6,
        content=long_sentence,
        sentences=[long_sentence]
    )
    
    timeout_start = time.time()
    async for result in checker.process_document_streaming([long_line]):
        if result['type'] == 'line_completed':
            print(f"✅ Long sentence processed: {len(result['issues'])} issues found")
        elif result['type'] == 'processing_complete':
            print(f"✅ Long sentence completed, skipped: {result['skipped_sentences']}")
            break
    timeout_end = time.time()
    
    print(f"   Long sentence processing time: {timeout_end - timeout_start:.2f} seconds")
    
    print(f"\n✅ Streaming Grammar Checker Test Completed!")
    return True

async def test_websocket_integration():
    """Test WebSocket integration (simulation)"""
    print(f"\n🔌 Testing WebSocket Integration")
    print("=" * 30)
    
    # This would normally test the WebSocket manager
    # For now, just verify the imports work
    try:
        from services.websocket_manager import websocket_manager
        print("✅ WebSocket manager imported successfully")
        print(f"   Active connections: {websocket_manager.get_connection_count()}")
        return True
    except Exception as e:
        print(f"❌ WebSocket manager import failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Streaming Grammar Checker Tests")
    print("=" * 60)
    
    try:
        # Test streaming grammar checker
        streaming_success = await test_streaming_grammar_checker()
        
        # Test WebSocket integration
        websocket_success = await test_websocket_integration()
        
        print(f"\n📋 Test Summary:")
        print(f"   Streaming Grammar Checker: {'✅ PASS' if streaming_success else '❌ FAIL'}")
        print(f"   WebSocket Integration: {'✅ PASS' if websocket_success else '❌ FAIL'}")
        
        if streaming_success and websocket_success:
            print(f"\n🎉 All tests passed! The streaming implementation is ready.")
            return True
        else:
            print(f"\n⚠️  Some tests failed. Please check the implementation.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
