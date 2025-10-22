# Environment Configuration for Windows Desktop App

## How .env Files Work

The Grammar Correction Desktop App supports environment variables via `.env` files in multiple locations.

## Configuration Locations (Priority Order)

### For Bundled Executable (Production)

The app checks for `.env` in this order:

1. **Next to the executable** (Recommended for users)
   ```
   Grammar Correction App.exe
   .env                          ← Place here
   ```

2. **Bundled inside the executable** (Set during build)
   - If `.env` exists in project root during build, it's included
   - Good for default configuration
   - Can't be changed without rebuilding

3. **System environment variables**
   - Fallback if no .env file found
   - Can be set in Windows Environment Variables

### For Development

During development (running `python main.py`):
- Loads from project root: `grammar-correction-app/.env`

## Build-Time vs Runtime Configuration

### Build-Time (Bundled in Executable)

To bundle `.env` during build:

1. Create `.env` in project root:
   ```bash
   cd grammar-correction-app
   cp .env.example .env
   # Edit .env with your values
   ```

2. Build the app:
   ```bash
   ./scripts/build-windows.sh
   ```

3. The `.env` will be included in `backend.exe`

**Pros:**
- ✅ Configuration travels with the app
- ✅ No setup required for users

**Cons:**
- ❌ Can't change config without rebuilding
- ❌ API keys are baked into the executable

### Runtime (Next to Executable)

To provide `.env` at runtime (recommended for users):

1. Place `.env` next to the `.exe`:
   ```
   electron/dist/
   ├── Grammar Correction App.exe
   └── .env                        ← Create this
   ```

2. Users can edit this file to configure their app

**Pros:**
- ✅ Users can change configuration
- ✅ API keys not in the executable
- ✅ Easy updates without rebuilding

**Cons:**
- ❌ Users must create the file
- ❌ File can be lost if app is moved

## Configuration Options

Create a `.env` file with these options:

```env
# OpenAI API Key (optional - for AI features)
OPENAI_API_KEY=sk-proj-your-key-here

# OpenAI Model (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Maximum file size in bytes (default: 10485760 = 10 MB)
MAX_FILE_SIZE=10485760

# Server configuration (for desktop app, use defaults)
PORT=8000
HOST=127.0.0.1

# CORS origins (desktop app handles this automatically)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Enable performance logging
ENABLE_PERFORMANCE_LOGGING=true
```

## Distribution Strategies

### Strategy 1: No Bundled Config (Cleanest)

**Build without .env:**
```bash
# Don't create .env in project root
./scripts/build-windows.sh
```

**Distribution:**
- Ship only the `.exe`
- Include `.env.example` with documentation
- Users create their own `.env` with their API keys

**Best for:** Public distribution, open source

### Strategy 2: Bundled Defaults (Convenient)

**Build with .env:**
```bash
# Create .env with default values (no API keys!)
cat > .env << EOF
OPENAI_MODEL=gpt-4o-mini
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
EOF

./scripts/build-windows.sh
```

**Distribution:**
- Ship the `.exe` with defaults
- Users can override by creating `.env` next to the `.exe`

**Best for:** Internal distribution, enterprise

### Strategy 3: Pre-Configured (Easiest for Users)

**Build with full config:**
```bash
# Create .env with all settings including API key
cp .env.production .env
./scripts/build-windows.sh
```

**Distribution:**
- Ship fully configured `.exe`
- Works immediately
- ⚠️ API key is in the executable

**Best for:** Personal use, specific deployments

## Security Considerations

### API Keys in Executables

**Risk:** If you bundle `.env` with API keys:
- Keys can be extracted from the executable
- Anyone with the file has your keys

**Recommendation:**
- ❌ Don't bundle API keys in public distributions
- ✅ Provide `.env.example` for users
- ✅ Document how to get API keys
- ✅ Let users add their own keys

### Protected Distribution

If you must bundle API keys:
1. Encrypt the `.env` file
2. Use Windows EFS (Encrypting File System)
3. Restrict file permissions
4. Monitor API usage for abuse

## User Instructions

### For End Users

**Setting up OpenAI API Key:**

1. Get your API key from https://platform.openai.com/api-keys

2. Create `.env` file next to the app:
   ```
   Grammar Correction App.exe  ← Your app
   .env                        ← Create this file
   ```

3. Edit `.env` with Notepad:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

4. Restart the app

5. AI features are now enabled!

### Verification

Check if configuration is loaded:
1. Run the app
2. Check console output (if visible)
3. Look for: `[Config] Loaded environment from: ...`

## Troubleshooting

### "No .env file found" message

**Solution:**
- Create `.env` next to the executable
- Or set system environment variables
- Or rebuild with `.env` in project root

### API Key not working

**Check:**
1. `.env` file exists next to the `.exe`
2. File is named exactly `.env` (not `.env.txt`)
3. API key format: `OPENAI_API_KEY=sk-proj-...`
4. No spaces around the `=` sign
5. No quotes around the value

### Configuration not updating

**Solution:**
1. Restart the app completely
2. Check you're editing the right `.env` file
3. Remove bundled `.env` by rebuilding without it

## Examples

### Example 1: Minimal .env (Just AI)
```env
OPENAI_API_KEY=sk-proj-abc123xyz
```

### Example 2: Complete .env
```env
# AI Configuration
OPENAI_API_KEY=sk-proj-abc123xyz
OPENAI_MODEL=gpt-4o-mini

# File Limits
MAX_FILE_SIZE=20971520

# Logging
LOG_LEVEL=DEBUG
ENABLE_PERFORMANCE_LOGGING=true
```

### Example 3: No AI Features
```env
# Disable AI features - use pattern-based only
# Don't set OPENAI_API_KEY

# Other settings
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
```

## Development vs Production

### Development
```bash
# Project root
grammar-correction-app/
├── .env              ← Development config
├── backend/
│   └── main.py
```

### Production (Bundled)
```bash
# App directory
dist/
├── Grammar Correction App.exe
└── .env              ← User's config (optional)
```

## Summary

**Default behavior (no .env):**
- ✅ App runs with default settings
- ❌ No AI features (no API key)
- ✅ Pattern-based checking works

**With .env file:**
- ✅ Custom configuration
- ✅ AI features enabled (with API key)
- ✅ Users control their settings

**Best practice:**
- Build without bundled API keys
- Provide `.env.example`
- Document setup for users
- Users add their own keys

