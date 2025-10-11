# API Keys Setup Guide
## How to Get API Keys for LLM Enhancement

**Last Updated:** January 2024

---

## 🔑 OpenAI API Key (Recommended)

### Step 1: Create OpenAI Account

1. **Visit:** https://platform.openai.com/signup
2. **Sign up** with your email or Google/Microsoft account
3. **Verify** your email address
4. **Complete** account setup

### Step 2: Add Payment Method

1. **Go to:** https://platform.openai.com/account/billing
2. Click **"Add payment method"**
3. Enter credit card details
4. **Set budget limits** (recommended: $100/month to start)
5. **Enable automatic recharge** or **set hard limits**

### Step 3: Generate API Key

1. **Go to:** https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. **Name it:** "Grammar Checker App" (for tracking)
4. **Copy the key** - It starts with `sk-proj-...`
5. **⚠️ IMPORTANT:** Save it immediately - you won't see it again!

### Step 4: Configure in Your App

```bash
# In your project root, edit .env file
OPENAI_API_KEY=sk-proj-your-key-here-xxxxxxxxxxxxx
LLM_ENHANCEMENT_ENABLED=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Step 5: Test Connection

```bash
cd backend
source venv/bin/activate
python3 test_llm_connection.py
```

Expected output:
```
✅ Connection successful: connected
📊 Test cost: $0.0001
```

### Pricing & Limits

```yaml
Model: GPT-4o-mini
Input: $0.15 per 1M tokens
Output: $0.60 per 1M tokens
Rate Limits: 
  - 10,000 requests per minute
  - 2M tokens per minute
  - More than enough for typical use

Expected Usage:
  - 100 documents/month: ~$2-3
  - 500 documents/month: ~$10-15
  - 2,000 documents/month: ~$40-60
```

### Budget Settings (Recommended)

```yaml
Free Trial: $5 credit (expires after 3 months)
Starter: $10/month limit
Professional: $100/month limit
Enterprise: $500-1000/month limit

Set in: https://platform.openai.com/account/limits
```

---

## 🔑 Google Gemini API Key (Budget Option)

### Step 1: Get API Key

1. **Visit:** https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. Click **"Get API Key"**
4. Choose **"Create API key in new project"** or select existing project
5. **Copy the key** - It starts with `AIza...`

### Step 2: Enable Billing (for production)

1. **Go to:** https://console.cloud.google.com/billing
2. **Link** a billing account
3. **Enable** Generative Language API
4. **Set budget alerts** at $50, $100, $200

### Step 3: Configure in Your App

```bash
# In your project root, edit .env file
GOOGLE_API_KEY=AIza-your-key-here-xxxxxxxxxxxxx
LLM_ENHANCEMENT_ENABLED=true
LLM_PROVIDER=google
LLM_MODEL=gemini-1.5-flash
```

### Pricing & Limits

```yaml
Model: Gemini 1.5 Flash
Input: $0.075 per 1M tokens (CHEAPEST)
Output: $0.30 per 1M tokens
Rate Limits:
  - 1,500 requests per minute
  - 4M tokens per minute

Expected Usage:
  - 100 documents/month: ~$1-2
  - 500 documents/month: ~$5-10
  - 2,000 documents/month: ~$20-40
```

### Free Tier

```
Gemini API Free Tier:
- 15 requests per minute
- 1M tokens per minute
- 1,500 requests per day
- Good for testing and low-volume use
```

---

## 🔑 Anthropic Claude API Key (Premium Option)

### Step 1: Join Waitlist or Request Access

1. **Visit:** https://console.anthropic.com/
2. **Sign up** with your email
3. **Request API access** (may require business verification)
4. **Wait for approval** (usually 1-3 days)

### Step 2: Add Payment Method

1. **Go to:** https://console.anthropic.com/account/billing
2. **Add payment method**
3. **Set budget limits**
4. **Enable usage alerts**

### Step 3: Generate API Key

1. **Go to:** https://console.anthropic.com/account/keys
2. Click **"Create Key"**
3. **Name it:** "Grammar Checker"
4. **Copy the key** - It starts with `sk-ant-...`
5. **Save immediately** - can't view again

### Step 4: Configure in Your App

```bash
# In your project root, edit .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here-xxxxxxxxxxxxx
LLM_ENHANCEMENT_ENABLED=true
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
```

### Pricing & Limits

```yaml
Model: Claude 3.5 Sonnet
Input: $3.00 per 1M tokens (HIGHEST QUALITY)
Output: $15.00 per 1M tokens
Rate Limits:
  - Varies by tier (contact sales for details)

Expected Usage:
  - 100 documents/month: ~$15-25
  - 500 documents/month: ~$75-125
  - Best for premium/enterprise tier

Model: Claude 3 Haiku (faster/cheaper)
Input: $0.25 per 1M tokens
Output: $1.25 per 1M tokens
```

---

## 🔒 Security Best Practices

### 1. Environment Variables (REQUIRED)

**❌ NEVER do this:**
```python
api_key = "sk-proj-abc123"  # Hard-coded in code
```

**✅ ALWAYS do this:**
```python
api_key = os.getenv("OPENAI_API_KEY")  # From environment
```

### 2. .env File Setup

```bash
# .env (DO NOT COMMIT TO GIT)
OPENAI_API_KEY=sk-proj-your-actual-key-here
GOOGLE_API_KEY=AIza-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Security
LLM_ENHANCEMENT_ENABLED=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Cost Controls
LLM_MAX_COST_PER_DOCUMENT=0.50
DAILY_LLM_COST_LIMIT=100.0
MONTHLY_LLM_COST_LIMIT=1000.0

# Cache (optional but recommended)
REDIS_URL=redis://localhost:6379
```

### 3. .gitignore Check

```bash
# Make sure .env is in .gitignore
cat .gitignore | grep ".env"

# If not there, add it:
echo ".env" >> .gitignore
```

### 4. Production Deployment

```yaml
Docker Secrets: Use Docker secrets for production
Kubernetes: Use Kubernetes secrets
Environment: Set via hosting platform (Railway, Heroku, AWS)
Rotation: Rotate keys every 90 days
```

### 5. Key Permissions

**OpenAI:**
- Enable: "Model capabilities" 
- Enable: "API access"
- Disable: "File uploads" (not needed)
- Disable: "Fine-tuning" (not needed)

**Set at:** https://platform.openai.com/account/api-keys

---

## 💳 Billing Setup & Alerts

### OpenAI Budget Alerts

1. **Go to:** https://platform.openai.com/account/limits
2. **Set soft limit:** $50/month (warning only)
3. **Set hard limit:** $100/month (stops processing)
4. **Email alerts:** Enable at 50%, 80%, 100%

### Cost Monitoring

```python
# Add to your .env
COST_ALERT_EMAIL=admin@yourdomain.com
COST_ALERT_THRESHOLD_PERCENTAGE=80

# System will email when:
# - Daily budget reaches 80%
# - Monthly budget reaches 80%
# - Unusual spending spike detected
```

---

## 🧪 Testing Your API Keys

### Test Script

Create this file: `backend/test_llm_connection.py`

```python
#!/usr/bin/env python3
"""
Test LLM API connection and estimate costs
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai():
    """Test OpenAI connection"""
    print("\n🔍 Testing OpenAI API...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        
        # Test API call
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'connected'"}],
            max_tokens=5
        )
        
        result = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Calculate cost
        cost = (response.usage.prompt_tokens * 0.15 + response.usage.completion_tokens * 0.60) / 1_000_000
        
        print(f"✅ Connection successful: '{result}'")
        print(f"📊 Tokens used: {tokens_used}")
        print(f"💰 Cost: ${cost:.6f}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_google():
    """Test Google Gemini connection"""
    print("\n🔍 Testing Google Gemini API...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:6]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'connected'")
        
        print(f"✅ Connection successful: '{response.text}'")
        print(f"💰 Cost: ~$0.0001 (estimated)")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_anthropic():
    """Test Anthropic Claude connection"""
    print("\n🔍 Testing Anthropic Claude API...")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:7]}...{api_key[-4:]}")
    
    try:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=api_key)
        
        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'connected'"}]
        )
        
        result = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        
        print(f"✅ Connection successful: '{result}'")
        print(f"📊 Tokens used: {tokens_used}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    """Test all configured providers"""
    print("=" * 60)
    print("🧪 LLM API Connection Test")
    print("=" * 60)
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    print(f"\n📍 Configured provider: {provider}")
    
    results = {}
    
    # Test based on provider
    if provider == "openai":
        results["openai"] = await test_openai()
    elif provider == "google":
        results["google"] = await test_google()
    elif provider == "anthropic":
        results["anthropic"] = await test_anthropic()
    else:
        # Test all available
        results["openai"] = await test_openai()
        results["google"] = await test_google()
        results["anthropic"] = await test_anthropic()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for provider_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{provider_name.upper()}: {status}")
    
    print("\n💡 Next Steps:")
    if any(results.values()):
        print("✅ At least one provider is working!")
        print("✅ You can now enable LLM enhancement")
        print("\n📝 To enable, set in .env:")
        print("   LLM_ENHANCEMENT_ENABLED=true")
    else:
        print("❌ No providers are working")
        print("📖 Check API keys in .env file")
        print("📖 Review this guide: docs/API_KEYS_SETUP_GUIDE.md")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💰 Billing Setup

### OpenAI Billing Configuration

#### Recommended Budget Settings

**For Testing:**
```
Hard Limit: $10
Soft Limit: $5
Email Alert: 80% ($8)
```

**For Small Scale (100-500 docs/month):**
```
Hard Limit: $50
Soft Limit: $25
Email Alert: 80% ($40)
```

**For Medium Scale (500-2000 docs/month):**
```
Hard Limit: $200
Soft Limit: $100
Email Alert: 80% ($160)
```

**For Large Scale (2000+ docs/month):**
```
Hard Limit: $1000
Soft Limit: $500
Email Alert: 80% ($800)
```

#### How to Set Limits

1. **Go to:** https://platform.openai.com/account/limits
2. **Monthly budget:** Set based on scale above
3. **Email notifications:** Enable at 50%, 80%, 100%
4. **Auto top-up:** Enable or disable based on preference
5. **Payment method:** Ensure valid card on file

---

## 🔐 Security Checklist

### Before Going Live

- [ ] API keys stored in environment variables (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] Budget limits configured
- [ ] Email alerts enabled
- [ ] Test script run successfully
- [ ] Keys have descriptive names (for tracking)
- [ ] Backup email address added for alerts
- [ ] Production keys separate from development keys

### Production Security

```yaml
Development:
  - Separate API key for dev/staging
  - Lower budget limits ($10-50)
  - Test on small documents only

Production:
  - Separate API key for production
  - Higher limits based on usage
  - Monitoring and alerts enabled
  - Key rotation every 90 days
```

---

## 🚨 Troubleshooting

### Common Issues

#### "Invalid API Key"
```
Problem: API key not recognized
Solutions:
  1. Check key is copied correctly (no extra spaces)
  2. Verify key starts with correct prefix:
     - OpenAI: sk-proj-...
     - Google: AIza...
     - Anthropic: sk-ant-...
  3. Check key hasn't been revoked
  4. Regenerate key if needed
```

#### "Rate Limit Exceeded"
```
Problem: Too many requests
Solutions:
  1. Check rate limits in dashboard
  2. Implement request throttling
  3. Use batch processing (10-20 issues)
  4. Contact provider for limit increase
```

#### "Insufficient Credits"
```
Problem: No money in account
Solutions:
  1. Add payment method
  2. Top up account
  3. Check billing status
  4. Enable auto-recharge
```

#### "Connection Timeout"
```
Problem: API not responding
Solutions:
  1. Check internet connection
  2. Verify API endpoint URL
  3. Check provider status page
  4. Increase timeout setting (30-60s)
```

### Testing Checklist

```bash
# 1. Environment variables loaded?
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"

# 2. Dependencies installed?
pip list | grep openai

# 3. API connection works?
python3 backend/test_llm_connection.py

# 4. Cost estimation working?
python3 backend/test_cost_estimation.py
```

---

## 📧 Email Notifications Setup

### OpenAI Email Alerts

Configure at: https://platform.openai.com/account/limits

```yaml
Billing Alerts:
  - 50% of budget: Warning email
  - 80% of budget: Urgent email
  - 100% of budget: Critical email + auto-stop

Usage Reports:
  - Weekly summary: Every Monday
  - Monthly report: 1st of month
  - Spike detection: Real-time
```

### Custom Application Alerts

```python
# In your app - send email when costs exceed threshold
import smtplib
from email.mime.text import MIMEText

def send_cost_alert(amount: float, limit: float):
    """Send email when cost threshold reached"""
    msg = MIMEText(f"""
    ⚠️ LLM Cost Alert
    
    Current spending: ${amount:.2f}
    Budget limit: ${limit:.2f}
    Percentage: {(amount/limit)*100:.1f}%
    
    Action: Review usage in admin dashboard
    """)
    
    msg['Subject'] = '⚠️ LLM Budget Alert'
    msg['From'] = 'noreply@yourdomain.com'
    msg['To'] = os.getenv('COST_ALERT_EMAIL')
    
    # Send via SMTP
    # ... (configure your email service)
```

---

## 📊 Cost Monitoring Dashboard

### Setup Admin Dashboard

```python
# backend/routes/admin.py

@app.get("/admin/llm-costs")
async def get_llm_costs(admin_key: str):
    """Get current LLM usage and costs"""
    
    if admin_key != os.getenv("ADMIN_SECRET_KEY"):
        raise HTTPException(403, "Unauthorized")
    
    return {
        "today": {
            "cost": cost_controller.get_daily_cost(),
            "documents": cost_controller.get_daily_docs(),
            "limit": cost_controller.daily_limit
        },
        "month": {
            "cost": cost_controller.get_monthly_cost(),
            "documents": cost_controller.get_monthly_docs(),
            "limit": cost_controller.monthly_limit
        },
        "averages": {
            "cost_per_document": cost_controller.get_avg_cost_per_doc(),
            "cost_per_mb": cost_controller.get_avg_cost_per_mb()
        }
    }
```

---

## 🎓 Getting Started Checklist

### Complete Setup (15 minutes)

- [ ] **Step 1:** Choose provider (OpenAI recommended)
- [ ] **Step 2:** Create account on provider's platform
- [ ] **Step 3:** Add payment method
- [ ] **Step 4:** Generate API key
- [ ] **Step 5:** Copy key to `.env` file
- [ ] **Step 6:** Set budget limits on provider platform
- [ ] **Step 7:** Enable email alerts
- [ ] **Step 8:** Run test script to verify
- [ ] **Step 9:** Configure app-level budget limits
- [ ] **Step 10:** Review security checklist
- [ ] **Step 11:** Test with sample document
- [ ] **Step 12:** Monitor costs for first week

---

## 🆘 Support Resources

### Official Documentation

- **OpenAI:** https://platform.openai.com/docs
- **Google AI:** https://ai.google.dev/docs
- **Anthropic:** https://docs.anthropic.com

### Status Pages

- **OpenAI Status:** https://status.openai.com
- **Google Cloud Status:** https://status.cloud.google.com
- **Anthropic Status:** https://status.anthropic.com

### Community Support

- **OpenAI Forum:** https://community.openai.com
- **Stack Overflow:** Tag: `openai-api`, `gemini-api`
- **Discord:** OpenAI Developer Discord

---

## ⚡ Quick Reference

### API Key Prefixes

```
OpenAI:     sk-proj-xxxxx...
Google:     AIza-xxxxx...
Anthropic:  sk-ant-xxxxx...
```

### Cost Per MB (Quick Lookup)

```
GPT-4o-mini:      $0.01-0.03/MB  ⭐ RECOMMENDED
Gemini Flash:     $0.01-0.02/MB  💰 CHEAPEST
Claude Sonnet:    $0.15-0.25/MB  👑 BEST QUALITY
```

### Rate Limits

```
OpenAI:     10,000 RPM  ✅ High
Google:     1,500 RPM   ⚠️ Medium
Anthropic:  Varies      ⚠️ Contact sales
```

---

**Need Help?** 
- Review full implementation guide: `docs/LLM_IMPLEMENTATION_GUIDE.md`
- Check cost estimates: `docs/LLM_COST_REFERENCE.md`
- Open an issue in the project repository

---

**Last Updated:** January 2024  
**Next Review:** When provider pricing changes
