#!/usr/bin/env python3
"""Generate Assets/Scenes/Tests/TreeTest.lvl: every MitchTree preset (Engine/Assets/Trees/Presets)
planted on a lawn in two rows under a low afternoon sun, for the tree flows and visual checks."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRESETS = ["Oak", "Maple", "Birch", "Pine", "Spruce", "Palm", "DeadSnag", "Bush"]


def guid(index):
    return "7472656500%06x" % index


def transform(position, rotation=(0.0, 0.0, 0.0, 1.0), scale=(1.0, 1.0, 1.0)):
    return {"Type": "Transform", "Position": list(position), "Rotation": list(rotation), "Scale": list(scale)}


def pitch_yaw(pitch_degrees, yaw_degrees):
    """Quaternion (x, y, z, w) for a yaw about +Y followed by a pitch about the local +X."""
    p, y = math.radians(pitch_degrees) * 0.5, math.radians(yaw_degrees) * 0.5
    qy = (0.0, math.sin(y), 0.0, math.cos(y))
    qp = (math.sin(p), 0.0, 0.0, math.cos(p))
    x1, y1, z1, w1 = qy
    x2, y2, z2, w2 = qp
    return (w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2)


def entity(index, name, components):
    return {"GUID": guid(index), "Name": name, "DestroyOnLoad": True, "Components": components}


def main():
    entities = []
    entities.append(entity(1, "Main Camera", [
        transform((0.0, 7.5, -34.0), pitch_yaw(8.0, 0.0)),
        {"Type": "Camera", "IsCurrent": True, "ClearType": "Procedural", "FieldOfView": 55.0, "Near": 0.1, "Far": 400.0,
         "ProceduralSky": {"Time": 16.5, "Turbidity": 2.2, "CloudCoverage": 0.25}},
        {"Type": "PostProcess", "Bloom": True, "BloomIntensity": 0.08, "FXAA": True, "AmbientOcclusion": True, "Tonemapper": "ACES"},
    ]))
    entities.append(entity(2, "Sun", [
        transform((0.0, 20.0, 0.0), pitch_yaw(32.0, -35.0)),
        {"Type": "Light", "LightType": "Directional", "DirectionalSource": "Automatic", "Color": [1.0, 0.92, 0.8], "Intensity": 3.0,
         "CastShadows": True, "ShadowDistance": 90.0},
    ]))
    entities.append(entity(3, "Lawn", [
        transform((0.0, 0.0, 6.0), scale=(40.0, 1.0, 30.0)),
        {"Type": "Mesh", "MeshType": "Plane", "CastShadows": False,
         "Material": {"Type": "StandardMaterial", "DiffuseColor": [0.23, 0.33, 0.14], "Roughness": 0.95}},
    ]))
    for i, name in enumerate(PRESETS):
        row, column = divmod(i, 4)
        x = -21.0 + column * 14.0 + (7.0 if row else 0.0)
        z = row * 16.0
        entities.append(entity(10 + i, name, [
            transform((x, 0.0, z), pitch_yaw(0.0, 37.0 * i)),
            {"Type": "Model", "ModelPath": "Assets/Trees/Presets/%s.mtree" % name, "Compact": True},
        ]))
    scene = {"Version": 2, "Cores": [], "Entities": entities}
    out = ROOT / "Assets" / "Scenes" / "Tests" / "TreeTest.lvl"
    out.write_text(json.dumps(scene, indent=4) + "\n")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
