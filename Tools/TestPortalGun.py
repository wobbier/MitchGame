#!/usr/bin/env python3
"""Build a temporary runtime probe, check placement/traversal, then restore the normal scripts.
Run from the project root: Engine/Tools/NixEnv.sh python3 Tools/TestPortalGun.py
"""
import argparse
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--frame-time', type=float, default=0.016666667)
parser.add_argument('--label', default='probe', help='Name for the temporary scene, screenshot and log')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.tmp/PortalGunTests'
OUT.mkdir(parents=True, exist_ok=True)
project = OUT / 'PortalProbe.csproj'
project.write_text(f'''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<TargetFramework>net8.0</TargetFramework><AssemblyName>Game.Script</AssemblyName>
<EnableDefaultItems>false</EnableDefaultItems><AllowUnsafeBlocks>true</AllowUnsafeBlocks>
</PropertyGroup><ItemGroup><Compile Include="{ROOT}/Assets/Scripts/Portals/*.cs" />
<Compile Include="{ROOT}/Tools/PortalGun/PortalProbe.cs" />
<ProjectReference Include="{ROOT}/Engine/Modules/ScriptCore/ScriptCore.csproj" />
</ItemGroup></Project>''')
scene = json.loads((ROOT / 'Assets/Scenes/Tests/PortalPhysics.lvl').read_text())
scene['Entities'].append({'Name': 'Portal Regression Probe', 'GUID': 'de00000000000001',
    'Components': [{'Type': 'Transform', 'Position': [0,0,0], 'Rotation': [0,0,0], 'Scale': [1,1,1]},
                   {'Type': 'ScriptComponent', 'ScriptName': 'PortalProbe', 'ScriptFields': '{}'}]})
scene_path = OUT / f'{args.label}.lvl'
scene_path.write_text(json.dumps(scene))
def build(path):
    subprocess.run(['dotnet', 'build', str(path), '-c', 'Debug', '-o', str(ROOT / '.build/Game_linux_Debug'),
                    '--artifacts-path', str(OUT / 'artifacts'), '--nologo'], cwd=ROOT, check=True)
try:
    build(project)
    with (OUT / f'{args.label}.log').open('w') as log:
        subprocess.run(['Engine/Tools/Headless.sh', '.build/Game_linux_Debug/Game_EntryPoint_x64',
            '--scene', str(scene_path), '--frames', '300', '--frame-time', str(args.frame_time),
            '--width', '960', '--height', '540', '--no-audio', '--screenshot', str(OUT / f'{args.label}.png'),
            '--exit'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    output = (OUT / f'{args.label}.log').read_text()
    for line in output.splitlines():
        if 'PORTAL ' in line or 'Exception' in line: print(line)
    if 'Shader compile failed:' in output or 'PORTAL FAIL:' in output or 'threw ' in output or 'PORTAL ALL PASSED:' not in output:
        raise RuntimeError(f'Portal regression failed: {OUT / (args.label + '.log')}')
finally:
    build(ROOT / 'Project/Game.Script.csproj')
