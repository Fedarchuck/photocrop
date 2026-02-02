"""
PyInstaller spec для сборки Windows .exe.

Сборка (локально):
  pip install -r requirements.txt
  pip install -e .
  pip install pyinstaller
  pyinstaller facecrop_windows.spec
"""

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Gradio и safehttpx тянут data/hidden imports — собираем автоматически
gradio_datas, gradio_binaries, gradio_hiddenimports = collect_all("gradio")
safehttpx_datas, safehttpx_binaries, safehttpx_hiddenimports = collect_all("safehttpx")

a = Analysis(
    ["facecrop_launcher.py"],
    pathex=[],
    binaries=gradio_binaries + safehttpx_binaries,
    datas=gradio_datas + safehttpx_datas + [
        ("fonts/Inter_24pt-Regular.ttf", "fonts"),
    ],
    hiddenimports=gradio_hiddenimports + safehttpx_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FaceCrop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # без консоли — удобнее обычным пользователям
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

