#!/usr/bin/env python3
"""Render and measure DoF focus/CoC/bypass regressions on a private display.

From the project root, after building Game_EntryPoint:
  .vscode/nix-env.sh python3 Tools/TestDepthOfField.py
Images, temporary scene variants and logs land in .tmp/DepthOfFieldImages.
Uses the engine's standard-library PNG reader; no imaging packages are required.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("screenshots", ROOT / "Engine/Tools/ScreenshotRegression.py")
screenshots = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screenshots)


def region(image, x, y, half_width=0.02, half_height=0.12):
    width, height, rows = image
    left, right = int((x - half_width) * width), int((x + half_width) * width)
    top, bottom = int((y - half_height) * height), int((y + half_height) * height)
    return [[rows[v][u * 3:u * 3 + 3] for u in range(left, right)] for v in range(top, bottom)]


def contrast(image, x):
    # Vertical target stripes: total variation in row-average luminance measures retained detail.
    rows = region(image, x, 0.5)
    values = [sum(0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2] for p in row) / len(row) for row in rows]
    return sum(abs(b - a) for a, b in zip(values, values[1:])) / len(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", default=".build/Game_linux_Debug/Game_EntryPoint_x64")
    parser.add_argument("--wrapper", default="Engine/Tools/Headless.sh")
    parser.add_argument("--frames", type=int, default=16)
    parser.add_argument("--skip-capture", action="store_true")
    args = parser.parse_args()
    output = ROOT / ".tmp/DepthOfFieldImages"
    output.mkdir(parents=True, exist_ok=True)
    scene = json.loads((ROOT / "Assets/Scenes/Tests/DepthOfFieldTest.lvl").read_text())
    # The interactive panel should not cover measured image regions.
    for entity in scene["Entities"]:
        entity["Components"] = [c for c in entity["Components"] if c["Type"] != "ScriptComponent"]
    variants = {
        "sharp": {"DepthOfField": False},
        "middle": {}, "near": {"DoFFocusDistance": 3.5}, "far": {"DoFFocusDistance": 18.0},
        "coc": {"DoFDebugCoC": True}, "zero": {"DoFMaxBlurRadius": 0},
        "ortho": {"Projection": "Orthographic"},
        "ortho_sharp": {"Projection": "Orthographic", "DepthOfField": False},
        "taa": {"TemporalAA": True},
        "odd": {"Width": 961, "Height": 541},
        "far_dark": {"DoFFocusDistance": 18.0, "DarkHighlights": True},
        "sharp_dark": {"DepthOfField": False, "DarkHighlights": True},
        "far_hdr": {"DoFFocusDistance": 18.0, "Width": 1600, "Height": 900},
        "far_hdr_dark": {"DoFFocusDistance": 18.0, "Width": 1600, "Height": 900, "DarkHighlights": True},
        "sharp_hdr": {"DepthOfField": False, "Width": 1600, "Height": 900},
        "sharp_hdr_dark": {"DepthOfField": False, "Width": 1600, "Height": 900, "DarkHighlights": True},
        "far_bright_backdrop": {"DoFFocusDistance": 18.0, "DarkHighlights": True, "BrightBackdrop": True},
    }
    split = {"DoFSplitDiopter": True, "DoFFocusDistance": 3.5, "DoFSplitFocusDistance": 18.0,
             "DoFSplitPosition": 0.5, "DoFSplitFeather": 0.02}
    variants.update({
        "split": split,
        "split_hard": dict(split, DoFSplitFeather=0),
        "split_left_edge": dict(split, DoFSplitPosition=0),
        "split_right_edge": dict(split, DoFSplitPosition=1),
        "split_equal": dict(split, DoFSplitFocusDistance=3.5),
        "split_feather": dict(split, DoFSplitFeather=0.25),
        "split_taa": dict(split, TemporalAA=True),
        "split_odd": dict(split, Width=961, Height=541),
    })
    images = {}
    for name, changes in variants.items():
        image_path = output / f"{name}.png"
        if not args.skip_capture:
            image_path.unlink(missing_ok=True)
            variant = copy.deepcopy(scene)
            camera_entity = next(e for e in variant["Entities"] if e["Name"] == "Main Camera")
            camera = next(c for c in camera_entity["Components"] if c["Type"] == "Camera")
            post = next(c for c in camera_entity["Components"] if c["Type"] == "PostProcess")
            post.update({"Bloom": False, "AmbientOcclusion": False, "FXAA": False, "VignetteIntensity": 0})
            post.update({k: v for k, v in changes.items() if k not in ("Projection", "Width", "Height", "DarkHighlights", "BrightBackdrop")})
            camera["Projection"] = changes.get("Projection", "Perspective")
            if changes.get("DarkHighlights"):
                for entity in variant["Entities"]:
                    if entity["Name"].startswith("Bokeh Light "):
                        next(c for c in entity["Components"] if c["Type"] == "Mesh")["Material"]["EmissiveIntensity"] = 0
            if changes.get("BrightBackdrop"):
                backdrop = next(e for e in variant["Entities"] if e["Name"] == "Backdrop")
                material = next(c for c in backdrop["Components"] if c["Type"] == "Mesh")["Material"]
                material.update({"DiffuseColor": [1, 1, 1], "EmissiveColor": [1, 1, 1], "EmissiveIntensity": 4})
            scene_path = output / f"{name}.lvl"
            scene_path.write_text(json.dumps(variant))
            command = shlex.split(args.wrapper) + [args.game, "--scene", str(scene_path),
                "--frames", str(max(args.frames, 8)), "--frame-time", "0.016666667",
                "--width", str(changes.get("Width", 960)), "--height", str(changes.get("Height", 540)),
                "--no-audio", "--screenshot", str(image_path), "--exit"]
            with (output / f"{name}.log").open("w") as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=120)
            if result.returncode:
                raise RuntimeError(f"{name} capture failed; see {output / (name + '.log')}")
        images[name] = screenshots.read_png(image_path)
        print(f"Captured {name}", flush=True)

    failures = []

    def check(condition, description):
        print(f"{'PASS' if condition else 'FAIL'} {description}", flush=True)
        if not condition:
            failures.append(description)

    # Positions are the projected centres of the authored targets at a 20-degree vertical FOV.
    for label, x, focused in [("near", 0.172, "near"), ("middle", 0.5, "middle"), ("far", 0.775, "far")]:
        sharp = contrast(images["sharp"], x)
        measured = contrast(images[focused], x)
        check(sharp > 1, f"{label} target contains measurable detail ({sharp:.2f})")
        check(measured > sharp * 0.80, f"{label} focus preserves detail ({measured:.2f}/{sharp:.2f})")
        defocused = contrast(images["near" if label == "middle" else "middle"], x)
        check(defocused < measured * 0.85, f"{label} defocus reduces detail ({defocused:.2f}/{measured:.2f})")
    for label, x, channel in [("foreground red", 0.172, 0), ("background green", 0.775, 1)]:
        pixels = [p for row in region(images["coc"], x, 0.5, 0.01, 0.02) for p in row]
        check(sum(p[channel] for p in pixels) > 5 * sum(p[1 - channel] + 1 for p in pixels), f"CoC shows {label}")
    pixels = [p for row in region(images["coc"], 0.5, 0.5, 0.01, 0.02) for p in row]
    check(max(max(p) for p in pixels) < 20, "CoC is black at the focal plane")
    # Immediately outside the near target's right silhouette, its blurred red colour must
    # cover previously visible background. This catches a hard foreground cutout.
    def redness(image):
        pixels = [p for row in region(image, 0.280, 0.5, 0.002, 0.08) for p in row]
        return sum(p[0] - p[1] for p in pixels) / len(pixels)
    check(redness(images["middle"]) > redness(images["sharp"]) + 15, "blurred foreground spills beyond its sharp silhouette")
    check(images["zero"] == images["sharp"], "zero-radius bypass exactly matches disabled DoF")
    check(images["ortho"] == images["ortho_sharp"], "orthographic bypass exactly matches disabled DoF")
    check(contrast(images["taa"], 0.5) > contrast(images["sharp"], 0.5) * 0.75, "TAA retains sharp focused detail")
    check(contrast(images["odd"], 0.5) > contrast(images["sharp"], 0.5) * 0.75, "odd resolution retains sharp focused detail")

    def max_error(a, b, left=0.0, right=1.0):
        width, height, rows = a
        return max(abs(rows[y][x] - b[2][y][x]) for y in range(height)
                   for x in range(int(left * width) * 3, int(right * width) * 3))

    for name in ("split", "split_hard", "split_feather"):
        check(max_error(images[name], images["near"], 0, 0.35) <= 1,
              f"{name} left side matches independently rendered near lens")
        check(max_error(images[name], images["far"], 0.65, 1) <= 1,
              f"{name} right side matches independently rendered far lens")
    check(max_error(images["split_hard"], images["near"], 0, 0.5) <= 1
          and max_error(images["split_hard"], images["far"], 0.5, 1) <= 1,
          "zero feather is a hard split without cross-lens blur contamination")
    for name, reference in (("split_left_edge", "far"), ("split_right_edge", "near"), ("split_equal", "near")):
        check(max_error(images[name], images[reference]) <= 1, f"{name} matches the corresponding ordinary lens")
    blurred_middle = max(contrast(images["near"], 0.5), contrast(images["far"], 0.5))
    check(contrast(images["split_feather"], 0.5) < blurred_middle * 1.1,
          "feather blends blurred images without a false focused strip from signed CoC cancellation")
    for name in ("split", "split_taa", "split_odd"):
        for label, x in (("near", 0.172), ("far", 0.775)):
            check(contrast(images[name], x) > contrast(images["sharp"], x) * 0.75,
                  f"{name} retains the {label} subject's focused detail")

    def highlight_ghosts(focused, dark, sharp, sharp_dark):
        width, height, rows = focused
        # Visible, sharp light footprints are measured from an emission-only difference.
        # Focused background points may be attenuated by blurred foreground, but may not
        # reappear elsewhere on a bar with the foreground's much larger blur radius.
        sources = set()
        for y in range(height):
            for x in range(width):
                i = x * 3
                if max(abs(sharp[2][y][i + c] - sharp_dark[2][y][i + c]) for c in range(3)) > 16:
                    sources.add((x, y))
        allowed = set()
        for x, y in sources:
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    allowed.add((x + dx, y + dy))
        errors = []
        for y in range(int(height * 0.2), int(height * 0.7)):
            for x in range(int(width * 0.56), int(width * 0.70)):
                i = x * 3
                r, g, b = sharp[2][y][i:i + 3]
                if r > 80 and g < 50 and b < 50 and (x, y) not in allowed:
                    errors.append(max(abs(rows[y][i + c] - dark[2][y][i + c]) for c in range(3)))
        unobstructed = [(x, y) for x, y in sources if x < width * 0.55 or x > width * 0.70]
        original_energy = sum(max(sharp[2][y][x * 3 + c] - sharp_dark[2][y][x * 3 + c], 0)
            for x, y in unobstructed for c in range(3))
        retained_energy = sum(max(rows[y][x * 3 + c] - dark[2][y][x * 3 + c], 0)
            for x, y in unobstructed for c in range(3))
        return len(sources), len(errors), max(errors, default=255), retained_energy / max(original_energy, 1)

    for suffix in ("", "_hdr"):
        dark_name = "far_hdr_dark" if suffix else "far_dark"
        sharp_dark_name = "sharp_hdr_dark" if suffix else "sharp_dark"
        sources, count, ghost, retained = highlight_ghosts(images["far" + suffix], images[dark_name],
            images["sharp" + suffix], images[sharp_dark_name])
        size = images["far" + suffix][:2]
        check(sources > 50 and count > 100, f"HDR regression at {size} samples lights and foreground bars ({count} pixels)")
        check(ghost < 16, f"focused lights at {size} do not form displaced copies on bars (max error {ghost}/255)")
        check(0.9 < retained < 1.1, f"visible focused lights at {size} retain their brightness ({retained:.3f})")
    def background_brightness(image):
        pixels = [p for row in region(image, 0.68, 0.5, 0.002, 0.08) for p in row]
        return sum((p[1] + p[2]) * 0.5 for p in pixels) / len(pixels)
    check(background_brightness(images["far_bright_backdrop"]) > background_brightness(images["far_dark"]) + 60,
        "foreground hole filling preserves an extended bright background")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
