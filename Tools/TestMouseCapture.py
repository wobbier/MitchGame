#!/usr/bin/env python3
"""Check slow OS mouse motion in an embedded Game View on a private X11 display.

Build MitchEngine_Tests with config=game_linux_debug, then run:
    Engine/Tools/NixEnv.sh python3 Tools/TestMouseCapture.py

XTest injects one-pixel movements in all four directions; no desktop window is touched.
"""
import ctypes
import ctypes.util
import glob
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def library(name, package, filename):
    candidates = [ctypes.util.find_library(name), *glob.glob(f'/nix/store/*{package}*/lib/{filename}')]
    for path in candidates:
        if not path:
            continue
        try:
            ctypes.CDLL(path)
            return path
        except OSError:
            continue
    raise RuntimeError(f'{name} is required for OS mouse injection')


env = os.environ.copy()
env['MITCH_TEST_XTEST_LIBRARY'] = library('Xtst', 'libXtst', 'libXtst.so.6')
env['MITCH_TEST_X11_LIBRARY'] = library('X11', 'libx11', 'libX11.so.6')
subprocess.run(['Engine/Tools/Headless.sh', '.build/Game_linux_Debug/MitchEngine_Tests',
                '--test-case=Input:*'], cwd=ROOT, env=env, check=True, timeout=120)
