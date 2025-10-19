# Grammar Correction App - Windows Desktop Edition

A standalone Windows desktop application for grammar checking and document correction.

## Features

✨ **Standalone Application**
- No installation required (portable executable)
- No Python or Node.js needed
- Runs directly from any location

🚀 **Fast & Efficient**
- Local processing for privacy
- Real-time progress tracking
- Background processing

🎯 **Comprehensive Checking**
- 30+ grammar categories
- Spelling and punctuation
- Style and clarity suggestions
- AI-powered enhancements (optional)

🔄 **Auto-Update**
- Automatic update notifications
- One-click update installation
- Always stay current

💾 **Flexible Output**
- Export to DOCX or PDF
- Preserves original formatting
- Track changes mode

## Quick Start

### For Users

1. **Download** the latest release:
   - `Grammar Correction App-[version]-portable.exe`

2. **Run** the executable:
   - Double-click the .exe file
   - Wait 10-15 seconds for startup
   - Application window will open

3. **Use** the application:
   - Upload your document (.doc or .docx)
   - Select grammar categories (optional)
   - Wait for analysis
   - Download corrected document

That's it! No installation or setup required.

### For Developers

See [BUILDING_WINDOWS_EXECUTABLE.md](BUILDING_WINDOWS_EXECUTABLE.md) for build instructions.

## System Requirements

**Minimum:**
- Windows 10 (21H1 or later)
- 4 GB RAM
- 500 MB disk space
- 1280x720 display

**Recommended:**
- Windows 11
- 8 GB RAM
- 1 GB disk space
- 1920x1080 display

**Supported:**
- Windows 10 (21H1+)
- Windows 11
- Windows Server 2019/2022

## First Run

On first launch:
1. Windows may show a security warning (normal for unsigned apps)
2. Click "More info" → "Run anyway"
3. App will start and run backend initialization
4. Main window opens when ready

The application will:
- Create an app data folder in `%APPDATA%\Grammar Correction App`
- Start the backend server on port 8000
- Check for updates (after 3 seconds)

## Using the Application

### Basic Workflow

1. **Launch Application**
   - Double-click the .exe file
   - Wait for startup

2. **Upload Document**
   - Drag and drop a file
   - Or click "Upload Document" button
   - Select .doc or .docx file

3. **Configure Analysis** (Optional)
   - Select specific grammar categories
   - Enable AI enhancement
   - Choose output format

4. **Process Document**
   - Click "Analyze" or upload triggers automatically
   - Watch real-time progress
   - See issues as they're found

5. **Download Results**
   - Click "Download Report"
   - Choose save location
   - Open in Microsoft Word or PDF reader

### Advanced Features

#### Category Selection
Choose which types of issues to check:
- Grammar & Syntax
- Spelling
- Punctuation
- Style & Clarity
- And 25+ more categories

#### AI Enhancement
Enable OpenAI-powered enhancements for:
- More accurate suggestions
- Context-aware corrections
- Natural language improvements

**Note:** Requires OpenAI API key and incurs costs (~$0.01-0.03 per document)

#### Output Formats
- **DOCX**: Editable with track changes
- **PDF**: Read-only with annotations

### System Tray

The application minimizes to system tray:
- Click tray icon to show/hide window
- Right-click for menu:
  - Show App
  - Check for Updates
  - Quit

### Keyboard Shortcuts

- `Ctrl+O` - Open file
- `Ctrl+S` - Download report (when ready)
- `Ctrl+Q` - Quit application
- `F5` - Refresh/restart
- `F12` - Developer tools (dev mode)

## Configuration

### OpenAI API Key

To use AI features:

1. Get API key from [OpenAI](https://platform.openai.com/api-keys)
2. Create `.env` file next to the executable:
   ```
   OPENAI_API_KEY=sk-...
   ```
3. Restart the application

### Advanced Settings

Create a `.env` file with these options:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# File Size Limit (bytes)
MAX_FILE_SIZE=10485760

# Server Configuration
PORT=8000
HOST=127.0.0.1
```

## Troubleshooting

### Application Won't Start

**Symptom**: Double-clicking does nothing

**Solutions**:
1. Check if `backend.exe` is in the resources folder
2. Verify port 8000 is not in use
3. Run from command line to see errors
4. Check antivirus isn't blocking

### Backend Error

**Symptom**: "Backend failed to start" error

**Solutions**:
1. Close other apps using port 8000
2. Check Windows Firewall settings
3. Run as administrator
4. Reinstall/redownload

### Upload Failed

**Symptom**: File upload shows error

**Solutions**:
1. Verify file is .doc or .docx format
2. Check file size is under 10 MB
3. Ensure file isn't corrupted
4. Try a different file

### Slow Performance

**Symptom**: Analysis takes too long

**Solutions**:
1. Close other applications
2. Check available RAM
3. Try smaller documents
4. Disable AI enhancement

### WebSocket Connection Failed

**Symptom**: No real-time progress updates

**Solutions**:
1. Refresh the application
2. Check firewall settings
3. Restart the application

### Update Failed

**Symptom**: Auto-update shows error

**Solutions**:
1. Check internet connection
2. Download update manually
3. Check GitHub releases page

## Known Limitations

1. **File Size**: Maximum 10 MB per document
2. **Formats**: Only .doc and .docx supported
3. **Language**: English only (currently)
4. **Port**: Requires port 8000 to be available
5. **AI Features**: Require OpenAI API key

## Privacy & Security

**Local Processing**:
- All grammar checking runs locally
- No data sent to external servers (except AI features)
- Documents stored temporarily and deleted after

**AI Features**:
- When enabled, sends text to OpenAI
- Subject to OpenAI's privacy policy
- Can be disabled entirely

**Network Usage**:
- Update checks: Contacts GitHub
- AI enhancement: Contacts OpenAI API
- Otherwise: No internet required

## Performance Tips

1. **For Large Documents**:
   - Split into smaller sections
   - Disable unused categories
   - Process during low activity

2. **For Best Quality**:
   - Enable all categories
   - Use AI enhancement
   - Review suggestions manually

3. **For Speed**:
   - Select specific categories only
   - Disable AI features
   - Close other applications

## Uninstallation

Since this is a portable application:

1. Delete the .exe file
2. Delete app data folder:
   - `%APPDATA%\Grammar Correction App`
3. Delete any created shortcuts

No registry changes or system modifications.

## Updates

The application checks for updates automatically:
- Check runs 3 seconds after startup
- Notification appears if update available
- Download and install with one click
- Manual check via tray menu

## Support & Feedback

**Issues**:
- Report bugs on GitHub Issues
- Include version number and error details
- Attach screenshots if possible

**Feature Requests**:
- Submit via GitHub Discussions
- Describe use case and benefit

**Documentation**:
- Building: [BUILDING_WINDOWS_EXECUTABLE.md](BUILDING_WINDOWS_EXECUTABLE.md)
- Testing: [TESTING_EXECUTABLE.md](TESTING_EXECUTABLE.md)
- API Setup: [API_KEYS_SETUP_GUIDE.md](API_KEYS_SETUP_GUIDE.md)

## Version History

### 1.0.0 (Initial Release)
- Standalone Windows executable
- 30+ grammar categories
- Real-time progress tracking
- DOCX/PDF export
- Auto-update support
- System tray integration

## License

[Your License Here]

## Credits

Built with:
- Electron - Desktop framework
- FastAPI - Backend server
- React - Frontend UI
- PyInstaller - Python bundling
- LanguageTool - Grammar checking
- OpenAI - AI enhancements (optional)

---

**Need Help?** Check the [FAQ](FAQ.md) or open an issue on GitHub.

