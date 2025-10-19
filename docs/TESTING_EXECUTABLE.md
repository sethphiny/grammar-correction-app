# Testing the Windows Executable

This guide provides comprehensive testing procedures for the Grammar Correction Windows desktop application.

## Pre-Testing Checklist

Before testing, ensure:
- [ ] Build completed successfully
- [ ] Executable file exists: `electron/dist/Grammar Correction App-*.exe`
- [ ] Test environment is clean (no existing installation)
- [ ] Test documents are prepared (.doc and .docx files)

## Test Environment Setup

### Clean Test Environment

Test on a clean Windows machine that doesn't have:
- Python installed
- Node.js installed
- Any development tools

This ensures the executable is truly standalone.

### Test Documents

Prepare sample documents with:
1. Simple grammar errors (spelling, punctuation)
2. Complex issues (sentence structure, style)
3. Large documents (>100 pages)
4. Small documents (<1 page)
5. Documents with special characters
6. Documents with images/tables

## Functional Tests

### 1. Application Startup

**Test**: Launch the application

**Steps**:
1. Double-click the .exe file
2. Wait for application to start

**Expected Results**:
- ✓ Application window opens within 10-15 seconds
- ✓ No error dialogs appear
- ✓ Backend starts automatically
- ✓ UI loads correctly
- ✓ No console windows visible (unless in debug mode)

**Common Issues**:
- Slow startup: Backend may be initializing
- Backend error: Check if port 8000 is available
- White screen: Frontend failed to load

### 2. System Tray Integration

**Test**: System tray functionality

**Steps**:
1. Minimize the application
2. Check system tray for app icon
3. Right-click tray icon
4. Click "Show App" to restore

**Expected Results**:
- ✓ Icon appears in system tray
- ✓ Context menu shows options
- ✓ "Show App" restores window
- ✓ "Quit" closes application completely

### 3. File Upload

**Test**: Document upload functionality

**Steps**:
1. Click "Upload Document" or drag-and-drop area
2. Select a .docx file
3. Wait for file to upload

**Expected Results**:
- ✓ File selector opens
- ✓ Only .doc and .docx files are selectable
- ✓ Upload progress is shown
- ✓ Upload completes successfully
- ✓ Processing begins automatically

**Test Cases**:
- Small file (<1 MB)
- Medium file (1-5 MB)
- Large file (5-10 MB)
- File with special characters in name
- File from network drive

### 4. Grammar Checking

**Test**: Grammar analysis functionality

**Steps**:
1. Upload a document with known errors
2. Wait for analysis to complete
3. Review detected issues

**Expected Results**:
- ✓ Real-time progress updates
- ✓ Progress bar moves smoothly
- ✓ Issue count updates in real-time
- ✓ Analysis completes successfully
- ✓ Issues are displayed correctly
- ✓ Issues are categorized properly

**Verify**:
- Spelling errors detected
- Grammar errors detected
- Punctuation errors detected
- Style suggestions provided

### 5. Category Selection

**Test**: Category filtering

**Steps**:
1. Before uploading, select specific categories
2. Upload document
3. Verify only selected categories are checked

**Expected Results**:
- ✓ Category checkboxes work
- ✓ Only selected categories are analyzed
- ✓ Processing time adjusts accordingly
- ✓ Results match selected categories

### 6. AI Features

**Test**: LLM enhancement (if enabled)

**Steps**:
1. Enable "AI Enhancement" toggle
2. Upload document
3. Wait for processing

**Expected Results**:
- ✓ Enhanced suggestions are provided
- ✓ Cost estimate is displayed
- ✓ Processing takes longer (expected)
- ✓ Quality of suggestions improves

**Note**: Requires valid OpenAI API key

### 7. Report Generation

**Test**: Download corrected document

**Steps**:
1. Complete grammar check
2. Click "Download Report"
3. Choose save location
4. Verify downloaded file

**Expected Results**:
- ✓ Download dialog appears
- ✓ File downloads successfully
- ✓ File can be opened in Word
- ✓ Corrections are applied
- ✓ Formatting is preserved
- ✓ Comments/suggestions are visible

**Test Both Formats**:
- DOCX output
- PDF output

### 8. WebSocket Connection

**Test**: Real-time updates

**Steps**:
1. Upload a large document
2. Watch the progress updates

**Expected Results**:
- ✓ Progress updates in real-time
- ✓ No lag or freezing
- ✓ Line count increments smoothly
- ✓ Issue count updates immediately
- ✓ Timing information is displayed

### 9. Error Handling

**Test**: Various error scenarios

**Test Cases**:

#### Invalid File
- Upload a non-Word file
- Expected: Clear error message

#### File Too Large
- Upload file >10 MB
- Expected: Size limit error

#### Corrupted File
- Upload corrupted .docx
- Expected: Parse error message

#### Backend Crash
- Kill backend process manually
- Expected: Error dialog and app closes

#### Network Issues
- Disconnect network (for update check)
- Expected: Graceful degradation

### 10. Performance Testing

**Test**: Application performance

**Metrics to Track**:
- Startup time: < 15 seconds
- File upload: < 2 seconds for 1 MB
- Grammar check: < 5 seconds per 100 lines
- Memory usage: < 500 MB
- CPU usage: < 50% average

**Large Document Test**:
1. Upload 50+ page document
2. Monitor resource usage
3. Verify completion

**Expected Results**:
- ✓ No memory leaks
- ✓ Stable performance
- ✓ Responsive UI during processing
- ✓ Accurate progress tracking

### 11. Auto-Update

**Test**: Update functionality

**Steps**:
1. Launch application
2. Wait for update check (automatic after 3 seconds)
3. If update available, test download
4. Test update installation

**Expected Results**:
- ✓ Update check runs silently
- ✓ Notification appears if update available
- ✓ Download progress is shown
- ✓ Update installs correctly
- ✓ App restarts with new version

**Manual Test**:
- Click "Check for Updates" in tray menu
- Verify check runs

### 12. Multi-Session Testing

**Test**: Multiple documents in sequence

**Steps**:
1. Process document 1
2. Process document 2 immediately after
3. Process document 3

**Expected Results**:
- ✓ Each session is independent
- ✓ No data leakage between sessions
- ✓ Temp files are cleaned up
- ✓ Memory is released between sessions

### 13. Application Closure

**Test**: Clean shutdown

**Steps**:
1. Upload and process a document
2. Close application during processing
3. Verify clean shutdown

**Expected Results**:
- ✓ Backend process terminates
- ✓ No orphaned processes
- ✓ Temp files are cleaned up
- ✓ App closes within 3 seconds

## Stress Tests

### Concurrent Operations
- Upload multiple files quickly
- Test with 10+ operations in queue

### Long-Running Session
- Keep app open for 24+ hours
- Process documents periodically
- Check for memory leaks

### Edge Cases
- Empty documents
- Documents with only images
- Documents with 1000+ pages
- Documents with unusual formatting

## UI/UX Testing

### Visual Tests
- [ ] All buttons are clickable
- [ ] Text is readable
- [ ] Colors are consistent
- [ ] Icons display correctly
- [ ] Progress bars animate smoothly
- [ ] Tooltips appear on hover

### Responsiveness
- [ ] Window resize works correctly
- [ ] Minimum window size is enforced
- [ ] UI adapts to window size
- [ ] No layout breaking

### Accessibility
- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Focus indicators are visible
- [ ] Error messages are clear

## Security Tests

### File Handling
- Test with malicious file names
- Test with files containing scripts
- Verify file sandboxing

### API Key Protection
- Check if API keys are exposed in logs
- Verify secure storage

## Compatibility Tests

### Windows Versions
- [ ] Windows 10 (21H1+)
- [ ] Windows 11
- [ ] Windows Server 2019/2022

### System Configurations
- [ ] Low memory (4 GB RAM)
- [ ] Standard (8 GB RAM)
- [ ] High performance (16+ GB RAM)

### Display Settings
- [ ] 100% scaling
- [ ] 125% scaling
- [ ] 150% scaling
- [ ] Multiple monitors

## Regression Tests

After each update, verify:
- [ ] All core features still work
- [ ] No new bugs introduced
- [ ] Performance hasn't degraded
- [ ] UI remains consistent

## Test Result Template

```markdown
## Test Session Report

**Date**: [Date]
**Tester**: [Name]
**Version**: [App Version]
**OS**: Windows [Version]

### Test Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| Startup | ✓ Pass | 12s load time |
| Upload | ✓ Pass | - |
| Analysis | ✓ Pass | - |
| Download | ✓ Pass | - |
| Updates | ✗ Fail | Timeout error |

### Issues Found
1. [Issue description]
2. [Issue description]

### Performance Metrics
- Startup: 12s
- Memory: 320 MB
- CPU: 25% average

### Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

## Known Issues

Document any known issues and workarounds:

1. **First Launch Slow**: First launch may take longer as Windows scans the executable
2. **Antivirus False Positive**: Some antivirus may flag PyInstaller executables
3. **Port Already in Use**: If another app uses port 8000, backend will fail

## Bug Reporting

When reporting bugs, include:
1. Windows version
2. Application version
3. Steps to reproduce
4. Expected vs actual behavior
5. Screenshots/videos
6. Log files (if available)

## Automated Testing (Future)

Consider implementing:
- Electron test automation
- Backend API tests
- End-to-end tests with Playwright
- Performance benchmarking scripts

## Sign-Off Checklist

Before releasing, ensure:
- [ ] All functional tests pass
- [ ] Performance is acceptable
- [ ] No critical bugs
- [ ] Documentation is updated
- [ ] Update system works
- [ ] Clean installation tested
- [ ] User feedback collected

