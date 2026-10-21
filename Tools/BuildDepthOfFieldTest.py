#!/usr/bin/env python3
"""Rebuild the self-contained DoF optics/occlusion test scene; run from any directory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
entities = []


def entity(name, position, scale=(1, 1, 1), components=(), rotation=(0, 0, 0, 1)):
    entities.append({
        "GUID": hashlib.sha256(name.encode()).hexdigest()[:16],
        "Name": name, "DestroyOnLoad": True,
        "Components": [{"Type": "Transform", "Position": position,
                        "Rotation": rotation, "Scale": scale}, *components],
    })


def mesh(name, position, scale, colour, shape="Cube", emission=0):
    # Engine cubes span [-1, 1]; scene dimensions below are full lengths.
    mesh_scale = [value * 0.5 for value in scale] if shape == "Cube" else scale
    entity(name, position, mesh_scale, [{"Type": "Mesh", "MeshType": shape, "Material": {
        "Type": "StandardMaterial", "DiffuseColor": colour,
        "Roughness": 0.45, "Metallic": 0.0,
        "EmissiveColor": colour, "EmissiveIntensity": emission,
    }}])


entity("Main Camera", [0, 1.6, -8], components=[
    {"Type": "Camera", "ClearType": "Color", "ClearColor": [0.025, 0.035, 0.06],
     "IsCurrent": True, "Projection": "Perspective", "FieldOfView": 20, "Zoom": 20,
     "Near": 0.1, "Far": 100},
    {"Type": "PostProcess", "DepthOfField": True, "DoFFocusDistance": 8.0,
     "DoFAperture": 1.0, "DoFSensorHeight": 24.0, "DoFMaxBlurRadius": 24.0,
     "DoFDebugCoC": False, "TemporalAA": False, "FXAA": True,
     "Bloom": True, "BloomIntensity": 0.025, "AmbientOcclusion": True,
     "VignetteIntensity": 0.08, "ExposureCompensation": 0.0},
    {"Type": "ScriptComponent", "ScriptName": "DepthOfFieldTest", "ScriptFields": "{}"},
])
# Directional illumination plus a little emissive fill keeps this test independent of probes.
entity("Key Light", [0, 6, -5], components=[{
    "Type": "Light", "LightType": "Directional", "Color": [1.0, 0.93, 0.85],
    "Intensity": 3.0, "CastShadows": True,
}], rotation=[0.25, -0.33, 0.09, 0.905])
mesh("Floor", [0, -0.08, 5], [16, 0.15, 28], [0.13, 0.15, 0.20], emission=0.15)
mesh("Backdrop", [0, 2.2, 12], [15, 6, 0.2], [0.055, 0.07, 0.105], emission=0.25)

# Three target planes, all facing a level camera: their front faces are exactly the named depths.
for label, depth, x, size, colour in [
    ("Near", 3.5, -0.72, 0.42, [0.95, 0.075, 0.04]),
    ("Middle", 8.0, 0.0, 0.80, [0.025, 0.80, 0.85]),
    ("Far", 18.0, 3.1, 1.35, [1.0, 0.55, 0.035]),
]:
    z = depth - 8.0
    mesh(f"{label} Target ({depth:g}m)", [x, 1.6, z + 0.06], [size, size * 1.6, 0.12], colour, emission=0.35)
    for stripe in range(7):
        # Small black/white bars show that focusing preserves detail rather than merely tinting.
        y = 1.6 + (stripe - 3) * size * 0.18
        mesh(f"{label} Detail {stripe}", [x, y, z - 0.006], [size * 0.85, size * 0.055, 0.01],
             [0.015] * 3 if stripe % 2 == 0 else [0.95] * 3, emission=0.35)
    mesh(f"{label} Plinth", [x, 0.35, z + 0.1], [size * 1.1, 0.7, size], [0.10, 0.12, 0.17], emission=0.2)

# Thin foreground occluders cross sharp middle/background detail and exercise near-field spill.
for i in range(3):
    mesh(f"Near Thin Bar {i}", [0.20 + i * 0.12, 1.7, -4.1], [0.025, 0.70, 0.025],
         [0.85, 0.12, 0.055], emission=0.45)

# HDR highlight grid: circular bokeh should remain round, with no separable box-shaped kernel.
for row in range(4):
    for col in range(15):
        colour = ([0.20, 0.60, 1.0], [1.0, 0.55, 0.12], [0.7, 0.2, 0.8])[(col + row) % 3]
        mesh(f"Bokeh Light {row:02d} {col:02d}", [(col - 7) * 0.7, 0.7 + row * 0.75, 10.8],
             [0.055, 0.055, 0.055], colour, "Sphere", emission=18)
for i in range(19):
    mesh(f"Floor Depth Ruler {i}", [0, 0.006, -5 + i], [6, 0.012, 0.035],
         [0.45, 0.48, 0.53], emission=0.2)

output = ROOT / "Assets/Scenes/Tests/DepthOfFieldTest.lvl"
output.write_text(json.dumps({"Version": 2, "Cores": [], "Entities": entities}, indent=4) + "\n")
print(f"Wrote {output.relative_to(ROOT)} ({len(entities)} entities)")
