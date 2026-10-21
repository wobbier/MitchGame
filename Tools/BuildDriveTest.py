#!/usr/bin/env python3
"""Generate the DriveTest terrain (Assets/Terrain/DriveTerrain.terrain) and Assets/Scenes/DriveTest.lvl:
rolling hills with a flat start pad and a mountain rim, a drivable 4x4 (VehicleController.cs), a
cockpit camera (CockpitCamera.cs), guided missiles (MissileLauncher.cs), jump ramps and stacks of physics crates."""

import json
import math
from pathlib import Path
import random
import struct
import sys

TILES = 4            # TILES x TILES source pages
QUADS = 64           # quads per tile edge
SPACING = 2.0        # metres per quad -> 512 m square
HALF = TILES * QUADS * SPACING / 2


def checksum(payload):
    value = 14695981039346656037
    for byte in payload:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def height(x, z):
    hills = (6.0 * math.sin(x * 0.021) * math.cos(z * 0.017)
             + 3.0 * math.sin(x * 0.047 + 1.3) * math.sin(z * 0.039 + 0.4)
             + 1.0 * math.sin(x * 0.11 + z * 0.07))
    # A dune-like ridge line to jump over, east of the start.
    ridge = 4.0 * math.exp(-((x - 70) ** 2) / 120.0) * smoothstep(-120, -60, z) * (1 - smoothstep(60, 120, z))
    # Flat start pad around the origin.
    pad = smoothstep(18, 45, math.hypot(x, z))
    # Mountains around the rim keep the car on the map.
    edge = max(abs(x), abs(z))
    rim = 45.0 * smoothstep(HALF - 70, HALF - 5, edge)
    return pad * (hills + ridge) + rim


def build_terrain(project):
    assets = project / "Assets/Terrain"
    pages = assets / "DriveTerrain.source"
    pages.mkdir(parents=True, exist_ok=True)
    guid = "6472697665746572"
    first = -TILES // 2
    manifest = {
        "Format": "MitchTerrain", "Version": 1, "AssetGUID": guid,
        "Settings": {"TileQuads": QUADS, "PatchQuads": 32, "SampleSpacing": SPACING,
                     "HeightBase": -512, "HeightRange": 1024, "MinTile": [first, first],
                     "TilesX": TILES, "TilesZ": TILES},
        "Pages": [],
    }
    for tx in range(first, first + TILES):
        for tz in range(first, first + TILES):
            payload = b"".join(struct.pack("<f", height((tx * QUADS + x) * SPACING, (tz * QUADS + z) * SPACING))
                               for z in range(QUADS + 1) for x in range(QUADS + 1))
            name = f"{tx}_{tz}.thp"
            header = struct.pack("<4sIIiiQQ", b"MTHP", 1, QUADS, tx, tz, len(payload), checksum(payload))
            (pages / name).write_bytes(header + payload)
            manifest["Pages"].append({"Tile": [tx, tz], "Source": f"DriveTerrain.source/{name}"})
    (assets / "DriveTerrain.terrain").write_text(json.dumps(manifest, indent=2) + "\n")
    (assets / "DriveTerrain.terrain.meta").write_text(json.dumps({"FileType": "terrain", "GUID": guid}, indent=2) + "\n")


def slot_machine(x, z, ground_y, yaw=125.0):
    """Cabinet entities (GUIDs d71e00000000s0..) plus the full-screen UI view the script drives."""
    def mesh(kind, color, emissive=None, intensity=0.0, roughness=0.5, metallic=0.0):
        material = {"Type": "StandardMaterial", "DiffuseColor": list(color), "Roughness": roughness, "Metallic": metallic}
        if emissive:
            material["EmissiveColor"] = list(emissive)
            material["EmissiveIntensity"] = intensity
        return {"Type": "Mesh", "MeshType": kind, "Material": material}

    def part(index, name, position, scale, components, rotation=(0, 0, 0)):
        return {"GUID": f"d71e00000000005{index}", "Name": name, "Parent": "d71e000000000050", "DestroyOnLoad": True,
                "Components": [{"Type": "Transform", "Position": list(position), "Rotation": list(rotation),
                                "Scale": list(scale)}] + components}

    root = {"GUID": "d71e000000000050", "Name": "Slot Machine", "DestroyOnLoad": True, "Components": [
        {"Type": "Transform", "Position": [x, ground_y, z], "Rotation": [0, yaw, 0], "Scale": [1, 1, 1]},
        {"Type": "BoxCollider", "Size": [2.4, 4.4, 2.0], "Center": [0, 2.2, 0]},
        # Driving into this sphere shows the slot UI.
        {"Type": "SphereCollider", "Radius": 9.0, "IsTrigger": True},
        {"Type": "ScriptComponent", "ScriptName": "SlotMachine", "ScriptFields": "{}"},
        {"Type": "Light", "LightType": "Point", "Color": [1.0, 0.75, 0.3], "Intensity": 25.0, "Range": 9.0, "CastShadows": False}]}
    return [
        root,
        part(1, "Slot Cabinet", (0, 1.6, 0), (1.2, 1.6, 1.0), [mesh("Cube", (0.55, 0.05, 0.05), roughness=0.35, metallic=0.3)]),
        part(2, "Slot Screen", (0, 2.1, 1.01), (0.95, 0.55, 0.02), [mesh("Cube", (0.05, 0.05, 0.05), (1.0, 0.85, 0.4), 3.0)]),
        part(3, "Slot Sign", (0, 3.6, 0.2), (1.35, 0.45, 0.5), [mesh("Cube", (0.9, 0.7, 0.1), (1.0, 0.75, 0.1), 6.0)]),
        part(4, "Slot Lever Arm", (1.35, 2.3, 0.2), (0.07, 0.7, 0.07), [mesh("Cylinder", (0.75, 0.75, 0.78), metallic=0.9, roughness=0.2)]),
        part(5, "Slot Lever Knob", (1.35, 3.05, 0.2), (0.2, 0.2, 0.2), [mesh("Sphere", (0.9, 0.05, 0.05), roughness=0.2)]),
        part(6, "Slot Tray", (0, 0.7, 1.05), (0.9, 0.12, 0.25), [mesh("Cube", (0.75, 0.6, 0.15), metallic=0.8, roughness=0.3)]),
        {"GUID": "d71e000000000060", "Name": "Slot UI", "DestroyOnLoad": True, "Components": [
            {"Type": "Transform", "Position": [0, 0, 0], "Rotation": [0, 0, 0], "Scale": [1, 1, 1]},
            {"Type": "BasicUIView", "FilePath": "Assets/UI/Drive/Slots.html"}]},
    ]


def build_props():
    """Physics playthings scattered over the map: brick walls, crate pyramids, barrel stacks, ball
    piles, domino lines and block towers. Entities get GUIDs starting with d71f so --props-only can
    replace them inside a hand-edited scene."""
    rng = random.Random(11)
    entities = []

    def add(name, position, rotation, scale, mesh, color, collider, mass, roughness=0.6, metallic=0.0):
        entities.append({"GUID": f"d71f{len(entities):012x}", "Name": name, "DestroyOnLoad": True, "Components": [
            {"Type": "Transform", "Position": list(position), "Rotation": list(rotation), "Scale": list(scale)},
            {"Type": "Mesh", "MeshType": mesh, "Material": {"Type": "StandardMaterial", "DiffuseColor": list(color),
                                                           "Roughness": roughness, "Metallic": metallic}},
            collider, {"Type": "Rigidbody", "Mass": mass}]})

    box = {"Type": "BoxCollider", "Size": [2, 2, 2]}

    def ground(x, z, half_extent, half_z=None, yaw=0.0):
        """Lays a flat static stone base over a footprint (sunk into the slope) and returns its top."""
        half_z = half_extent if half_z is None else half_z
        c, n = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        samples = [height(x + dx * c + dz * n, z - dx * n + dz * c)
                   for dx in (-half_extent, 0, half_extent) for dz in (-half_z, 0, half_z)]
        top = max(samples) + 0.05
        depth = top - min(samples) + 0.5
        entities.append({"GUID": f"d71f{len(entities):012x}", "Name": f"Base {x:.0f},{z:.0f}", "DestroyOnLoad": True,
                         "Components": [
            {"Type": "Transform", "Position": [x, top - depth / 2, z], "Rotation": [0, yaw, 0],
             "Scale": [half_extent + 0.3, depth / 2, half_z + 0.3]},
            {"Type": "Mesh", "MeshType": "Cube", "Material": {"Type": "StandardMaterial", "DiffuseColor": [0.45, 0.44, 0.42],
                                                               "Roughness": 0.9}},
            {"Type": "BoxCollider", "Size": [2, 2, 2]}]})
        return top

    def brick_wall(cx, cz, yaw, columns=10, rows=6):
        y0 = ground(cx, cz, columns * 0.52, 0.4, yaw)
        r = math.radians(yaw)
        ax, az = math.cos(r), -math.sin(r)
        for row in range(rows):
            for col in range(columns - (row % 2)):
                offset = (col - (columns - 1) / 2 + (row % 2) * 0.5) * 1.02
                color = (0.62 + rng.uniform(-0.06, 0.06), 0.25, 0.18)
                add(f"Brick {cx},{cz} {row}-{col}", (cx + ax * offset, y0 + 0.26 + row * 0.51, cz + az * offset),
                    (0, yaw, 0), (0.5, 0.25, 0.25), "Cube", color, box, 1.5, 0.85)

    def crate_pyramid(cx, cz, base=5):
        y0 = ground(cx, cz, base * 0.6)
        for layer in range(base):
            for i in range(base - layer):
                for j in range(base - layer):
                    x = cx + (i - (base - layer - 1) / 2) * 1.04
                    z = cz + (j - (base - layer - 1) / 2) * 1.04
                    add(f"Crate {cx},{cz} {layer}-{i}-{j}", (x, y0 + 0.5 + layer * 1.0, z), (0, rng.uniform(-4, 4), 0),
                        (0.5, 0.5, 0.5), "Cube", (0.75, 0.5, 0.22), box, 2.0, 0.7)

    def barrel_stack(cx, cz):
        # A ring of eight standing barrels with four more on top.
        y0 = ground(cx, cz, 1.8)
        colors = [(0.75, 0.12, 0.08), (0.15, 0.35, 0.7), (0.2, 0.45, 0.18), (0.85, 0.6, 0.1)]
        for layer, count in ((0, 8), (1, 4)):
            for k in range(count):
                angle = k / count * math.tau
                add(f"Barrel {cx},{cz} {layer}-{k}", (cx + math.cos(angle) * 1.05, y0 + 0.6 + layer * 1.21, cz + math.sin(angle) * 1.05),
                    (0, 0, 0), (0.4, 0.6, 0.4), "Cylinder", rng.choice(colors), {"Type": "MeshCollider", "Convex": True},
                    3.0, 0.4, 0.5)

    def ball_pile(cx, cz, count=30):
        y0 = ground(cx, cz, 3.5)
        for k in range(count):
            radius = rng.uniform(0.25, 0.6)
            add(f"Ball {cx},{cz} {k}", (cx + rng.uniform(-3, 3), y0 + 0.6 + (k // 10) * 1.3, cz + rng.uniform(-3, 3)),
                (0, 0, 0), (radius, radius, radius), "Sphere", (rng.random(), rng.random() * 0.8, rng.random()),
                {"Type": "SphereCollider", "Radius": 1.0, "Restitution": 0.5}, radius * 3, 0.25)

    def dominoes(x0, z0, yaw, count=30):
        # A straight run on one long base; knock the first one over.
        r = math.radians(yaw)
        fx, fz = math.sin(r), math.cos(r)
        length = (count - 1) * 1.1
        cx, cz = x0 + fx * length / 2, z0 + fz * length / 2
        top = ground(cx, cz, 0.6, length / 2 + 0.6, yaw)
        for k in range(count):
            add(f"Domino {x0},{z0} {k}", (x0 + fx * k * 1.1, top + 1.0, z0 + fz * k * 1.1), (0, yaw, 0), (0.4, 1.0, 0.1),
                "Cube", (0.95, 0.95, 0.92), box, 1.0, 0.3)

    def tower(cx, cz, levels=12):
        y0 = ground(cx, cz, 1.5)
        for level in range(levels):
            for k in range(3):
                offset = (k - 1) * 0.9
                pos = (cx + offset, y0 + 0.2 + level * 0.41, cz) if level % 2 == 0 else (cx, y0 + 0.2 + level * 0.41, cz + offset)
                add(f"Block {cx},{cz} {level}-{k}", pos, (0, 0 if level % 2 == 0 else 90, 0), (0.42, 0.2, 1.35),
                    "Cube", (0.9, 0.78, 0.55), box, 1.2, 0.75)

    for cx, cz, yaw in [(0, 70, 0), (-35, 45, 90), (60, -40, 30), (-90, -20, 60), (100, 90, 0), (-130, 120, 45)]:
        brick_wall(cx, cz, yaw)
    for cx, cz in [(25, 35), (-55, 75), (80, 20), (-20, -60), (130, -110), (-140, -130), (40, 140)]:
        crate_pyramid(cx, cz)
    for cx, cz in [(-15, 25), (55, 85), (-100, 60), (110, -30), (-60, -110)]:
        barrel_stack(cx, cz)
    for cx, cz in [(20, -20), (-70, 20), (90, 120), (-120, -60)]:
        ball_pile(cx, cz)
    for x0, z0, yaw in [(-10, -30, 90), (40, -90, 0), (-150, 30, 0), (70, 60, 45)]:
        dominoes(x0, z0, yaw)
    for cx, cz in [(12, 50), (-30, -30), (70, -70), (-80, 100), (140, 40)]:
        tower(cx, cz)

    def jenga(cx, cz, levels=30, width=1.2, thickness=0.7, length=3.6):
        # Three blocks per layer, alternating direction, like the real game at roughly 25x scale.
        y0 = ground(cx, cz, length / 2 + 0.5)
        for level in range(levels):
            for k in range(3):
                offset = (k - 1) * (width + 0.01)
                y = y0 + thickness / 2 + level * thickness
                along_x = level % 2 == 0
                pos = (cx, y, cz + offset) if along_x else (cx + offset, y, cz)
                tint = rng.uniform(-0.05, 0.05)
                add(f"Jenga {cx},{cz} {level}-{k}", pos, (0, 0 if along_x else 90, 0),
                    (length / 2, thickness / 2, width / 2), "Cube", (0.86 + tint, 0.7 + tint, 0.47 + tint), box, 4.0, 0.7)

    # The two giant towers side by side, just ahead of the start.
    for cx in (-5, 5):
        jenga(cx, 24)
    return entities


def add_props(scene):
    data = json.loads(scene.read_text())
    kept = [e for e in data["Entities"] if not e["GUID"].startswith("d71f")]
    props = build_props()
    data["Entities"] = kept + props
    scene.write_text(json.dumps(data, indent=4) + "\n")
    print(f"{scene}: {len(props)} physics props")


def main():
    project = Path(__file__).resolve().parents[1]
    scene = project / "Assets/Scenes/DriveTest.lvl"
    if "--props-only" in sys.argv:
        add_props(scene)
        return
    build_terrain(project)
    rng = random.Random(7)
    entities = []
    counter = [0]

    def entity(name, components, parent=None):
        counter[0] += 1
        guid = f"d71e{counter[0]:012x}"
        record = {"GUID": guid, "Name": name, "DestroyOnLoad": True, "Components": components}
        if parent:
            record["Parent"] = parent
        entities.append(record)
        return guid

    def transform(position, rotation=(0, 0, 0), scale=(1, 1, 1)):
        return {"Type": "Transform", "Position": list(position), "Rotation": list(rotation), "Scale": list(scale)}

    def cube(color, roughness=0.6):
        return {"Type": "Mesh", "MeshType": "Cube",
                "Material": {"Type": "StandardMaterial", "DiffuseColor": list(color), "Roughness": roughness}}

    def script(name, fields):
        return {"Type": "ScriptComponent", "ScriptName": name, "ScriptFields": json.dumps(fields)}

    entity("Sun", [
        transform((0, 50, 0), (42, -35, 0)),
        {"Type": "Light", "LightType": "Directional", "Color": [1.0, 0.94, 0.82], "Intensity": 3.2,
         "CastShadows": True, "ShadowDistance": 120.0},
    ])
    entity("Terrain", [
        transform((0, 0, 0)),
        {"Type": "Terrain", "Asset": "Assets/Terrain/DriveTerrain.terrain", "Color": [0.34, 0.5, 0.22],
         "Roughness": 0.92, "CastShadows": True, "Collision": True, "Friction": 0.8, "Restitution": 0},
    ])

    # The car: root (yaw, kinematic body, collider, controller) -> Body (terrain tilt) -> Model.
    vehicle = entity("Vehicle", [
        transform((0, height(0, 0) + 0.5, 0)),
        {"Type": "Rigidbody", "BodyType": "Kinematic"},
        {"Type": "BoxCollider", "Size": [2.0, 1.1, 4.4], "Center": [0, 1.15, 0]},
        script("VehicleController", {"BodyName": "Vehicle Body"}),
    ])
    body = entity("Vehicle Body", [transform((0, 0, 0))], vehicle)
    entity("Vehicle Model", [
        transform((0, 0, 0), (0, 180, 0)),
        {"Type": "Model", "ModelPath": "Assets/Models/Synty/ExplorerKit/FBX/SM_Veh_4x4_Car_01.fbx"},
    ], body)
    # Driver's-seat camera (CockpitCamera: Look turns the head and aims the missiles).
    entity("Main Camera", [
        transform((-0.36, 1.58, -0.3), (-9.9, 0, 0)),
        {"Type": "Camera", "ClearType": "Procedural", "IsCurrent": True, "Near": 0.1, "Far": 900.0, "Zoom": 60.0},
        {"Type": "PostProcess", "AutoExposure": False, "ExposureCompensation": 0.3, "Bloom": True,
         "BloomIntensity": 0.06, "AmbientOcclusion": True, "FXAA": True},
        {"Type": "AudioListener"},
        script("CockpitCamera", {}),
    ], body)
    # Roof mount the guided missiles launch from (MissileLauncher; Fire shoots).
    entity("Missile Launcher", [transform((0, 2.3, 0.4)), script("MissileLauncher", {})], body)

    # Roadside slot machine (SlotMachine.cs, reels in Assets/UI/Drive/Slots.html): E to spin, three
    # radiation symbols drop a nuke.
    for record in slot_machine(-9.0, 8.0, height(-9.0, 8.0)):
        entities.append(record)

    # Jump ramps: tilted static slabs dug into the ground.
    for index, (x, z, yaw) in enumerate([(0, 40, 0), (-40, 10, -90), (30, -35, 150), (-60, -70, 45)]):
        ground = height(x, z)
        entity(f"Ramp {index}", [
            transform((x, ground + 0.6, z), (-14, yaw, 0), (3.5, 0.3, 5.0)),
            cube((0.55, 0.42, 0.3), 0.8),
            {"Type": "BoxCollider", "Size": [2, 2, 2]},
        ])

    # Crate stacks to plough through.
    for stack, (cx, cz) in enumerate([(14, 20), (-22, -18), (45, 60), (-80, 40)]):
        for layer in range(3):
            for column in range(3 - layer):
                x = cx + (column - (2 - layer) / 2) * 1.05
                y = height(cx, cz) + 0.5 + layer * 1.0
                entity(f"Crate {stack}-{layer}-{column}", [
                    transform((x, y, cz), (0, rng.uniform(-6, 6), 0), (0.5, 0.5, 0.5)),
                    cube((0.75, 0.5, 0.22), 0.7),
                    {"Type": "BoxCollider", "Size": [2, 2, 2]},
                    {"Type": "Rigidbody", "Mass": 2.0},
                ])

    scene.write_text(json.dumps({"Version": 2, "Cores": [], "Entities": entities}, indent=4) + "\n")
    add_props(scene)
    print(f"Wrote {TILES * TILES} terrain pages and {scene}")


if __name__ == "__main__":
    main()
