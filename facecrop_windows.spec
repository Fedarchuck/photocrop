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

# Gradio и зависимости с data/hidden imports — собираем автоматически
gradio_datas, gradio_binaries, gradio_hiddenimports = collect_all("gradio")
safehttpx_datas, safehttpx_binaries, safehttpx_hiddenimports = collect_all("safehttpx")
groovy_datas, groovy_binaries, groovy_hiddenimports = collect_all("groovy")
httpx_datas, httpx_binaries, httpx_hiddenimports = collect_all("httpx")
httpcore_datas, httpcore_binaries, httpcore_hiddenimports = collect_all("httpcore")
pydantic_datas, pydantic_binaries, pydantic_hiddenimports = collect_all("pydantic")
pydantic_core_datas, pydantic_core_binaries, pydantic_core_hiddenimports = collect_all("pydantic_core")
fastapi_datas, fastapi_binaries, fastapi_hiddenimports = collect_all("fastapi")
starlette_datas, starlette_binaries, starlette_hiddenimports = collect_all("starlette")
jinja2_datas, jinja2_binaries, jinja2_hiddenimports = collect_all("jinja2")
python_multipart_datas, python_multipart_binaries, python_multipart_hiddenimports = collect_all("python_multipart")
orjson_datas, orjson_binaries, orjson_hiddenimports = collect_all("orjson")

a = Analysis(
    ["facecrop_launcher.py"],
    pathex=[],
    binaries=(
        gradio_binaries
        + safehttpx_binaries
        + groovy_binaries
        + httpx_binaries
        + httpcore_binaries
        + pydantic_binaries
        + pydantic_core_binaries
        + fastapi_binaries
        + starlette_binaries
        + jinja2_binaries
        + python_multipart_binaries
        + orjson_binaries
    ),
    datas=(
        gradio_datas
        + safehttpx_datas
        + groovy_datas
        + httpx_datas
        + httpcore_datas
        + pydantic_datas
        + pydantic_core_datas
        + fastapi_datas
        + starlette_datas
        + jinja2_datas
        + python_multipart_datas
        + orjson_datas
        + [
        ("fonts/Inter_24pt-Regular.ttf", "fonts"),
    ]
    ),
    hiddenimports=(
        gradio_hiddenimports
        + safehttpx_hiddenimports
        + groovy_hiddenimports
        + httpx_hiddenimports
        + httpcore_hiddenimports
        + pydantic_hiddenimports
        + pydantic_core_hiddenimports
        + fastapi_hiddenimports
        + starlette_hiddenimports
        + jinja2_hiddenimports
        + python_multipart_hiddenimports
        + orjson_hiddenimports
    ),
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

