# -*- mode: python ; coding: utf-8 -*-

from benten.version import __version__

block_cipher = None


a = Analysis(['benten-ls.py'],
             pathex=[],
             binaries=[],
             datas=[("../benten_schemas/*", "benten_schemas")],
             hiddenimports=[],
             hookspath=["."],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='benten-ls',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=f'benten-{__version__}')
