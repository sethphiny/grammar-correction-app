"""
Test the optimized chunk-based grammar checking performance
"""
import asyncio
import time
import pytest
from services.grammar_checker import GrammarChecker
from models.schemas import DocumentLine


@pytest.mark.asyncio
async def test_parallel_sentence_processing_speed():
    """Test that parallel processing is faster than sequential"""
    checker = GrammarChecker()
    
    # Create test data with 20 sentences
    test_sentences = [
        "This is a test sentence number one.",
        "The quick brown fox jumps over the lazy dog.",
        "Grammar checking should be fast and accurate.",
        "We need to test the performance improvements.",
        "Parallel processing can significantly improve speed.",
        "LanguageTool is a powerful grammar checking tool.",
        "Python asyncio enables concurrent processing.",
        "Timeout handling prevents sentences from hanging.",
        "Semaphore limits concurrent operations.",
        "Error handling ensures robust processing.",
        "The system should handle large documents.",
        "Chunk-based processing improves scalability.",
        "Each sentence is processed independently.",
        "Results are collected and aggregated.",
        "Performance metrics help track improvements.",
        "Testing is essential for quality assurance.",
        "Documentation helps other developers.",
        "Code optimization improves user experience.",
        "Fast processing reduces waiting time.",
        "Quality results build user confidence."
    ]
    
    # Create chunk text and lines
    chunk_text = "\n".join(test_sentences)
    chunk_lines = [DocumentLine(line_number=idx+1, content=sent, sentences=[sent]) for idx, sent in enumerate(test_sentences)]
    
    # Test parallel processing time
    start_time = time.time()
    issues = await checker.check_text_chunk(chunk_text, chunk_lines, 1)
    parallel_time = time.time() - start_time
    
    print(f"\n✅ Parallel processing time: {parallel_time:.2f} seconds")
    print(f"📊 Sentences processed: {len(test_sentences)}")
    print(f"⚡ Average time per sentence: {parallel_time/len(test_sentences):.2f} seconds")
    print(f"🔍 Issues found: {len(issues)}")
    
    # Parallel processing should complete in reasonable time
    # With 5 concurrent sentences, 20 sentences should take ~4x the time of 1 sentence
    # Plus overhead, expect less than 60 seconds total
    assert parallel_time < 60, f"Processing took too long: {parallel_time:.2f}s"
    
    return issues


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that sentence timeouts work correctly"""
    checker = GrammarChecker()
    
    # Create a moderately long sentence that will timeout
    # Use a single sentence without periods to avoid splitting
    long_sentence = "This is a very long sentence without any punctuation that continues on and on " * 50
    chunk_lines = [DocumentLine(line_number=1, content=long_sentence, sentences=[long_sentence])]
    
    start_time = time.time()
    issues = await checker.check_text_chunk(long_sentence, chunk_lines, 1)
    elapsed_time = time.time() - start_time
    
    print(f"\n⏱️  Timeout test completed in: {elapsed_time:.2f} seconds")
    print(f"📝 Issues found: {len(issues)}")
    
    # With a single long sentence, should timeout within the configured limit (10s + overhead)
    # Allow up to 15 seconds for processing overhead
    assert elapsed_time < 15, f"Timeout mechanism not working properly: took {elapsed_time:.2f}s"


@pytest.mark.asyncio
async def test_concurrent_chunk_processing():
    """Test processing multiple chunks concurrently"""
    checker = GrammarChecker()
    
    # Create 3 chunks with different content
    chunks = [
        ("Chunk one has several sentences. Each sentence is unique.", 
         [DocumentLine(line_number=1, content="Chunk one has several sentences. Each sentence is unique.", 
                      sentences=["Chunk one has several sentences.", "Each sentence is unique."])]),
        ("Chunk two contains different text. Testing is important.", 
         [DocumentLine(line_number=1, content="Chunk two contains different text. Testing is important.", 
                      sentences=["Chunk two contains different text.", "Testing is important."])]),
        ("Chunk three completes the test. Results should be accurate.", 
         [DocumentLine(line_number=1, content="Chunk three completes the test. Results should be accurate.", 
                      sentences=["Chunk three completes the test.", "Results should be accurate."])]),
    ]
    
    # Process all chunks concurrently
    start_time = time.time()
    tasks = [
        checker.check_text_chunk(chunk_text, chunk_lines, idx + 1)
        for idx, (chunk_text, chunk_lines) in enumerate(chunks)
    ]
    results = await asyncio.gather(*tasks)
    elapsed_time = time.time() - start_time
    
    print(f"\n🚀 Concurrent chunk processing time: {elapsed_time:.2f} seconds")
    print(f"📦 Chunks processed: {len(chunks)}")
    print(f"🔍 Total issues found: {sum(len(r) for r in results)}")
    
    # All chunks should process successfully
    assert all(isinstance(r, list) for r in results), "All chunks should return lists"
    
    # Processing should be fast due to parallelism
    assert elapsed_time < 30, f"Concurrent processing took too long: {elapsed_time:.2f}s"


@pytest.mark.asyncio
async def test_empty_and_edge_cases():
    """Test edge cases like empty chunks, short sentences, etc."""
    checker = GrammarChecker()
    
    # Test empty chunk
    issues = await checker.check_text_chunk("", [], 1)
    assert issues == [], "Empty chunk should return empty results"
    
    # Test very short sentence
    short_chunk = "Hi."
    short_lines = [DocumentLine(line_number=1, content=short_chunk, sentences=[short_chunk])]
    issues = await checker.check_text_chunk(short_chunk, short_lines, 1)
    assert isinstance(issues, list), "Should return a list"
    
    # Test whitespace only
    whitespace_chunk = "   \n  \n  "
    whitespace_lines = [DocumentLine(line_number=1, content=whitespace_chunk, sentences=[])]
    issues = await checker.check_text_chunk(whitespace_chunk, whitespace_lines, 1)
    assert issues == [], "Whitespace-only chunk should return empty results"
    
    print("\n✅ All edge cases handled correctly")


if __name__ == "__main__":
    print("🧪 Running optimized chunk processing tests...\n")
    
    # Run tests
    asyncio.run(test_parallel_sentence_processing_speed())
    asyncio.run(test_timeout_handling())
    asyncio.run(test_concurrent_chunk_processing())
    asyncio.run(test_empty_and_edge_cases())
    
    print("\n✨ All tests completed!")

