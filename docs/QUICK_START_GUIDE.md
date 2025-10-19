# Quick Start Guide - Windows Desktop App

Get started with the Grammar Correction App in 5 minutes!

## For End Users

### Step 1: Download
Download `Grammar Correction App-[version]-portable.exe` from the releases page.

### Step 2: Run
Double-click the .exe file. Windows may show a security warning - click "More info" then "Run anyway".

### Step 3: Upload
Drag and drop your .docx file onto the application window, or click "Upload Document".

### Step 4: Analyze
The app will automatically analyze your document. Watch the progress bar.

### Step 5: Download
Click "Download Report" to save the corrected document.

Done! 🎉

## For Developers - Building

### Step 1: Install Prerequisites
- Python 3.8+
- Node.js 18+
- pnpm

### Step 2: Setup Environment
```bash
# Windows
scripts\setup-build-env.bat

# Mac/Linux
chmod +x scripts/setup-build-env.sh
./scripts/setup-build-env.sh
```

### Step 3: Build
```bash
# Windows
scripts\build-windows.bat

# Mac/Linux
chmod +x scripts/build-windows.sh
./scripts/build-windows.sh
```

### Step 4: Test
Find your executable in `electron/dist/Grammar Correction App-*-portable.exe`

## Common Issues

### "Backend failed to start"
**Fix**: Close any app using port 8000, then restart.

### "File upload failed"
**Fix**: Ensure file is .docx format and under 10 MB.

### "Update check failed"
**Fix**: Check internet connection. Updates are optional.

## Tips

- **Faster processing**: Select specific categories instead of all
- **Better results**: Enable AI enhancement (requires OpenAI API key)
- **Large files**: Split into smaller documents for better performance

## Next Steps

- Read the [full documentation](WINDOWS_DESKTOP_README.md)
- Learn about [building from source](BUILDING_WINDOWS_EXECUTABLE.md)
- Configure [AI features](API_KEYS_SETUP_GUIDE.md)

## Need Help?

Open an issue on GitHub with:
- Your Windows version
- Error messages
- Steps to reproduce

