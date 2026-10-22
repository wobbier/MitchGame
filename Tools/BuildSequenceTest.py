#!/usr/bin/env python3
"""Rebuild the self-contained object and camera animation demonstration."""
import hashlib
import json
from pathlib import Path

from CameraSequences import push_pull, as_asset, asset_references

ROOT = Path(__file__).resolve().parents[1]
entities = []


def entity(name, position, scale=(1, 1, 1), components=(), rotation=(0, 0, 0, 1)):
    guid = hashlib.sha256(("sequence-test/" + name).encode()).hexdigest()[:16]
    result = {"GUID": guid, "Name": name, "DestroyOnLoad": True,
              "Components": [{"Type": "Transform", "Position": position, "Rotation": rotation, "Scale": scale}, *components]}
    entities.append(result)
    return result


def mesh(name, position, scale, colour, metallic=0.0):
    return entity(name, position, scale, [{"Type": "Mesh", "MeshType": "Cube", "Material": {
        "Type": "StandardMaterial", "DiffuseColor": colour, "Roughness": 0.3, "Metallic": metallic,
        "EmissiveColor": colour, "EmissiveIntensity": 0.12}}])


camera = entity("Main Camera", [0, 2, -12], components=[
    {"Type": "Camera", "ClearType": "Color", "ClearColor": [0.025, 0.04, 0.065],
     "IsCurrent": True, "FieldOfView": 52, "Near": 0.1, "Far": 100},
    {"Type": "PostProcess", "AmbientOcclusion": True, "Bloom": True, "BloomIntensity": 0.06,
     "FXAA": True, "TemporalAA": False, "VignetteIntensity": 0.15}])
sequence = push_pull(camera["GUID"], [0, 2, -12], [0, 0, 0, 1], [0, 0, 1], subject_distance=12.0)
camera["Components"].append(sequence)
entity("Key Light", [0, 6, -5], components=[
    {"Type": "Light", "LightType": "Directional", "Color": [1.0, 0.88, 0.7], "Intensity": 3.5, "CastShadows": True}],
    rotation=[0.25, -0.33, 0.09, 0.905])
mesh("Floor", [0, -0.15, 6], [12, 0.15, 20], [0.08, 0.12, 0.17])
mesh("Plinth", [0, 0.5, 0], [1.5, 0.5, 1.5], [0.2, 0.24, 0.3])
# The subject's front face is at z=0. Keep it still; the camera/FOV compensation holds its
# screen size while the background pillars and secondary animated object change perspective.
mesh("Dolly Zoom Subject", [0, 2, 0.04], [0.7, 0.9, 0.04], [0.06, 0.7, 0.85], 0.6)
subject = mesh("Animated Cube", [2.4, 1.3, 4], [0.7, 0.7, 0.7], [0.85, 0.65, 0.12], 0.6)
for i, z in enumerate([-2, 3, 8, 13]):
    for x in [-4, 4]:
        mesh(f"Pillar {i} {x}", [x, 1.5, z], [0.35, 1.5, 0.35], [0.85, 0.4, 0.1])
sequence["Tracks"].append({"Target": subject["GUID"], "Component": "Transform", "Property": "Rotation", "Enabled": True,
                           "Keys": [{"Frame": frame, "Value": q, "Interpolation": "SmoothStep"} for frame, q in
                                    [(0, [0, 0, 0, 1]), (120, [0, 0.70710678, 0, 0.70710678]), (240, [0, 0, 0, 1])]]})
sequence["Tracks"].append({"Target": subject["GUID"], "Component": "Transform", "Property": "Scale", "Enabled": True,
                           "Keys": [{"Frame": frame, "Value": scale, "Interpolation": "SmoothStep"} for frame, scale in
                                    [(0, [0.7, 0.7, 0.7, 0]), (120, [0.9, 1.1, 0.9, 0]), (240, [0.7, 0.7, 0.7, 0])]]})
asset_path = "Assets/Animations/CameraDollyZoom.sequence"
asset, player = as_asset(sequence, asset_path, {e["GUID"]: e["Name"] for e in entities})
camera["Components"][camera["Components"].index(sequence)] = player
camera["Components"].append({"Type": "ScriptComponent", "ScriptName": "SequenceClipProbe"})
(ROOT / asset_path).parent.mkdir(parents=True, exist_ok=True)
(ROOT / asset_path).write_text(json.dumps(asset, indent=4) + "\n")
(ROOT / "Assets/Scenes/Tests/SequenceTest.lvl").write_text(json.dumps({"Version": 2, "Cores": [], "Entities": entities,
    "AssetReferences": asset_references([asset_path], ROOT)}, indent=4) + "\n")
print("wrote Assets/Scenes/Tests/SequenceTest.lvl")
