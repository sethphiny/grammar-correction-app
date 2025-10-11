#!/usr/bin/env python3
"""
Test LLM API connection and cost estimation
Run this script to verify your API keys are working correctly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_openai():
    """Test OpenAI API connection"""
    print("\n" + "="*60)
    print("🔍 Testing OpenAI API (GPT-4o-mini)")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Add it to your .env file:")
        print("   OPENAI_API_KEY=sk-proj-your-key-here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        from openai import AsyncOpenAI
        import tiktoken
        
        client = AsyncOpenAI(api_key=api_key)
        
        # Test simple API call
        print("\n📡 Sending test request...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say only the word 'connected'"}
            ],
            max_tokens=5
        )
        
        result = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        
        # Calculate cost
        input_cost = (prompt_tokens / 1_000_000) * 0.15
        output_cost = (completion_tokens / 1_000_000) * 0.60
        total_cost = input_cost + output_cost
        
        print(f"\n✅ Response: '{result}'")
        print(f"📊 Tokens: {tokens_used} (input: {prompt_tokens}, output: {completion_tokens})")
        print(f"💰 Cost: ${total_cost:.6f}")
        
        # Test a typical enhancement request
        print("\n📡 Testing typical grammar enhancement request...")
        test_prompt = """Fix this grammar issue:
Text: "The report was completed and then it was submitted to the manager."
Problem: Passive voice and redundancy
Provide a better version.

Return JSON: {"improved_fix": "...", "explanation": "..."}"""
        
        response2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        tokens_used2 = response2.usage.total_tokens
        cost2 = ((response2.usage.prompt_tokens / 1_000_000) * 0.15 + 
                 (response2.usage.completion_tokens / 1_000_000) * 0.60)
        
        print(f"✅ Enhancement test successful")
        print(f"📊 Tokens: {tokens_used2}")
        print(f"💰 Cost: ${cost2:.6f}")
        
        # Estimate costs for typical usage
        print("\n" + "="*60)
        print("💰 Cost Estimates for Your Use Case")
        print("="*60)
        print(f"Per enhancement: ~${cost2:.4f}")
        print(f"Per document (20 enhancements): ~${cost2*20:.4f}")
        print(f"Per 1MB doc (30 enhancements): ~${cost2*30:.4f}")
        print(f"100 docs/month: ~${cost2*20*100:.2f}")
        print(f"500 docs/month: ~${cost2*20*500:.2f}")
        
        return True
        
    except ImportError:
        print("❌ OpenAI package not installed")
        print("💡 Install with: pip install openai tiktoken")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check your API key is valid")
        print("   2. Verify you have credits/payment method")
        print("   3. Check internet connection")
        print("   4. Visit: https://platform.openai.com/account/api-keys")
        return False


async def test_google():
    """Test Google Gemini API connection"""
    print("\n" + "="*60)
    print("🔍 Testing Google Gemini API (Flash)")
    print("="*60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("💡 Add it to your .env file:")
        print("   GOOGLE_API_KEY=AIza-your-key-here")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("\n📡 Sending test request...")
        response = model.generate_content("Say only the word 'connected'")
        
        print(f"\n✅ Response: '{response.text}'")
        print(f"💰 Cost: ~$0.0001 (estimated)")
        
        print("\n💰 Cost Estimates:")
        print(f"Per enhancement: ~$0.0005")
        print(f"Per document (20 enhancements): ~$0.01")
        print(f"Per 1MB doc (30 enhancements): ~$0.015")
        
        return True
        
    except ImportError:
        print("❌ Google Generative AI package not installed")
        print("💡 Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def main():
    """Test configured LLM provider"""
    print("\n" + "🔹"*30)
    print("🧪 LLM API CONNECTION TEST")
    print("🔹"*30)
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    enabled = os.getenv("LLM_ENHANCEMENT_ENABLED", "false").lower() == "true"
    
    print(f"\n📍 Configured Provider: {provider.upper()}")
    print(f"📍 Enhancement Enabled: {enabled}")
    
    if not enabled:
        print("\n⚠️ LLM enhancement is DISABLED in .env")
        print("💡 To enable, add to .env:")
        print("   LLM_ENHANCEMENT_ENABLED=true")
        print("\nContinuing test anyway...\n")
    
    # Test based on provider
    results = {}
    
    if provider == "openai" or provider == "all":
        results["openai"] = await test_openai()
    
    if provider == "google" or provider == "all":
        results["google"] = await test_google()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    any_success = False
    for provider_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{provider_name.upper()}: {status}")
        if success:
            any_success = True
    
    print("\n" + "="*60)
    print("💡 NEXT STEPS")
    print("="*60)
    
    if any_success:
        print("✅ At least one provider is working!")
        print("✅ You can now enable LLM enhancement")
        print("\n📝 To enable in your app:")
        print("   1. Edit .env file")
        print("   2. Set: LLM_ENHANCEMENT_ENABLED=true")
        print("   3. Restart your backend server")
        print("   4. Enable 'AI-Enhanced Suggestions' in frontend")
        print("\n📊 Monitor costs at:")
        print("   - OpenAI: https://platform.openai.com/usage")
        print("   - Google: https://console.cloud.google.com/billing")
    else:
        print("❌ No providers are working")
        print("\n🔧 Troubleshooting:")
        print("   1. Check API keys in .env file")
        print("   2. Verify payment method is set up")
        print("   3. Check you have credits/budget")
        print("   4. Review: docs/API_KEYS_SETUP_GUIDE.md")
        print("\n📖 Get API keys:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("   - Google: https://makersuite.google.com/app/apikey")
    
    print("\n")
    return any_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
