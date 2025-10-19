# Electron Desktop Application

This directory contains the Electron application that wraps the Grammar Correction app as a Windows desktop executable.

## Structure

```
electron/
├── main.js           # Main Electron process
├── preload.js        # Preload script (security bridge)
├── package.json      # Dependencies and build config
├── icon.png          # Application icon (required)
├── resources/        # Bundled resources (created during build)
│   ├── backend.exe   # Python backend (created by build)
│   └── frontend/     # React app build (created by build)
└── dist/             # Build output (created by electron-builder)
```

## Development

### Run in Development Mode

```bash
# Ensure backend and frontend are running separately
cd electron
npm install
npm run dev
```

Development mode:
- Loads frontend from `http://localhost:3000`
- Runs Python backend directly (not bundled)
- Enables DevTools
- Hot reload supported

### Build for Production

```bash
# Use the master build script instead
cd ..
scripts/build-windows.bat  # Windows
# or
./scripts/build-windows.sh  # Mac/Linux
```

Or build Electron only (after backend and frontend are ready):

```bash
cd electron
npm install
npm run build:win          # Portable executable
npm run build:win:installer # NSIS installer
```

## Configuration

### Build Settings

Edit `package.json` → `build` section:

- **appId**: Unique application identifier
- **productName**: Display name
- **directories**: Build directories
- **files**: Files to include
- **extraResources**: Resources to copy
- **win**: Windows-specific settings
- **publish**: Auto-update configuration

### Auto-Update

Configure GitHub releases in `package.json`:

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-username",
      "repo": "your-repo"
    }
  }
}
```

Required for auto-update:
1. Create GitHub release
2. Upload executable as release asset
3. `electron-builder` generates `latest.yml` automatically

## Scripts

- `npm run start` - Run packaged app (after build)
- `npm run dev` - Run in development mode
- `npm run build:win` - Build portable .exe
- `npm run build:win:installer` - Build NSIS installer
- `npm run build` - Build for all platforms

## Requirements

### Before Building

1. **Backend executable**: Must exist at `resources/backend.exe`
2. **Frontend build**: Must exist at `resources/frontend/`
3. **Application icon**: Must have `icon.png` (512x512 or larger)
4. **Dependencies**: Run `npm install`

### Build Environment

- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher
- **Windows**: For Windows builds (or use Wine on Linux/Mac)

## Icon

Place `icon.png` in this directory:
- Format: PNG with transparency
- Size: 512x512 or larger (1024x1024 recommended)
- Used for: Window icon, system tray, installer

You can convert to .ico automatically during build.

## Troubleshooting

### Build Issues

**Problem**: "Cannot find backend.exe"
```bash
# Build backend first
python scripts/build-backend.py
```

**Problem**: "Cannot find frontend build"
```bash
# Build frontend first
cd frontend && pnpm run build
```

**Problem**: "Module not found"
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Runtime Issues

**Problem**: Backend doesn't start
- Check if port 8000 is available
- Run backend manually to see errors
- Check `backend.exe` exists in resources

**Problem**: White screen
- Check if frontend files exist in resources
- Open DevTools (F12) to see errors
- Verify `preload.js` is loaded

**Problem**: Auto-update fails
- Check internet connection
- Verify GitHub release exists
- Check `latest.yml` is present

## Development Tips

### Debugging

Enable DevTools in development:
```javascript
// In main.js
mainWindow.webContents.openDevTools();
```

View backend logs:
```javascript
// Backend stdout/stderr printed to console
backendProcess.stdout.on('data', (data) => {
  console.log(`Backend: ${data}`);
});
```

### Testing Changes

Test without full rebuild:
1. Modify `main.js` or `preload.js`
2. Restart Electron: `npm run dev`
3. Changes reflected immediately

For backend/frontend changes:
1. Rebuild that component
2. Copy to `resources/`
3. Restart Electron

### Performance Optimization

Reduce build size:
- Remove unused dependencies
- Exclude dev dependencies
- Use UPX compression
- Minimize resources

Improve startup time:
- Lazy load modules
- Optimize backend startup
- Cache resources
- Preload critical files

## Security

### Best Practices

1. **Context Isolation**: Enabled by default
2. **Node Integration**: Disabled in renderer
3. **Remote Module**: Disabled
4. **Sandbox**: Use sandboxed processes
5. **CSP**: Set Content Security Policy

### Code Signing

For production releases:

1. Get a code signing certificate
2. Configure in `package.json`:
```json
{
  "win": {
    "certificateFile": "path/to/cert.pfx",
    "certificatePassword": "password"
  }
}
```

## Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [Electron Updater](https://www.electron.build/auto-update)
- [Security Guidelines](https://www.electronjs.org/docs/tutorial/security)

## License

[Your License Here]

