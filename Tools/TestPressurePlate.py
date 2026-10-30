#!/usr/bin/env python3
"""Drop the carried cube onto the plate center/edges and test its real gate response.

Run: Engine/Tools/NixEnv.sh python3 Tools/TestPressurePlate.py
The temporary test assembly is always replaced by the normal game assembly afterwards.
"""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--frames', type=int, default=1100)
parser.add_argument('--allow-failures', action='store_true', help='Capture a known-broken baseline.')
args = parser.parse_args()
OUT = ROOT / '.tmp/PressurePlateTests'
OUT.mkdir(parents=True, exist_ok=True)
project = OUT / 'PressurePlateProbe.csproj'
project.write_text(f'''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<TargetFramework>net8.0</TargetFramework><AssemblyName>Game.Script</AssemblyName>
<EnableDefaultItems>false</EnableDefaultItems><AllowUnsafeBlocks>true</AllowUnsafeBlocks>
</PropertyGroup><ItemGroup><Compile Include="{ROOT}/Assets/Scripts/Portals/*.cs" />
<Compile Include="{ROOT}/Tools/PortalGun/PressurePlateProbe.cs" />
<ProjectReference Include="{ROOT}/Engine/Modules/ScriptCore/ScriptCore.csproj" />
</ItemGroup></Project>''')
scene = json.loads((ROOT / 'Assets/Scenes/Portals.lvl').read_text())
scene['Entities'].append({'Name': 'Pressure Plate Regression Probe', 'GUID': 'de00000000000004',
    'Components': [{'Type': 'Transform', 'Position': [0, 0, 0], 'Rotation': [0, 0, 0], 'Scale': [1, 1, 1]},
                   {'Type': 'ScriptComponent', 'ScriptName': 'PressurePlateProbe', 'ScriptFields': '{}'}]})
scene_path = OUT / 'probe.lvl'
scene_path.write_text(json.dumps(scene))

def build(path):
    subprocess.run(['dotnet', 'build', str(path), '-c', 'Debug', '-o', str(ROOT / '.build/Game_linux_Debug'),
                    '--artifacts-path', str(OUT / 'artifacts'), '--nologo'], cwd=ROOT, check=True)

try:
    build(project)
    print('PLATE PROBE ASSEMBLY READY', flush=True)
    with (OUT / 'probe.log').open('w') as log:
        subprocess.run(['Engine/Tools/Headless.sh', '.build/Game_linux_Debug/Game_EntryPoint_x64',
            '--scene', str(scene_path), '--frames', str(args.frames), '--frame-time', '0.016666667',
            '--width', '800', '--height', '450', '--no-audio', '--screenshot', str(OUT / 'probe.png'),
            '--exit'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=480)
    output = (OUT / 'probe.log').read_text()
    for line in output.splitlines():
        if 'PLATE ' in line or 'Exception' in line: print(line)
    failed = 'PLATE FAIL:' in output or 'threw ' in output or 'PLATE ALL PASSED:' not in output
    if failed and not args.allow_failures:
        raise RuntimeError(f'Pressure plate regression failed: {OUT / "probe.log"}')
finally:
    build(ROOT / 'Project/Game.Script.csproj')
