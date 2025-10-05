#!/usr/bin/env python3
"""
Test script to verify LanguageTool 2.9.4 compatibility
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_languagetool_import():
    """Test LanguageTool import"""
    try:
        from language_tool_python import LanguageTool
        print("✅ LanguageTool import successful")
        return True
    except ImportError as e:
        print(f"❌ LanguageTool import failed: {e}")
        return False

def test_languagetool_local():
    """Test local LanguageTool functionality"""
    try:
        from language_tool_python import LanguageTool
        tool = LanguageTool('en-US')
        
        # Test with a simple grammar error
        test_text = "This is a test sentance with some grammer errors."
        matches = tool.check(test_text)
        
        print(f"✅ Local LanguageTool working: {len(matches)} matches found")
        for match in matches:
            print(f"   - {match.message}: '{match.context}'")
        
        return True
    except Exception as e:
        print(f"❌ Local LanguageTool error: {e}")
        return False

def test_languagetool_remote():
    """Test remote LanguageTool functionality"""
    try:
        from language_tool_python import LanguageTool
        tool = LanguageTool('en-US', remote_server='http://localhost:8081')
        
        # Test with a simple grammar error
        test_text = "This is a test sentance with some grammer errors."
        matches = tool.check(test_text)
        
        print(f"✅ Remote LanguageTool working: {len(matches)} matches found")
        for match in matches:
            print(f"   - {match.message}: '{match.context}'")
        
        return True
    except Exception as e:
        print(f"❌ Remote LanguageTool error: {e}")
        return False

def test_hybrid_grammar_checker():
    """Test our hybrid grammar checker implementation"""
    try:
        from services.hybrid_grammar_checker import HybridGrammarChecker
        from models.schemas import DocumentData, DocumentLine
        
        checker = HybridGrammarChecker()
        
        # Create test document data
        test_line = DocumentLine(
            line_number=1,
            content="This is a test sentance with grammer errors.",
            sentences=["This is a test sentance with grammer errors."]
        )
        
        document_data = DocumentData(
            filename="test.docx",
            lines=[test_line],
            total_lines=1,
            total_sentences=1
        )
        
        print("✅ HybridGrammarChecker import and initialization successful")
        return True
    except Exception as e:
        print(f"❌ HybridGrammarChecker error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing LanguageTool 2.9.4 Compatibility")
    print("=" * 50)
    
    tests = [
        ("LanguageTool Import", test_languagetool_import),
        ("Local LanguageTool", test_languagetool_local),
        ("Remote LanguageTool", test_languagetool_remote),
        ("Hybrid Grammar Checker", test_hybrid_grammar_checker),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! LanguageTool 2.9.4 is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
