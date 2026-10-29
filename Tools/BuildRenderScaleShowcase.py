#!/usr/bin/env python3
"""Builds Assets/Scenes/Showcase/RenderScale.lvl (LOOK-S1) from the Lighting showcase.

The Lighting scene's camera becomes four split-screen cameras with the same view, each rendering
below its output size and upscaling with a different filter (bloom and SSAO are off: four full
post chains would pass bgfx's framebuffer limit):

    top left: Bilinear at 0.5       top right: Nearest at 0.35 (uneven blocks)
    bottom left: Pixel at 0.25      bottom right: Sharp at 0.5 (Catmull-Rom + contrast-adaptive sharpening)
                (exact 4 x 4 blocks)

The pixel filters run lower than 0.5 so their blocks survive the regression's 2x downscale.

Run from the project root after Lighting.lvl changes:  python3 Tools/BuildRenderScaleShowcase.py
"""
import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "Assets/Scenes/Showcase/Lighting.lvl")
OUTPUT = os.path.join(ROOT, "Assets/Scenes/Showcase/RenderScale.lvl")

# name, filter, render scale, viewport (x, y from the top left, width, height), stable GUID
VIEWS = [
    ("Bilinear", "Bilinear", 0.5, [0.0, 0.0, 0.5, 0.5], "52a3f0c1e9b84d01"),
    ("Nearest", "Nearest", 0.35, [0.5, 0.0, 0.5, 0.5], "52a3f0c1e9b84d02"),
    ("Pixel", "Pixel", 0.25, [0.0, 0.5, 0.5, 0.5], "52a3f0c1e9b84d03"),
    ("Sharp", "Sharp", 0.5, [0.5, 0.5, 0.5, 0.5], "52a3f0c1e9b84d04"),
]


def main():
    with open(SOURCE) as f:
        scene = json.load(f)
    entities = scene["Entities"]
    index = next(i for i, e in enumerate(entities) if any(c["Type"] == "Camera" for c in e["Components"]))
    template = entities[index]
    cameras = []
    for i, (name, upscale, scale, viewport, guid) in enumerate(VIEWS):
        camera = copy.deepcopy(template)
        camera["GUID"] = guid
        camera["Name"] = "Camera (" + name + ")"
        for component in camera["Components"]:
            if component["Type"] == "Camera":
                component["IsCurrent"] = i == 0
                component["Viewport"] = viewport
                component["RenderScale"] = scale
                component["Upscale"] = upscale
                component["UpscaleSharpness"] = 0.6
            elif component["Type"] == "PostProcess":
                # Four cameras' bloom chains and SSAO targets would pass bgfx's framebuffer limit.
                component["Bloom"] = False
                component["AmbientOcclusion"] = False
        cameras.append(camera)
    entities[index:index + 1] = cameras
    with open(OUTPUT, "w", newline="\n") as f:
        json.dump(scene, f, indent=4)
        f.write("\n")
    print("wrote", os.path.relpath(OUTPUT, ROOT))


if __name__ == "__main__":
    main()
