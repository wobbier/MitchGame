#!/usr/bin/env python3
"""Procedural terrain from Perlin noise (issue board #1).

Writes a MitchEngine terrain source asset (format version 1, see Engine/Docs/Terrain.md "Source
formats"): a `<Name>.terrain` JSON manifest, one `<Name>.source/<tx>_<tz>.thp` Float32 page per tile
and the `<Name>.terrain.meta` sidecar, plus (optionally) a test scene that places it.

Heights are a pure function of the terrain-wide sample lattice, so tiles agree on their shared
edges by construction and the same seed always produces the same terrain. Three presets:

    hills      fractal Brownian motion of gradient (Perlin) noise with a quintic fade
    mountains  Musgrave-style ridged multifractal (sharp crests, smooth valleys)
    island     hills shaped by a radial falloff to a sea level

Examples (from the game root):

    Tools/GenerateTerrain.py --out Assets/Terrain --name Procedural --seed 7 \
        --tiles 2 2 --min-tile -1 -1 --quads 64 --patch 16 --spacing 2 \
        --scene Assets/Scenes/Tests/TerrainProceduralTest.lvl
    Tools/GenerateTerrain.py --preset mountains --amplitude 80 --frequency 0.004 --out .tmp/Terrain

Pure Python on purpose (the dev shell's python3 has no numpy); a 2x2 x 64-quad terrain takes well
under a second, 4x4 x 128 quads a few seconds. Unit tests: python3 -I -m unittest discover -s Tools/Tests
"""

import argparse
import hashlib
import json
import math
import random
import struct
from pathlib import Path

PAGE_MAGIC = b"MTHP"
PAGE_VERSION = 1
PAGE_HEADER = struct.Struct("<4sIIiiQQ")  # magic, version, quads, tile x, tile z, payload bytes, FNV-1a
MANIFEST_FORMAT = "MitchTerrain"
MANIFEST_VERSION = 1
MAX_TILE_QUADS = 4096
MAX_PATCH_QUADS = 1024

PRESETS = {
    "hills": dict(amplitude=12.0, frequency=1.0 / 120.0, octaves=5, lacunarity=2.0, gain=0.5, warp=0.35),
    "mountains": dict(amplitude=60.0, frequency=1.0 / 300.0, octaves=6, lacunarity=2.1, gain=0.5, warp=0.25),
    "island": dict(amplitude=18.0, frequency=1.0 / 100.0, octaves=5, lacunarity=2.0, gain=0.5, warp=0.3),
}


def fnv1a64(payload):
    """The engine's page checksum (TerrainSerialization.cpp)."""
    value = 0xCBF29CE484222325
    for byte in payload:
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def fade(t):
    """Perlin's quintic fade: zero first and second derivatives at the lattice."""
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(edge0, edge1, x):
    t = min(max((x - edge0) / (edge1 - edge0), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


class Perlin2D:
    """Classic gradient noise on the integer lattice, scaled to roughly [-1, 1] (zero on lattice points)."""

    _SQ = math.sqrt(0.5)
    GRADIENTS = ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0), (_SQ, _SQ), (-_SQ, _SQ), (_SQ, -_SQ), (-_SQ, -_SQ))
    # The largest 2D value with unit gradients is sqrt(2)/2, so this maps the range onto [-1, 1].
    SCALE = math.sqrt(2.0)

    def __init__(self, seed):
        rng = random.Random(seed)
        table = list(range(256))
        rng.shuffle(table)
        self.perm = table + table

    def gradient(self, ix, iy):
        return self.GRADIENTS[self.perm[(ix & 255) + self.perm[iy & 255]] & 7]

    def noise(self, x, y):
        x0 = math.floor(x)
        y0 = math.floor(y)
        fx = x - x0
        fy = y - y0
        g00 = self.gradient(x0, y0)
        g10 = self.gradient(x0 + 1, y0)
        g01 = self.gradient(x0, y0 + 1)
        g11 = self.gradient(x0 + 1, y0 + 1)
        n00 = g00[0] * fx + g00[1] * fy
        n10 = g10[0] * (fx - 1.0) + g10[1] * fy
        n01 = g01[0] * fx + g01[1] * (fy - 1.0)
        n11 = g11[0] * (fx - 1.0) + g11[1] * (fy - 1.0)
        u = fade(fx)
        v = fade(fy)
        value = lerp(lerp(n00, n10, u), lerp(n01, n11, u), v) * self.SCALE
        return min(max(value, -1.0), 1.0)


class Fractal:
    """fBm and ridged multifractal sums over one Perlin field; octaves are rotated so lattices never line up."""

    ROTATION = 0.7  # radians between octaves

    def __init__(self, perlin, octaves=5, lacunarity=2.0, gain=0.5):
        self.perlin = perlin
        self.octaves = max(1, int(octaves))
        self.lacunarity = lacunarity
        self.gain = gain

    def _rotated(self, x, y, octave):
        angle = self.ROTATION * octave
        c, s = math.cos(angle), math.sin(angle)
        return x * c - y * s + 31.7 * octave, x * s + y * c - 17.3 * octave

    def fbm(self, x, y):
        """Sum of octaves normalized to roughly [-1, 1]."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        weight_sum = 0.0
        for octave in range(self.octaves):
            rx, ry = self._rotated(x * frequency, y * frequency, octave)
            total += self.perlin.noise(rx, ry) * amplitude
            weight_sum += amplitude
            amplitude *= self.gain
            frequency *= self.lacunarity
        return total / weight_sum

    def ridged(self, x, y, offset=1.0, ridge_gain=2.0):
        """Musgrave's ridged multifractal in roughly [0, 1]: crests where the noise crosses zero."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        weight = 1.0
        weight_sum = 0.0
        for octave in range(self.octaves):
            rx, ry = self._rotated(x * frequency, y * frequency, octave)
            signal = offset - abs(self.perlin.noise(rx, ry))
            signal = signal * signal * weight
            weight = min(max(signal * ridge_gain, 0.0), 1.0)
            total += signal * amplitude
            weight_sum += amplitude
            amplitude *= self.gain
            frequency *= self.lacunarity
        return min(max(total / weight_sum, 0.0), 1.0)


class TerrainParams:
    """Everything that determines the heights. Validated like Heightfield::Settings::Validate."""

    def __init__(self, seed=7, tiles=(2, 2), min_tile=(-1, -1), quads=64, patch=16, spacing=2.0,
                 preset="hills", base=0.0, amplitude=None, frequency=None, octaves=None,
                 lacunarity=None, gain=None, warp=None, sea_level=None):
        if preset not in PRESETS:
            raise ValueError(f"unknown preset '{preset}' (one of {', '.join(PRESETS)})")
        defaults = PRESETS[preset]
        self.seed = int(seed)
        self.tiles_x, self.tiles_z = int(tiles[0]), int(tiles[1])
        self.min_tile = (int(min_tile[0]), int(min_tile[1]))
        self.quads = int(quads)
        self.patch = int(patch)
        self.spacing = float(spacing)
        self.preset = preset
        self.base = float(base)
        self.amplitude = float(defaults["amplitude"] if amplitude is None else amplitude)
        self.frequency = float(defaults["frequency"] if frequency is None else frequency)
        self.octaves = int(defaults["octaves"] if octaves is None else octaves)
        self.lacunarity = float(defaults["lacunarity"] if lacunarity is None else lacunarity)
        self.gain = float(defaults["gain"] if gain is None else gain)
        self.warp = float(defaults["warp"] if warp is None else warp)
        self.sea_level = self.base if sea_level is None else float(sea_level)
        self.validate()

    def validate(self):
        def power_of_two(n):
            return n > 0 and (n & (n - 1)) == 0
        if not power_of_two(self.quads) or self.quads > MAX_TILE_QUADS:
            raise ValueError(f"tile quads must be a power of two up to {MAX_TILE_QUADS}, got {self.quads}")
        if not power_of_two(self.patch) or self.patch > MAX_PATCH_QUADS or self.patch > self.quads:
            raise ValueError(f"patch quads must be a power of two up to min({MAX_PATCH_QUADS}, tile quads), got {self.patch}")
        if self.tiles_x < 1 or self.tiles_z < 1:
            raise ValueError("at least one tile in each direction")
        if not (self.spacing > 0.0 and math.isfinite(self.spacing)):
            raise ValueError("sample spacing must be positive")
        if not (self.amplitude >= 0.0 and math.isfinite(self.amplitude)):
            raise ValueError("amplitude must be finite and non-negative")
        if not (self.frequency > 0.0 and math.isfinite(self.frequency)):
            raise ValueError("frequency must be positive")

    @property
    def tiles(self):
        return [(self.min_tile[0] + tx, self.min_tile[1] + tz) for tx in range(self.tiles_x) for tz in range(self.tiles_z)]

    def world_extent(self):
        """Terrain-local X/Z bounds in metres."""
        x0 = self.min_tile[0] * self.quads * self.spacing
        z0 = self.min_tile[1] * self.quads * self.spacing
        return x0, z0, x0 + self.tiles_x * self.quads * self.spacing, z0 + self.tiles_z * self.quads * self.spacing


class TerrainGenerator:
    """Evaluates heights for a TerrainParams; `height(x, z)` takes terrain-local metres."""

    def __init__(self, params):
        self.params = params
        self.shape = Fractal(Perlin2D(params.seed), params.octaves, params.lacunarity, params.gain)
        # Separate fields for the domain warp, so warping never correlates with the heights.
        self.warp_x = Fractal(Perlin2D(params.seed * 7919 + 1), 3, 2.0, 0.5)
        self.warp_z = Fractal(Perlin2D(params.seed * 7919 + 2), 3, 2.0, 0.5)
        x0, z0, x1, z1 = params.world_extent()
        self.center = ((x0 + x1) * 0.5, (z0 + z1) * 0.5)
        self.radius = max(x1 - x0, z1 - z0) * 0.5

    def height(self, x, z):
        p = self.params
        nx, nz = x * p.frequency, z * p.frequency
        if p.warp > 0.0:
            # Domain warping bends the lattice so ridges and hills meander instead of running straight.
            nx += self.warp_x.fbm(nx * 0.5, nz * 0.5) * p.warp
            nz += self.warp_z.fbm(nx * 0.5, nz * 0.5) * p.warp
        if p.preset == "mountains":
            h = p.base + self.shape.ridged(nx, nz) * p.amplitude
        else:
            h = p.base + self.shape.fbm(nx, nz) * p.amplitude
        if p.preset == "island":
            dx, dz = x - self.center[0], z - self.center[1]
            r = math.sqrt(dx * dx + dz * dz) / max(self.radius, 1e-6)
            mask = 1.0 - smoothstep(0.55, 1.0, r)
            # Land sinks towards (and slightly below) the sea level at the edges.
            h = p.sea_level - 2.0 + (h + 2.0 - p.sea_level) * mask
        return h

    def sample(self, sx, sz):
        """Height at integer terrain-wide sample coordinates."""
        return self.height(sx * self.params.spacing, sz * self.params.spacing)

    def tile(self, tx, tz):
        """Row-major (z outer, x inner) Float32-ready heights for one tile, (quads + 1)^2 of them."""
        q = self.params.quads
        return [self.sample(tx * q + x, tz * q + z) for z in range(q + 1) for x in range(q + 1)]

    def generate(self):
        return {tile: self.tile(*tile) for tile in self.params.tiles}


def height_settings(tiles):
    """HeightBase / HeightRange that cover every sample with a margin, so a UInt16 cook can encode them."""
    low = min(min(samples) for samples in tiles.values())
    high = max(max(samples) for samples in tiles.values())
    margin = max(1.0, (high - low) * 0.05)
    base = math.floor(low - margin)
    rng = math.ceil(high - low + 2.0 * margin)
    return float(base), float(max(rng, 1))


def asset_guid(name, seed):
    """A stable nonzero 16-digit hexadecimal GUID (the manifest's AssetGUID)."""
    digest = hashlib.sha1(f"MitchGame terrain {name} seed {seed}".encode("utf-8")).hexdigest()[:16]
    return digest if int(digest, 16) != 0 else "7465727261696e02"


def encode_page(quads, tx, tz, samples):
    expected = (quads + 1) * (quads + 1)
    if len(samples) != expected:
        raise ValueError(f"tile ({tx}, {tz}) has {len(samples)} samples, expected {expected}")
    payload = struct.pack(f"<{expected}f", *samples)
    return PAGE_HEADER.pack(PAGE_MAGIC, PAGE_VERSION, quads, tx, tz, len(payload), fnv1a64(payload)) + payload


def read_page(path):
    """Decodes and validates a version 1 page like the engine's reader; returns (quads, tx, tz, samples)."""
    data = Path(path).read_bytes()
    if len(data) < PAGE_HEADER.size:
        raise ValueError("page header truncated")
    magic, version, quads, tx, tz, length, checksum = PAGE_HEADER.unpack_from(data, 0)
    if magic != PAGE_MAGIC or version != PAGE_VERSION:
        raise ValueError("not a version 1 MitchTerrain page")
    payload = data[PAGE_HEADER.size:]
    count = (quads + 1) * (quads + 1)
    if length != len(payload) or length != count * 4:
        raise ValueError("page payload length mismatch")
    if fnv1a64(payload) != checksum:
        raise ValueError("page checksum mismatch")
    samples = list(struct.unpack(f"<{count}f", payload))
    if not all(math.isfinite(s) for s in samples):
        raise ValueError("page has non-finite heights")
    return quads, tx, tz, samples


def build_manifest(params, name, tiles):
    base, rng = height_settings(tiles)
    manifest = {
        "Format": MANIFEST_FORMAT,
        "Version": MANIFEST_VERSION,
        "AssetGUID": asset_guid(name, params.seed),
        "Settings": {
            "TileQuads": params.quads,
            "PatchQuads": params.patch,
            "SampleSpacing": params.spacing,
            "HeightBase": base,
            "HeightRange": rng,
            "MinTile": [params.min_tile[0], params.min_tile[1]],
            "TilesX": params.tiles_x,
            "TilesZ": params.tiles_z,
        },
        # Sorted by X then Z, like the engine's own serializer.
        "Pages": [{"Tile": [tx, tz], "Source": f"{name}.source/{tx}_{tz}.thp"} for (tx, tz) in sorted(tiles)],
    }
    return manifest


def write_asset(out_dir, name, params, tiles):
    """Writes <name>.terrain, <name>.terrain.meta and the pages; returns the manifest path."""
    out_dir = Path(out_dir)
    pages_dir = out_dir / f"{name}.source"
    pages_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(params, name, tiles)
    for (tx, tz), samples in tiles.items():
        (pages_dir / f"{tx}_{tz}.thp").write_bytes(encode_page(params.quads, tx, tz, samples))
    manifest_path = out_dir / f"{name}.terrain"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (out_dir / f"{name}.terrain.meta").write_text(json.dumps({"FileType": "terrain", "GUID": manifest["AssetGUID"]}, indent=2) + "\n")
    return manifest_path


def build_scene(asset_path, generator, color=(0.34, 0.5, 0.22)):
    """A test scene like Tools/BuildTerrainTest.py's: camera, the terrain, a sun and boxes on the surface."""
    params = generator.params
    x0, z0, x1, z1 = params.world_extent()
    size = max(x1 - x0, z1 - z0)
    center_x, center_z = (x0 + x1) * 0.5, (z0 + z1) * 0.5
    peak = max(generator.height(center_x + dx, center_z + dz) for dx in (-size * 0.25, 0.0, size * 0.25) for dz in (-size * 0.25, 0.0, size * 0.25))

    def transform(position, rotation=(0, 0, 0)):
        return {"Type": "Transform", "Position": [float(v) for v in position], "Rotation": list(rotation), "Scale": [1, 1, 1]}

    entities = [
        {"Name": "Main Camera", "Components": [
            transform((center_x, peak + size * 0.35, z0 - size * 0.15), (30, 0, 0)),
            {"Type": "Camera", "ClearType": "Color", "ClearColor": [0.16, 0.24, 0.34], "IsCurrent": True,
             "Near": 0.1, "Far": max(500.0, size * 4.0), "Zoom": 55}]},
        {"Name": "Terrain", "Components": [
            transform((0, 0, 0)),
            {"Type": "Terrain", "Asset": asset_path, "Color": list(color), "Roughness": 0.9,
             "CastShadows": True, "Collision": True, "Friction": 0.6, "Restitution": 0}]},
        {"Name": "Sun", "Components": [
            transform((0, 50, 0), (50, -30, 0)),
            {"Type": "Light", "LightType": "Directional", "Color": [1, 0.93, 0.78], "Intensity": 3, "CastShadows": True}]},
    ]
    for index, fraction in enumerate((-0.2, 0.0, 0.2)):
        x = center_x + fraction * size
        entities.append({"Name": f"Terrain Box {index + 1}", "Components": [
            transform((x, generator.height(x, center_z) + 1.0, center_z)),
            {"Type": "Mesh", "MeshType": "Cube", "Material": {"Type": "StandardMaterial", "DiffuseColor": [0.85, 0.32, 0.1], "Roughness": 0.55}},
            {"Type": "Rigidbody", "Mass": 1}, {"Type": "BoxCollider", "Size": [1, 1, 1]}]})
    # The existing v1 migration supplies stable-in-session entity GUIDs on load.
    return {"Cores": [], "Scene": entities}


def write_scene(path, asset_path, generator):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_scene(asset_path, generator), indent=2) + "\n")
    return path


def stats(tiles):
    samples = [s for page in tiles.values() for s in page]
    return {"samples": len(samples), "min": min(samples), "max": max(samples), "mean": sum(samples) / len(samples)}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default="Assets/Terrain", help="folder for the .terrain, .meta and .source pages")
    parser.add_argument("--name", default="Procedural", help="asset name (Procedural -> Procedural.terrain)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="hills")
    parser.add_argument("--tiles", type=int, nargs=2, default=(2, 2), metavar=("X", "Z"))
    parser.add_argument("--min-tile", type=int, nargs=2, default=(-1, -1), metavar=("X", "Z"))
    parser.add_argument("--quads", type=int, default=64, help="quads per storage tile (power of two)")
    parser.add_argument("--patch", type=int, default=16, help="quads per render patch (power of two <= quads)")
    parser.add_argument("--spacing", type=float, default=2.0, help="metres between samples")
    parser.add_argument("--base", type=float, default=0.0, help="height the noise is centred on, metres")
    parser.add_argument("--amplitude", type=float, help="height range of the noise, metres (preset default)")
    parser.add_argument("--frequency", type=float, help="noise cycles per metre (preset default)")
    parser.add_argument("--octaves", type=int)
    parser.add_argument("--lacunarity", type=float)
    parser.add_argument("--gain", type=float)
    parser.add_argument("--warp", type=float, help="domain warp strength, 0 for none")
    parser.add_argument("--sea-level", type=float, help="island preset: the level the edges sink to")
    parser.add_argument("--scene", help="also write a .lvl test scene placing the terrain")
    parser.add_argument("--scene-asset-path", help="asset path the scene refers to (default: --out/--name relative to the cwd)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    params = TerrainParams(seed=args.seed, tiles=args.tiles, min_tile=args.min_tile, quads=args.quads, patch=args.patch,
                           spacing=args.spacing, preset=args.preset, base=args.base, amplitude=args.amplitude,
                           frequency=args.frequency, octaves=args.octaves, lacunarity=args.lacunarity, gain=args.gain,
                           warp=args.warp, sea_level=args.sea_level)
    generator = TerrainGenerator(params)
    tiles = generator.generate()
    manifest_path = write_asset(args.out, args.name, params, tiles)
    info = stats(tiles)
    print(f"Wrote {manifest_path} ({len(tiles)} pages, {info['samples']} samples, heights {info['min']:.2f}..{info['max']:.2f} m)")
    if args.scene:
        asset_path = args.scene_asset_path or (Path(args.out) / f"{args.name}.terrain").as_posix()
        print(f"Wrote {write_scene(args.scene, asset_path, generator)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
