#!/usr/bin/env python3
"""Check circular DoF point-spread quality, including the maximum 64 px radius.

Run inside the development environment after building Game_EntryPoint. A tiny HDR
square on a coplanar black surface should become a filled, uniform circular disk,
without repeated point copies or a sparse sampling pattern. Tests both CoC signs
at even/odd resolutions; narrow outputs exercise large radii without full 4K cost.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import shlex
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("screenshots", ROOT / "Engine/Tools/ScreenshotRegression.py")
screenshots = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screenshots)


def fixture(focus):
    entities = []

    def entity(name, position, scale, components):
        entities.append(dict(GUID=f"{len(entities) + 1:016x}", Name=name, Components=[
            dict(Type="Transform", Position=position, Rotation=[0, 0, 0, 1], Scale=scale), *components]))

    def surface(power):
        return dict(Type="Mesh", MeshType="Cube", CastShadows=False, Material=dict(
            Type="StandardMaterial", DiffuseColor=[0, 0, 0], EmissiveColor=[1, 1, 1],
            EmissiveIntensity=power, Roughness=1))

    entity("Main Camera", [0, 0, 0], [1, 1, 1], [dict(Type="Camera", IsCurrent=True,
        Projection="Perspective", FieldOfView=20, Near=0.1, Far=30, ClearType="Color", ClearColor=[0, 0, 0]),
        dict(Type="PostProcess", DepthOfField=True, DoFFocusDistance=focus, DoFAperture=0.7,
             DoFSensorHeight=36, DoFMaxBlurRadius=32, DoFSplitDiopter=False, Tonemapper="None",
             Bloom=False, AmbientOcclusion=False, FXAA=False, TemporalAA=False,
             VignetteIntensity=0, ExposureCompensation=0)])
    entity("Coplanar black surface", [0, 0, 3.002], [10, 10, 0.001], [surface(0)])
    # Five full-resolution pixels wide at 1080p; bright enough to measure after
    # spreading, while the resulting disk stays below display clipping.
    entity("Point source", [0, 0, 3], [0.00245, 0.00245, 0.0001], [surface(4)])
    return dict(Version=2, Cores=[], Entities=entities)


def measure(image):
    width, height, rows = image
    radius = min(32 * height / 1080, 64)
    inner, disk, outside = [], [], []
    radial_energy = 0
    total_energy = 0
    for y in range(int(height / 2 - radius * 1.5), int(height / 2 + radius * 1.5) + 1):
        for x in range(int(width / 2 - radius * 1.5), int(width / 2 + radius * 1.5) + 1):
            distance = math.hypot(x + 0.5 - width / 2, y + 0.5 - height / 2)
            encoded = sum(rows[y][x * 3:x * 3 + 3]) / (3 * 255)
            value = encoded / 12.92 if encoded <= 0.04045 else ((encoded + 0.055) / 1.055) ** 2.4
            if distance < radius * 0.55:
                inner.append(value)
            if distance < radius * 0.8:
                radial_energy += value
            if radius * 1.3 < distance < radius * 1.5:
                outside.append(value)
            if distance < radius * 1.5:
                total_energy += value
            if distance < radius * 0.7:
                disk.append(encoded)
    average = statistics.mean(inner)
    return dict(radius=radius, variation=statistics.pstdev(inner) / max(average, 1e-8),
                interior=average, outside=statistics.mean(outside),
                core_energy=radial_energy / max(total_energy, 1e-8), signal=statistics.mean(disk))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", default=".build/Game_linux_Debug/Game_EntryPoint_x64")
    parser.add_argument("--wrapper", default="Engine/Tools/Headless.sh")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--output", default=".tmp/DepthOfFieldBlur")
    parser.add_argument("--skip-capture", action="store_true")
    args = parser.parse_args()
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    failures = []
    for width, height in ((257, 541), (512, 1080), (257, 2161)):
        for label, focus in (("near", 18), ("far", 1)):
            name = f"{label}-{width}x{height}"
            path = output / f"{name}.png"
            if not args.skip_capture:
                path.unlink(missing_ok=True)
                scene = output / f"{name}.lvl"
                scene.write_text(json.dumps(fixture(focus)))
                command = shlex.split(args.wrapper) + [args.game, "--scene", str(scene),
                    "--frames", str(max(8, args.frames)), "--frame-time", "0.016666667",
                    "--width", str(width), "--height", str(height), "--no-audio", "--no-ui",
                    "--no-debug-overlay", "--screenshot", str(path), "--exit"]
                with (output / f"{name}.log").open("w") as log:
                    subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=180, check=True)
            result = measure(screenshots.read_png(path))
            checks = [(result["signal"] > 0.05, "measurable disk"),
                      (result["variation"] < 0.06, f"uniform interior (variation {result['variation']:.1%})"),
                      (0.55 < result["core_energy"] < 0.72,
                       f"circular aperture profile (core energy {result['core_energy']:.1%})"),
                      (result["outside"] < result["interior"] * 0.02, "bounded circular footprint")]
            for passed, description in checks:
                print(f"{'PASS' if passed else 'FAIL'} {name}: {description}", flush=True)
                if not passed:
                    failures.append((name, description))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
