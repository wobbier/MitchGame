"""Unit tests for Tools/GenerateTerrain.py (issue board #1 / #16).

Run from the game root:  python3 -I -m unittest discover -s Tools/Tests -v
"""

import json
import math
import random
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import GenerateTerrain as gt  # noqa: E402


class ChecksumTests(unittest.TestCase):
    def test_fnv1a64_matches_reference_vectors(self):
        self.assertEqual(gt.fnv1a64(b""), 0xCBF29CE484222325)
        self.assertEqual(gt.fnv1a64(b"a"), 0xAF63DC4C8601EC8C)
        self.assertEqual(gt.fnv1a64(b"foobar"), 0x85944171F73967E8)


class PerlinTests(unittest.TestCase):
    def test_zero_on_lattice_points(self):
        perlin = gt.Perlin2D(3)
        for ix in range(-5, 6):
            for iy in range(-5, 6):
                self.assertEqual(perlin.noise(ix, iy), 0.0)

    def test_range_and_determinism(self):
        a, b, c = gt.Perlin2D(11), gt.Perlin2D(11), gt.Perlin2D(12)
        rng = random.Random(1)
        differs = False
        for _ in range(5000):
            x, y = rng.uniform(-100, 100), rng.uniform(-100, 100)
            va = a.noise(x, y)
            self.assertTrue(-1.0 <= va <= 1.0, va)
            self.assertEqual(va, b.noise(x, y))
            differs = differs or abs(va - c.noise(x, y)) > 1e-6
        self.assertTrue(differs, "different seeds give different noise")

    def test_noise_uses_the_whole_range(self):
        perlin = gt.Perlin2D(5)
        rng = random.Random(2)
        values = [perlin.noise(rng.uniform(-50, 50), rng.uniform(-50, 50)) for _ in range(20000)]
        self.assertLess(min(values), -0.6)
        self.assertGreater(max(values), 0.6)
        self.assertAlmostEqual(sum(values) / len(values), 0.0, delta=0.02)

    def test_continuity_across_a_lattice_edge(self):
        perlin = gt.Perlin2D(9)
        for y in (0.25, 3.75, -2.5):
            self.assertAlmostEqual(perlin.noise(2.0 - 1e-6, y), perlin.noise(2.0 + 1e-6, y), places=4)


class FractalTests(unittest.TestCase):
    def test_fbm_and_ridged_ranges(self):
        fractal = gt.Fractal(gt.Perlin2D(4), octaves=6)
        rng = random.Random(3)
        for _ in range(3000):
            x, y = rng.uniform(-40, 40), rng.uniform(-40, 40)
            self.assertTrue(-1.0 <= fractal.fbm(x, y) <= 1.0)
            self.assertTrue(0.0 <= fractal.ridged(x, y) <= 1.0)

    def test_more_octaves_add_detail(self):
        coarse = gt.Fractal(gt.Perlin2D(4), octaves=1)
        fine = gt.Fractal(gt.Perlin2D(4), octaves=6)
        # High-frequency energy: mean absolute second difference along a line.
        def roughness(f):
            xs = [i * 0.05 for i in range(400)]
            vs = [f.fbm(x, 0.37) for x in xs]
            return sum(abs(vs[i + 1] - 2 * vs[i] + vs[i - 1]) for i in range(1, len(vs) - 1)) / (len(vs) - 2)
        self.assertGreater(roughness(fine), roughness(coarse) * 2.0)


class ParamsTests(unittest.TestCase):
    def test_rejects_invalid_settings(self):
        with self.assertRaises(ValueError):
            gt.TerrainParams(quads=48)
        with self.assertRaises(ValueError):
            gt.TerrainParams(quads=16, patch=32)
        with self.assertRaises(ValueError):
            gt.TerrainParams(quads=8192, patch=16)
        with self.assertRaises(ValueError):
            gt.TerrainParams(tiles=(0, 1))
        with self.assertRaises(ValueError):
            gt.TerrainParams(spacing=0)
        with self.assertRaises(ValueError):
            gt.TerrainParams(preset="volcano")

    def test_presets_fill_defaults_and_overrides_win(self):
        p = gt.TerrainParams(preset="mountains", amplitude=5.0)
        self.assertEqual(p.amplitude, 5.0)
        self.assertEqual(p.octaves, gt.PRESETS["mountains"]["octaves"])
        self.assertEqual(sorted(gt.TerrainParams(tiles=(2, 3), min_tile=(-1, 0)).tiles),
                         [(-1, 0), (-1, 1), (-1, 2), (0, 0), (0, 1), (0, 2)])


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = gt.TerrainParams(seed=21, tiles=(2, 2), min_tile=(-1, -1), quads=8, patch=4, spacing=1.5)
        cls.generator = gt.TerrainGenerator(cls.params)
        cls.tiles = cls.generator.generate()

    def test_every_tile_has_the_right_sample_count(self):
        q = self.params.quads
        self.assertEqual(set(self.tiles), {(-1, -1), (-1, 0), (0, -1), (0, 0)})
        for samples in self.tiles.values():
            self.assertEqual(len(samples), (q + 1) * (q + 1))
            self.assertTrue(all(math.isfinite(s) for s in samples))

    def test_shared_edges_agree_between_neighbours(self):
        q = self.params.quads
        west, east = self.tiles[(-1, 0)], self.tiles[(0, 0)]
        south, north = self.tiles[(0, -1)], self.tiles[(0, 0)]
        for i in range(q + 1):
            # west's last column == east's first column (row-major: z outer, x inner)
            self.assertEqual(west[i * (q + 1) + q], east[i * (q + 1)])
            # south's last row == north's first row
            self.assertEqual(south[q * (q + 1) + i], north[i])
        # the corner shared by all four tiles
        self.assertEqual(self.tiles[(-1, -1)][q * (q + 1) + q], self.tiles[(0, 0)][0])

    def test_same_seed_same_terrain_and_seed_changes_it(self):
        again = gt.TerrainGenerator(gt.TerrainParams(seed=21, tiles=(2, 2), min_tile=(-1, -1), quads=8, patch=4, spacing=1.5)).generate()
        self.assertEqual(again, self.tiles)
        other = gt.TerrainGenerator(gt.TerrainParams(seed=22, tiles=(2, 2), min_tile=(-1, -1), quads=8, patch=4, spacing=1.5)).generate()
        self.assertNotEqual(other, self.tiles)

    def test_presets_shape_the_heights(self):
        flat = gt.TerrainGenerator(gt.TerrainParams(seed=1, quads=8, patch=4, amplitude=0.0, base=3.0)).generate()
        self.assertTrue(all(s == 3.0 for page in flat.values() for s in page))
        mountains = gt.TerrainGenerator(gt.TerrainParams(seed=1, quads=8, patch=4, preset="mountains", base=0.0, amplitude=50.0)).generate()
        self.assertTrue(all(0.0 <= s <= 50.0 for page in mountains.values() for s in page))
        island = gt.TerrainParams(seed=1, tiles=(2, 2), min_tile=(-1, -1), quads=16, patch=4, spacing=4.0, preset="island", sea_level=0.0)
        gen = gt.TerrainGenerator(island)
        x0, z0, x1, z1 = island.world_extent()
        # Corners of an island are below the sea, the middle is land (heights are centred on the sea level + hills).
        self.assertLess(gen.height(x0, z0), 0.0)
        self.assertLess(gen.height(x1, z1), 0.0)
        self.assertGreater(max(gen.height(x, z) for x in range(-20, 21, 5) for z in range(-20, 21, 5)), 0.0)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.params = gt.TerrainParams(seed=5, tiles=(2, 1), min_tile=(0, -1), quads=8, patch=8, spacing=1.0)
        self.generator = gt.TerrainGenerator(self.params)
        self.tiles = self.generator.generate()
        self.manifest_path = gt.write_asset(self.tmp.name, "Unit", self.params, self.tiles)

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_is_a_valid_version_1_source(self):
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["Format"], "MitchTerrain")
        self.assertEqual(manifest["Version"], 1)
        self.assertRegex(manifest["AssetGUID"], r"^[0-9a-f]{16}$")
        self.assertNotEqual(int(manifest["AssetGUID"], 16), 0)
        settings = manifest["Settings"]
        self.assertEqual(settings["TileQuads"], 8)
        self.assertEqual(settings["PatchQuads"], 8)
        self.assertEqual(settings["MinTile"], [0, -1])
        self.assertEqual((settings["TilesX"], settings["TilesZ"]), (2, 1))
        self.assertGreater(settings["HeightRange"], 0.0)
        pages = manifest["Pages"]
        self.assertEqual(len(pages), 2)
        self.assertEqual([p["Tile"] for p in pages], [[0, -1], [1, -1]], "sorted by X then Z")
        sources = [p["Source"] for p in pages]
        self.assertEqual(len(set(sources)), len(sources))
        for source in sources:
            self.assertFalse(source.startswith("/") or ".." in source)
            self.assertTrue((Path(self.tmp.name) / source).is_file())
        meta = json.loads((Path(self.tmp.name) / "Unit.terrain.meta").read_text())
        self.assertEqual(meta, {"FileType": "terrain", "GUID": manifest["AssetGUID"]})

    def test_pages_round_trip_and_heights_fit_the_encoding_range(self):
        manifest = json.loads(self.manifest_path.read_text())
        base, rng = manifest["Settings"]["HeightBase"], manifest["Settings"]["HeightRange"]
        for page in manifest["Pages"]:
            quads, tx, tz, samples = gt.read_page(Path(self.tmp.name) / page["Source"])
            self.assertEqual((quads, [tx, tz]), (8, page["Tile"]))
            expected = [struct.unpack("<f", struct.pack("<f", s))[0] for s in self.tiles[(tx, tz)]]
            self.assertEqual(samples, expected)
            self.assertTrue(all(base <= s <= base + rng for s in samples))

    def test_page_reader_rejects_corruption(self):
        path = Path(self.tmp.name) / "Unit.source" / "0_-1.thp"
        data = bytearray(path.read_bytes())
        data[-1] ^= 0xFF
        path.write_bytes(bytes(data))
        with self.assertRaises(ValueError):
            gt.read_page(path)
        path.write_bytes(bytes(data[:-4]))
        with self.assertRaises(ValueError):
            gt.read_page(path)

    def test_scene_places_the_terrain_and_boxes_above_it(self):
        scene_path = gt.write_scene(Path(self.tmp.name) / "Scenes" / "Unit.lvl", "Assets/Terrain/Unit.terrain", self.generator)
        scene = json.loads(scene_path.read_text())
        self.assertEqual(scene["Cores"], [])
        by_name = {e["Name"]: e for e in scene["Scene"]}
        terrain = next(c for c in by_name["Terrain"]["Components"] if c["Type"] == "Terrain")
        self.assertEqual(terrain["Asset"], "Assets/Terrain/Unit.terrain")
        self.assertTrue(any(c["Type"] == "Camera" and c["IsCurrent"] for c in by_name["Main Camera"]["Components"]))
        for name, entity in by_name.items():
            if name.startswith("Terrain Box"):
                position = next(c for c in entity["Components"] if c["Type"] == "Transform")["Position"]
                self.assertGreater(position[1], self.generator.height(position[0], position[2]))

    def test_cli_writes_asset_and_scene(self):
        out = Path(self.tmp.name) / "cli"
        scene = Path(self.tmp.name) / "cli" / "Test.lvl"
        self.assertEqual(gt.main(["--out", str(out), "--name", "Cli", "--seed", "3", "--quads", "8", "--patch", "4",
                                  "--tiles", "1", "1", "--min-tile", "0", "0", "--scene", str(scene),
                                  "--scene-asset-path", "Assets/Terrain/Cli.terrain"]), 0)
        self.assertTrue((out / "Cli.terrain").is_file())
        self.assertTrue((out / "Cli.terrain.meta").is_file())
        self.assertTrue((out / "Cli.source" / "0_0.thp").is_file())
        self.assertEqual(json.loads(scene.read_text())["Scene"][1]["Components"][1]["Asset"], "Assets/Terrain/Cli.terrain")


if __name__ == "__main__":
    unittest.main()
