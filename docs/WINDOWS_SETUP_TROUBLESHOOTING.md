# Windows Setup Troubleshooting

This guide helps resolve common issues when setting up the Grammar Correction App on Windows.

## Common Issue: Microsoft Visual C++ Build Tools Required

### Error Message

```
error: Microsoft Visual C++ 14.0 or greater is required. 
Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
ERROR: Failed building wheel for cymem
ERROR: Failed building wheel for murmurhash
```

### Why This Happens

Some Python packages (spaCy, cymem, murmurhash) contain C/C++ extensions that need to be compiled on Windows. This requires Microsoft Visual C++ Build Tools.

### Solution 1: Install Microsoft C++ Build Tools (Recommended)

**Quick Install:**

1. Download: [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run the installer
3. Select "Desktop development with C++" workload
4. Install (requires ~7 GB disk space)

**Detailed Steps:**

1. **Download the installer:**
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Click "Download Build Tools"

2. **Run the installer:**
   - Double-click `vs_BuildTools.exe`
   - Wait for the Visual Studio Installer to load

3. **Select workload:**
   - Check "Desktop development with C++"
   - On the right side, ensure these are selected:
     - MSVC v143 - VS 2022 C++ x64/x86 build tools
     - Windows 11 SDK (or Windows 10 SDK)
     - C++ CMake tools for Windows

4. **Install:**
   - Click "Install" button
   - Wait for installation (5-15 minutes)

5. **Restart your terminal/IDE**

6. **Re-run setup:**
   ```cmd
   scripts\windows\dev-setup.bat
   ```

### Solution 2: Use Pre-built Wheels (Faster, Less Disk Space)

If you don't want to install Build Tools, use pre-built wheels:

```cmd
cd backend

REM Activate virtual environment
venv\Scripts\activate

REM Install spaCy with pre-built wheels
pip install spacy -f https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/

REM Or install from conda-forge (if you have conda)
conda install -c conda-forge spacy
```

### Solution 3: Use Python 3.11 or Earlier

Python 3.12+ sometimes has compatibility issues with some packages. Try using Python 3.11:

1. Download Python 3.11: https://www.python.org/downloads/
2. Install Python 3.11
3. Re-create virtual environment:
   ```cmd
   cd backend
   rmdir /s /q venv
   py -3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Solution 4: Use Anaconda/Miniconda (Alternative)

Anaconda pre-compiles packages:

1. Install Miniconda: https://docs.conda.io/en/latest/miniconda.html

2. Create conda environment:
   ```cmd
   cd backend
   conda create -n grammar-app python=3.11
   conda activate grammar-app
   conda install -c conda-forge spacy
   pip install -r requirements.txt
   ```

## Other Common Issues

### Issue: "Python not found"

**Solution:**
1. Install Python 3.9 or higher: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal
4. Verify: `python --version`

### Issue: "node not found" or "npm not found"

**Solution:**
1. Install Node.js: https://nodejs.org/ (LTS version recommended)
2. Restart terminal
3. Verify: `node --version` and `npm --version`

### Issue: Port 8000 or 3000 already in use

**Solution:**
```cmd
REM Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

REM Kill the process (replace <PID> with the number from above)
taskkill /PID <PID> /F
```

### Issue: Permission Denied errors

**Solution:**
- Run terminal as Administrator
- Or disable antivirus temporarily during setup

### Issue: Long path errors

**Solution:**
Enable long paths in Windows:

```cmd
REM Run as Administrator
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Then restart your computer.

### Issue: pip install hangs or is very slow

**Solution:**
```cmd
REM Use a faster mirror
pip config set global.index-url https://pypi.org/simple
pip config set global.trusted-host pypi.org

REM Or upgrade pip
python -m pip install --upgrade pip
```

### Issue: "Cannot find spacy model"

**Solution:**
```cmd
cd backend
venv\Scripts\activate
python -m spacy download en_core_web_sm
```

## Verification

After fixing issues, verify your setup:

```cmd
REM Check Python
python --version

REM Check pip
pip --version

REM Check Node.js
node --version

REM Check npm
npm --version

REM Check virtual environment
cd backend
venv\Scripts\activate
python -c "import spacy; print('spaCy:', spacy.__version__)"
python -c "from services.grammar_checker import GrammarChecker; print('✓ Backend OK')"

REM Check frontend
cd ../frontend
npm list --depth=0
```

## Getting More Help

1. **Check logs:**
   - Backend errors: `backend.log`
   - Frontend errors: `frontend.log`

2. **Common log locations:**
   - Backend: `backend/logs/`
   - Build errors: Terminal output

3. **Still having issues?**
   - Create an issue on GitHub with:
     - Full error message
     - Python version (`python --version`)
     - Windows version
     - Steps you've tried

## Recommended Setup for Windows

For the smoothest experience on Windows:

1. **Use Git Bash** instead of CMD/PowerShell
   - Download: https://git-scm.com/download/win
   - See: `scripts/GITBASH_WINDOWS.md`

2. **Install Visual Studio Code**
   - Download: https://code.visualstudio.com/
   - Set Git Bash as default terminal

3. **Install Windows Terminal** (optional but nice)
   - From Microsoft Store
   - Better terminal experience

4. **Use Python 3.11** (not 3.12+)
   - Better package compatibility
   - Fewer build issues

## Quick Fix Command

Try this one-liner to fix most issues:

```cmd
REM Run this in Command Prompt as Administrator
@echo off
echo Installing common fixes...
python -m pip install --upgrade pip setuptools wheel
pip install --upgrade spacy
python -m spacy download en_core_web_sm
echo Done! Try running setup again.
```

## Prevention

To avoid these issues in the future:

1. ✅ Install Microsoft C++ Build Tools before starting
2. ✅ Use Python 3.11 instead of 3.12+
3. ✅ Use Git Bash for better compatibility
4. ✅ Run terminal as Administrator during initial setup
5. ✅ Keep Python, Node.js, and npm updated

## System Requirements

**Minimum:**
- Windows 10 (21H1 or later) or Windows 11
- Python 3.9+
- Node.js 18+
- 4 GB RAM
- 10 GB free disk space (20 GB with Build Tools)

**Recommended:**
- Windows 11
- Python 3.11
- Node.js 20 LTS
- 8 GB RAM
- 20 GB free disk space
- Microsoft C++ Build Tools installed
- Git Bash installed

## Additional Resources

- [Python on Windows FAQ](https://docs.python.org/3/faq/windows.html)
- [Node.js on Windows](https://nodejs.org/en/download/)
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [Git Bash Guide](scripts/GITBASH_WINDOWS.md)

