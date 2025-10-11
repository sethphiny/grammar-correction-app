# Quick Start: Enable AI-Enhanced Grammar Corrections

**Estimated Setup Time:** 15 minutes  
**Cost:** ~$0.01-0.03 per MB  
**Provider:** OpenAI GPT-4o-mini (Recommended)

---

## ⚡ 5-Minute Setup

### Step 1: Get OpenAI API Key (5 min)

1. Go to https://platform.openai.com/signup
2. Sign up or log in
3. Add payment method: https://platform.openai.com/account/billing
4. Create API key: https://platform.openai.com/api-keys
5. Copy the key (starts with `sk-proj-...`)

### Step 2: Install Dependencies (2 min)

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python3 -m pip install openai tiktoken
```

### Step 3: Configure Environment (3 min)

```bash
# Copy example environment file if you haven't already
cp env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

Add these lines to `.env`:

```bash
# Enable LLM Enhancement
LLM_ENHANCEMENT_ENABLED=true
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Cost Controls
LLM_MAX_COST_PER_DOCUMENT=0.50
DAILY_LLM_COST_LIMIT=100.0
MONTHLY_LLM_COST_LIMIT=1000.0
```

### Step 4: Test Connection (2 min)

```bash
cd backend
python3 test_llm_connection.py
```

Expected output:
```
✅ Connection successful: 'connected'
💰 Cost: $0.000060
```

### Step 5: Restart Backend (1 min)

```bash
# Stop current backend (Ctrl+C)
# Start again
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ [LLMEnhancer] Initialized with gpt-4o-mini
```

### Step 6: Use in Frontend

1. Upload a document
2. Check the **"✨ AI-Enhanced Suggestions"** checkbox
3. Click Analyze
4. Get better corrections!

---

## 💰 What to Expect

### Costs
- **Per document (1MB):** $0.01-0.03
- **100 docs/month:** ~$2-3
- **500 docs/month:** ~$10-15

### Performance
- **Extra processing time:** +3-5 seconds
- **Quality improvement:** +40-50% on complex issues
- **Issues enhanced:** ~20-30% of total (only complex ones)

### What Gets Enhanced
- ✅ Awkward phrasing (confidence < 85%)
- ✅ Tense consistency issues
- ✅ Parallelism/concision issues
- ✅ Dialogue formatting (complex cases)
- ❌ Simple pattern matches (already good)
- ❌ High confidence issues (> 85%)

---

## 🔒 Security Checklist

Before going live:

- [ ] API key in `.env` file (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] Budget limits set on OpenAI platform
- [ ] Email alerts enabled
- [ ] Test script passed
- [ ] Local `.env` NOT committed to git

---

## 📊 Monitoring

### Check Costs

**OpenAI Dashboard:**
https://platform.openai.com/usage

**In Your Logs:**
```bash
# Backend logs show cost per request
[LLMEnhancer] Batch complete - Actual cost: $0.0234
[task_id] 💰 LLM cost: $0.0234
```

### Set Budget Alerts

1. Go to: https://platform.openai.com/account/limits
2. Set soft limit: $50/month
3. Set hard limit: $100/month
4. Enable email at 80%

---

## 🐛 Troubleshooting

### "OpenAI package not installed"
```bash
pip install openai tiktoken
```

### "API key not found"
```bash
# Check .env file exists
ls -la .env

# Check key is set
grep OPENAI_API_KEY .env
```

### "Connection failed"
- Check API key is correct
- Verify payment method added
- Check you have credits
- Visit: https://platform.openai.com/account/api-keys

### "LLM enhancement not working"
- Check `.env` has `LLM_ENHANCEMENT_ENABLED=true`
- Restart backend server
- Check backend logs for errors
- Run `python3 test_llm_connection.py`

---

## 📖 More Information

- **Full Guide:** `docs/LLM_IMPLEMENTATION_GUIDE.md`
- **Cost Details:** `docs/LLM_COST_REFERENCE.md`
- **API Keys:** `docs/API_KEYS_SETUP_GUIDE.md`

---

## 🎯 Success!

If you see this in logs:
```
✅ [LLMEnhancer] Initialized with gpt-4o-mini
[GrammarChecker] ✨ LLM enhancement ENABLED
[LLMEnhancer] Batch complete - Actual cost: $0.0234
```

You're all set! 🎉

**Cost tracking:** Check your OpenAI dashboard daily  
**Quality:** Compare results with/without enhancement  
**Support:** See troubleshooting section above

