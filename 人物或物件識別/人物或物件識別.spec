# -*- mode: python ; coding: utf-8 -*-

import os
base_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['launcher.py', '人臉識別.py', '即時識別.py', '即時汽車識別系統.py',
     '汽車識別.py', '手指擦玻璃.py', '3D粒子手勢.py', '量子空間.py',
     '偵測手掌數據.py', '電阻識別.py', 'opencv 多物件追蹤.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[
        ('hand_landmarker.task', '.'),
        ('daniel.jpg', '.'),
        ('cars.webp', '.'),
    ],
    hiddenimports=[
        'cv2', 'numpy', 'mediapipe',
        'mediapipe.tasks', 'mediapipe.tasks.python',
        'mediapipe.tasks.python.vision',
        'ultralytics', 'ultralytics.engine',
        'ultralytics.models',
        'ultralytics.models.yolo',
        'ultralytics.models.yolo.model',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='人物或物件識別',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='人物或物件識別',
)
