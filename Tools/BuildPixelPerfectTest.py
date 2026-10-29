#!/usr/bin/env python3
"""Builds Assets/Scenes/Tests/PixelPerfectTest.lvl (LOOK-S6).

An orthographic pixel-perfect camera (240x135 reference, 16 pixels per unit) pans across blocks
placed at fractional positions (Panner: 1.5, 0.23 units/s, 0.4 and 0.06 texels a frame, so some
frames move a texel and most don't). Engine/Tools/PixelShimmerCheck.py captures consecutive frames and requires each pair to be
identical or an exact whole-texel shift. Everything screen-fixed is off: vignette, FXAA, bloom,
shadows (cascades move with the camera) and temporal AA.

    python3 Tools/BuildPixelPerfectTest.py [--no-snap OUT.lvl]   (--no-snap: the control scene)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "Assets/Scenes/Tests/PixelPerfectTest.lvl")


def transform(position, scale=(1.0, 1.0, 1.0), rotation=(0.0, 0.0, 0.0)):
    return {"Type": "Transform", "Position": list(position), "Rotation": list(rotation), "Scale": list(scale)}


def block(guid, name, position, scale, color):
    return {"GUID": guid, "Name": name, "DestroyOnLoad": True, "Components": [
        transform(position, scale),
        {"Type": "Mesh", "MeshType": "Cube", "Material": {"Type": "StandardMaterial", "DiffuseColor": list(color), "Metallic": 0.0, "Roughness": 1.0}},
    ]}


def build(snap):
    camera = {"GUID": "7f31c2d0a4e95b01", "Name": "Pixel Camera", "DestroyOnLoad": True, "Components": [
        transform((0.0, 0.0, -20.0)),
        {"Type": "Camera", "ClearType": "Color", "ClearColor": [0.16, 0.12, 0.22], "IsCurrent": True, "Near": 0.1, "Far": 100.0,
         "Projection": "Orthographic", "OrthographicSize": 4.0, "SunShadows": False, "AmbientOcclusion": False, "VolumetricFog": False,
         "PixelPerfect": True, "ReferenceResolution": [240.0, 135.0], "PixelsPerUnit": 16.0, "PixelSnap": snap},
        {"Type": "PostProcess", "AutoExposure": False, "ExposureCompensation": 0.0, "Bloom": False, "AmbientOcclusion": False,
         "VignetteIntensity": 0.0, "FXAA": False, "TemporalAA": False, "Fog": False},
        {"Type": "ScriptComponent", "ScriptName": "Panner", "ScriptFields": json.dumps({"Velocity": {"x": 1.5, "y": 0.23, "z": 0.0}})},
    ]}
    sun = {"GUID": "7f31c2d0a4e95b02", "Name": "Sun", "DestroyOnLoad": True, "Components": [
        transform((0.0, 10.0, -10.0), rotation=(30.0, 25.0, 0.0)),
        {"Type": "Light", "LightType": "Directional", "Color": [1.0, 0.96, 0.9], "Intensity": 3.0, "CastShadows": False},
    ]}
    entities = [camera, sun]
    colors = [(0.9, 0.35, 0.3), (0.35, 0.75, 0.4), (0.3, 0.5, 0.95), (0.95, 0.8, 0.3), (0.8, 0.4, 0.85)]
    index = 0
    for row in range(-3, 4):
        for column in range(-7, 9):
            if (row + column) % 2:
                continue
            # Off the texel grid on purpose (a 16th of a unit is a texel).
            x = column * 1.37 + 0.031 * row
            y = row * 1.21 + 0.047 * column
            size = 0.5 + 0.11 * ((row * 7 + column * 3) % 4)
            entities.append(block("7f31c2d0a4e9%04x" % index, "Block %d" % index, (x, y, 0.0), (size, size * 0.8, 0.5), colors[index % len(colors)]))
            index += 1
    return {"Version": 2, "Cores": [], "Entities": entities}


def main():
    snap = "--no-snap" not in sys.argv
    output = sys.argv[sys.argv.index("--no-snap") + 1] if not snap else OUTPUT
    with open(output, "w", newline="\n") as f:
        json.dump(build(snap), f, indent=4)
        f.write("\n")
    print("wrote", os.path.relpath(output, ROOT))


if __name__ == "__main__":
    main()
