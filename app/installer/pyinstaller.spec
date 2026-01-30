# pyinstaller.spec
# Build: pyinstaller pyinstaller.spec

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('pynput')


_a = Analysis(
    ['../src/main.py'],
    pathex=['..'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(_a.pure, _a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    _a.scripts,
    _a.binaries,
    _a.zipfiles,
    _a.datas,
    name='CursorZoomRecorder',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
