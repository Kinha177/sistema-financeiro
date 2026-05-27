# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — SisGest Financeiro
# Gera um pacote one-directory para Windows (sem console).
#
# Uso:
#   pyinstaller sisfinanceiro.spec --noconfirm
# ou via build.ps1

from pathlib import Path

ROOT = Path(SPECPATH)

block_cipher = None

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Estilos e recursos visuais
        (str(ROOT / "assets"), "assets"),
        # Scripts Alembic (não usados no executável, mas incluídos por precaução)
        (str(ROOT / "alembic"), "alembic"),
        (str(ROOT / "alembic.ini"), "."),
    ],
    hiddenimports=[
        # SQLAlchemy
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.dialects.sqlite.pysqlite",
        # Alembic
        "alembic.runtime.migration",
        "alembic.operations.ops",
        "alembic.operations.base",
        "alembic.autogenerate",
        # ReportLab
        "reportlab.graphics",
        "reportlab.platypus",
        "reportlab.lib.styles",
        "reportlab.lib.enums",
        "reportlab.lib.pagesizes",
        "reportlab.lib.units",
        "reportlab.lib.utils",
        "reportlab.lib.colors",
        # openpyxl
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.utils",
        "openpyxl.writer.excel",
        # PySide6 extras (carregados dinamicamente pelo Qt)
        "PySide6.QtSvg",
        "PySide6.QtXml",
        "PySide6.QtPrintSupport",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "notebook", "IPython"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SisGestFinanceiro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                 # sem janela de terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",      # descomente se tiver ícone .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SisGestFinanceiro",
)
