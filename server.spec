# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['server.py'],
             pathex=['/Users/artembakhanov/Code/server1to3person'],
             binaries=[],
             datas=[('navec_news_v1_1B_250K_300d_100q.tar', '.'), ('slovnet_morph_news_v1.tar', '.'), ('slovnet_ner_news_v1.tar', '.'), ('slovnet_syntax_news_v1.tar', '.'), ('dicts/p_t_given_w.intdawg', 'dicts'), ('dicts/prediction-suffixes-2.dawg', 'dicts'), ('dicts/gramtab-opencorpora-int.json', 'dicts'), ('dicts/grammemes.json', 'dicts'), ('dicts/words.dawg', 'dicts'), ('dicts/gramtab-opencorpora-ext.json', 'dicts'), ('dicts/suffixes.json', 'dicts'), ('dicts/prediction-suffixes-1.dawg', 'dicts'), ('dicts/prediction-suffixes-0.dawg', 'dicts'), ('dicts/paradigms.array', 'dicts'), ('dicts/meta.json', 'dicts')],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='server',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
