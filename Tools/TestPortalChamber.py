#!/usr/bin/env python3
"""Exercise the saved portal chamber and its real mechanics in the native game.

Run from the project root: Engine/Tools/NixEnv.sh python3 Tools/TestPortalChamber.py
The temporary probe assembly is always replaced by the normal game assembly afterwards.
"""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--frames', type=int, default=1100)
parser.add_argument('--width', type=int, default=960)
parser.add_argument('--height', type=int, default=540)
args = parser.parse_args()
OUT = ROOT / '.tmp/PortalChamberTests'
OUT.mkdir(parents=True, exist_ok=True)
project = OUT / 'ChamberProbe.csproj'
project.write_text(f'''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<TargetFramework>net8.0</TargetFramework><AssemblyName>Game.Script</AssemblyName>
<EnableDefaultItems>false</EnableDefaultItems><AllowUnsafeBlocks>true</AllowUnsafeBlocks>
</PropertyGroup><ItemGroup><Compile Include="{ROOT}/Assets/Scripts/Portals/*.cs" />
<Compile Include="{ROOT}/Tools/PortalGun/ChamberProbe.cs" />
<ProjectReference Include="{ROOT}/Engine/Modules/ScriptCore/ScriptCore.csproj" />
</ItemGroup></Project>''')
scene = json.loads((ROOT / 'Assets/Scenes/Portals.lvl').read_text())
scene['Entities'].append({'Name': 'Chamber Regression Probe', 'GUID': 'de00000000000002',
    'Components': [{'Type': 'Transform', 'Position': [0, 0, 0], 'Rotation': [0, 0, 0], 'Scale': [1, 1, 1]},
                   {'Type': 'ScriptComponent', 'ScriptName': 'ChamberProbe', 'ScriptFields': '{}'}]})
scene_path = OUT / 'probe.lvl'
scene_path.write_text(json.dumps(scene))

def build(path):
    subprocess.run(['dotnet', 'build', str(path), '-c', 'Debug', '-o', str(ROOT / '.build/Game_linux_Debug'),
                    '--artifacts-path', str(OUT / 'artifacts'), '--nologo'], cwd=ROOT, check=True)

try:
    build(project)
    with (OUT / 'probe.log').open('w') as log:
        subprocess.run(['Engine/Tools/Headless.sh', '.build/Game_linux_Debug/Game_EntryPoint_x64',
            '--scene', str(scene_path), '--frames', str(args.frames), '--frame-time', '0.016666667',
            '--width', str(args.width), '--height', str(args.height), '--no-audio',
            '--screenshot', str(OUT / 'probe.png'), '--exit'], cwd=ROOT,
            stdout=log, stderr=subprocess.STDOUT, check=True, timeout=480)
    output = (OUT / 'probe.log').read_text()
    for line in output.splitlines():
        if 'CHAMBER ' in line or 'Exception' in line:
            print(line)
    if 'CHAMBER FAIL:' in output or 'threw ' in output or 'CHAMBER ALL PASSED:' not in output:
        raise RuntimeError(f'Chamber regression failed: {OUT / "probe.log"}')
finally:
    build(ROOT / 'Project/Game.Script.csproj')
