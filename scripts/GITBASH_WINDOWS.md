# Using Scripts with Git Bash on Windows

If you have Git Bash installed on Windows, you can use the Linux shell scripts (`.sh`) instead of the Windows batch scripts (`.bat`).

## Why Use Git Bash?

- ✅ More powerful shell environment
- ✅ Unix-like commands and tools
- ✅ Better script compatibility with Mac/Linux
- ✅ Supports all the same scripts as Unix/Linux/Mac

## Prerequisites

1. **Install Git for Windows** (includes Git Bash)
   - Download from: https://git-scm.com/download/win
   - During installation, select "Git Bash Here" option

2. **Verify Installation**
   ```bash
   # Open Git Bash and check:
   bash --version
   python --version
   node --version
   ```

## Quick Start

Open **Git Bash** (not Command Prompt or PowerShell) and run:

```bash
# 1. Navigate to project
cd /c/path/to/grammar-correction-app

# 2. Make scripts executable (first time only)
chmod +x scripts/linux/*.sh

# 3. Initial setup
./scripts/linux/dev-setup.sh

# 4. Start development servers
./scripts/linux/start-dev.sh

# 5. Run tests
./scripts/linux/test-all.sh
```

## Important Notes for Git Bash on Windows

### Python Virtual Environment

The Linux scripts will detect if you're on Windows and use the correct virtual environment activation:

```bash
# Automatically detects and uses:
# - Linux/Mac: source venv/bin/activate
# - Git Bash on Windows: source venv/Scripts/activate
```

### Path Handling

Git Bash uses Unix-style paths:
- ✅ Use forward slashes: `/c/Users/YourName/project`
- ❌ Don't use backslashes: `C:\Users\YourName\project`

Git Bash automatically converts paths when needed.

### Python Command

In Git Bash, you can use either:
- `python` (if Python is in PATH)
- `python3` (if multiple versions installed)
- `/c/Python39/python.exe` (absolute path)

The scripts will try `python3` first, then fall back to `python`.

## Troubleshooting

### Issue: "Permission Denied" when running scripts

**Solution:**
```bash
chmod +x scripts/linux/*.sh
```

### Issue: "bad interpreter" or "No such file or directory"

**Cause:** Windows line endings (CRLF) instead of Unix (LF)

**Solution:**
```bash
# Convert line endings for all shell scripts
find scripts/linux -name "*.sh" -exec dos2unix {} \;

# Or using Git:
cd scripts/linux
git config core.autocrlf input
git rm --cached -r .
git reset --hard
```

### Issue: Virtual environment activation fails

**Solution:** The scripts automatically detect Windows Git Bash. If issues persist:

```bash
# Manually activate virtual environment:
cd backend
source venv/Scripts/activate  # Note: Scripts (not bin) on Windows
```

### Issue: `pnpm` not found

**Solution:**
```bash
# Install pnpm globally
npm install -g pnpm

# Or just use npm - scripts will auto-detect
```

### Issue: Port already in use

**Solution:**
```bash
# Find and kill process using port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Find and kill process using port 3000 (frontend)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### Issue: Docker commands fail

**Solution:**
```bash
# Make sure Docker Desktop for Windows is running
# In Git Bash, Docker commands work the same as Linux
docker ps
docker run -d -p 8081:8081 silviof/docker-languagetool:latest
```

## Command Comparison

| Task | Git Bash (Windows) | CMD/PowerShell (Windows) |
|------|-------------------|-------------------------|
| Setup | `./scripts/linux/dev-setup.sh` | `scripts\windows\dev-setup.bat` |
| Start Backend | `./scripts/linux/start-backend.sh` | `scripts\windows\start-backend.bat` |
| Start Frontend | `./scripts/linux/start-frontend.sh` | `scripts\windows\start-frontend.bat` |
| Start Both | `./scripts/linux/start-dev.sh` | `scripts\windows\start-dev.bat` |
| Run Tests | `./scripts/linux/test-all.sh` | `scripts\windows\test-all.bat` |

## Advantages of Git Bash

1. **Consistent Environment** - Same commands work on Windows, Mac, and Linux
2. **Better Tools** - Access to grep, sed, awk, curl, etc.
3. **SSH Support** - Built-in SSH client
4. **Git Integration** - Native Git commands
5. **Script Compatibility** - Can use the same scripts across all platforms

## Best Practices

1. **Always use Git Bash** for development (not CMD or PowerShell)
2. **Set Git Bash as default terminal** in your IDE (VS Code, etc.)
3. **Use Unix-style paths** in scripts and configuration
4. **Keep line endings consistent** (LF, not CRLF)

## IDE Integration

### Visual Studio Code

Set Git Bash as default terminal:

1. Open VS Code settings (Ctrl+,)
2. Search for "terminal.integrated.defaultProfile.windows"
3. Set to "Git Bash"

Or add to `settings.json`:
```json
{
  "terminal.integrated.defaultProfile.windows": "Git Bash",
  "terminal.integrated.profiles.windows": {
    "Git Bash": {
      "path": "C:\\Program Files\\Git\\bin\\bash.exe",
      "icon": "terminal-bash"
    }
  }
}
```

### JetBrains IDEs (PyCharm, WebStorm, etc.)

1. Go to Settings → Tools → Terminal
2. Set Shell path to: `"C:\Program Files\Git\bin\bash.exe" --login`
3. Click OK

## Additional Resources

- [Git Bash Documentation](https://git-scm.com/docs/git-bash)
- [Git for Windows](https://gitforwindows.org/)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)

## Support

If you encounter issues specific to Git Bash on Windows:
1. Check that Git for Windows is up to date
2. Verify Python and Node.js are in your PATH
3. Try running the equivalent `.bat` script as a fallback
4. Report issues with "Git Bash on Windows" in the title

