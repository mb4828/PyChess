# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['venv/lib/python3.11/site-packages', 'game/', 'logic/'],
    binaries=[],
    datas=[('assets/images/*', 'assets/images'), ('assets/sounds/*', 'assets/sounds'), ('venv/lib/python3.11/site-packages/pygame_menu/resources/fonts/*', 'pygame_menu/resources/fonts')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PyChess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/images/pychess.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PyChess',
)
app = BUNDLE(
    coll,
    name='PyChess.app',
    icon='assets/images/pychess.ico',
    bundle_identifier=None,
)
