# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Grammar Correction Backend
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the backend directory
backend_dir = os.path.dirname(os.path.abspath('main.py'))

# Collect all category modules
category_modules = collect_submodules('services.categories')

# Collect data files for various packages
datas = []

# Language Tool Python data files
datas += collect_data_files('language_tool_python')

# Spacy data files
try:
    import en_core_web_sm
    spacy_data_path = en_core_web_sm.__path__[0]
    datas.append((spacy_data_path, 'en_core_web_sm'))
except ImportError:
    print("Warning: en_core_web_sm not found. Please install it with: python -m spacy download en_core_web_sm")

# Tiktoken data files (for OpenAI)
datas += collect_data_files('tiktoken')

# All hidden imports needed
hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'pydantic',
    'pydantic.json',
    'pydantic_core',
    'language_tool_python',
    'docx',
    'docx2txt',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.platypus',
    'spacy',
    'spacy.lang.en',
    'openai',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'httpx',
    'aiofiles',
    'python_multipart',
    'jose',
    'passlib',
    'dotenv',
    # All category modules
    'services.categories',
    'services.categories.base_category',
] + category_modules

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[backend_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# EXE executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

