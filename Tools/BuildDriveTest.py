#!/usr/bin/env python3
"""Generate the DriveTest terrain (Assets/Terrain/DriveTerrain.terrain) and Assets/Scenes/DriveTest.lvl:
rolling hills with a flat start pad and a mountain rim, a drivable 4x4 (VehicleController.cs), a
cockpit camera (CockpitCamera.cs), guided missiles (MissileLauncher.cs), a tarot deck on the dash (TarotDeck.cs),
jump ramps and stacks of physics crates, plus set pieces on flattened pads: a casino plaza, a mega ramp
through a ring of fire, a giant bowling alley, a fuel depot of explosive drums (ExplosiveBarrel.cs) and
a stone circle.

The scene is partly hand edited, so `--props-only` is the usual way to rerun this: it rebuilds the
terrain and replaces only the generated props (GUIDs d71f...) and set pieces (d720...)."""

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


# Flat pads under the set pieces: centre x, z, half extents x, z, height and blend distance.
PADS = [
    (10, -145, 30, 24, 0.0, 18),     # casino plaza
    (-40, 150, 82, 9, 1.0, 14),      # mega ramp run
    (155, -45, 8, 52, -1.0, 12),     # bowling alley
    (-152, -60, 14, 16, 0.0, 12),    # fuel depot
    (-150, 160, 16, 14, 1.0, 10),    # stone circle
]


def height(x, z):
    return flatten(x, z, natural_height(x, z))


def flatten(x, z, h):
    for cx, cz, hx, hz, target, blend in PADS:
        outside = math.hypot(max(abs(x - cx) - hx, 0.0), max(abs(z - cz) - hz, 0.0))
        h += (target - h) * (1 - smoothstep(0, blend, outside))
    return h


def natural_height(x, z):
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
            {"Type": "UIDocument", "FilePath": "Assets/UI/Drive/Slots.rml"}]},
    ]


def tarot_deck(body):
    """The dashboard tarot deck (TarotDeck.cs, cards in Assets/UI/Drive/Tarot.rml): a stack of cards on a
    stand right of the wheel, tilted toward the driver. The root (and its glow light) floats 0.16 m above
    the stack along the deck's tilted up axis."""
    yaw, pitch, lift = math.radians(20.0) / 2, math.radians(-40.0) / 2, 0.16
    cy, sy, cx, sx = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    x, y, z, w = cy * sx, sy * cx, -sy * sx, cy * cx
    up = (2 * (x * y - w * z), 1 - 2 * (x * x + z * z), 2 * (y * z + w * x))
    base = (0.0, 1.465, 0.41)
    width, length, half_height = 0.05, 0.082, 0.018
    back = {"Type": "StandardMaterial", "DiffuseColor": [1.0, 1.0, 1.0], "Roughness": 0.85,
            "Textures": {"Diffuse": {"Path": "Assets/UI/Drive/Tarot/Back.png", "RenderMode": "Opaque"}}}

    def part(index, name, y_offset, scale, material, z_offset=0.0):
        return {"GUID": f"7a407a400000000{index}", "Name": name, "Parent": "7a407a4000000001", "DestroyOnLoad": True,
                "Components": [{"Type": "Transform", "Position": [0, y_offset - lift, z_offset], "Rotation": [0, 0, 0], "Scale": list(scale)},
                               {"Type": "Mesh", "MeshType": "Cube", "Material": material}]}

    return [
        {"GUID": "7a407a4000000001", "Name": "Tarot Deck", "Parent": body, "DestroyOnLoad": True, "Components": [
            {"Type": "Transform", "Position": [base[i] + up[i] * lift for i in range(3)], "Rotation": [x, y, z, w], "Scale": [1, 1, 1]},
            {"Type": "ScriptComponent", "ScriptName": "TarotDeck", "ScriptFields": "{}"},
            {"Type": "UIDocument", "FilePath": "Assets/UI/Drive/Tarot.rml"},
            {"Type": "Light", "LightType": "Point", "Color": [0.6, 0.3, 1.0], "Intensity": 0.05, "Range": 0.45, "CastShadows": False}]},
        part(2, "Tarot Stack", half_height, (width, half_height, length), back),
        part(3, "Tarot Card", half_height * 2 + 0.002, (width, 0.0015, length), back),
        part(4, "Tarot Stand", -0.03, (width * 0.8, 0.03, length * 0.75),
             {"Type": "StandardMaterial", "DiffuseColor": [0.05, 0.035, 0.08], "Metallic": 0.6, "Roughness": 0.35}, 0.01),
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


def build_setpieces():
    """The set pieces on the flat PADS. Entities get GUIDs starting with d720 so --props-only can
    replace them inside a hand-edited scene."""
    rng = random.Random(23)
    entities = []

    def material(color, roughness=0.6, metallic=0.0, emissive=None, intensity=0.0, texture=None):
        m = {"Type": "StandardMaterial", "DiffuseColor": list(color), "Roughness": roughness, "Metallic": metallic}
        if emissive:
            m["EmissiveColor"] = list(emissive)
            m["EmissiveIntensity"] = intensity
        if texture:
            m["Textures"] = {"Diffuse": {"Path": texture, "RenderMode": "Opaque"}}
        return m

    def piece(name, position, rotation=(0, 0, 0), scale=(1, 1, 1), mesh="Cube", mat=None, collider="box",
              mass=None, parent=None, extra=(), shadows=True):
        """One entity: a primitive mesh, a collider ("box", "sphere", "convex" or None) and, with a
        mass, a dynamic rigidbody; static otherwise."""
        guid = f"d720{len(entities):012x}"
        components = [{"Type": "Transform", "Position": list(position), "Rotation": list(rotation), "Scale": list(scale)}]
        if mesh:
            m = {"Type": "Mesh", "MeshType": mesh, "Material": mat or material((0.5, 0.5, 0.5))}
            if not shadows:
                m["CastShadows"] = False
            components.append(m)
        if collider == "box":
            components.append({"Type": "BoxCollider", "Size": [2, 2, 2]})
        elif collider == "sphere":
            components.append({"Type": "SphereCollider", "Radius": 1.0, "Restitution": 0.2})
        elif collider == "convex":
            components.append({"Type": "MeshCollider", "Convex": True})
        if mass is not None:
            components.append({"Type": "Rigidbody", "Mass": mass})
        components.extend(extra)
        record = {"GUID": guid, "Name": name, "DestroyOnLoad": True, "Components": components}
        if parent:
            record["Parent"] = parent
        entities.append(record)
        return guid

    def light(name, position, color, intensity, radius):
        return piece(name, position, mesh=None, collider=None, extra=[
            {"Type": "Light", "LightType": "Point", "Color": list(color), "Intensity": intensity, "Range": radius, "CastShadows": False}])

    def fire(name, position, radius=0.4, rate=40.0, parent=None):
        return piece(name, position, mesh=None, collider=None, parent=parent, extra=[
            {"Type": "ParticleSystem", "EmissionRate": rate, "Shape": "Sphere", "ShapeRadius": radius,
             "Lifetime": [0.35, 0.7], "Speed": [0.5, 1.5], "Size": [0.35, 0.6], "EndSize": 0.2, "Intensity": 9.0,
             "Gravity": -0.4, "NoiseStrength": 1.5, "StartColor": [1.0, 0.75, 0.3], "StartColor2": [1.0, 0.5, 0.15],
             "EndColor": [0.9, 0.15, 0.03], "EndAlpha": 0.0}])

    def slab(name, a, b, half_width, color, yaw, thickness=0.5, roughness=0.7):
        """A static slab whose top surface runs from a to b (points along the yaw heading: distance
        along it and height), half_width to each side."""
        (d0, y0), (d1, y1) = a, b
        run, rise = d1 - d0, y1 - y0
        length = math.hypot(run, rise)
        angle = math.atan2(rise, run)
        # The slab's centre sits thickness below the middle of the top surface.
        mid_d = (d0 + d1) / 2 + math.sin(angle) * thickness
        mid_y = (y0 + y1) / 2 - math.cos(angle) * thickness
        return mid_d, mid_y, (half_width, thickness, length / 2), -math.degrees(angle)

    def along(origin, yaw, distance, side=0.0):
        r = math.radians(yaw)
        return origin[0] + math.sin(r) * distance + math.cos(r) * side, origin[1] + math.cos(r) * distance - math.sin(r) * side

    def neon_arch(name, x, z, ground_y, yaw, half_width, color, height=9.0):
        r = math.radians(yaw)
        ax, az = math.cos(r), -math.sin(r)
        glow = material((0.1, 0.1, 0.1), 0.3, 0.6, color, 5.0)
        frame = material((0.12, 0.1, 0.12), 0.35, 0.8)
        for side in (-1, 1):
            px, pz = x + ax * half_width * side, z + az * half_width * side
            piece(f"{name} Pillar {side}", (px, ground_y + height / 2, pz), (0, yaw, 0), (0.5, height / 2, 0.5), mat=frame)
            piece(f"{name} Pillar Glow {side}", (px, ground_y + height / 2, pz), (0, yaw, 0), (0.56, height / 2 - 0.4, 0.1),
                  mat=glow, collider=None, shadows=False)
        piece(f"{name} Beam", (x, ground_y + height + 0.5, z), (0, yaw, 0), (half_width + 0.6, 0.6, 0.45), mat=frame, collider=None)
        piece(f"{name} Beam Glow", (x, ground_y + height + 0.5, z), (0, yaw, 0), (half_width + 0.3, 0.3, 0.5),
              mat=glow, collider=None, shadows=False)
        bulb = material((1.0, 0.9, 0.6), 0.3, 0.0, (1.0, 0.8, 0.35), 8.0)
        count = int(half_width * 2)
        for k in range(count + 1):
            offset = -half_width + k * (2 * half_width / count)
            piece(f"{name} Bulb {k}", (x + ax * offset, ground_y + height + 1.25, z + az * offset), scale=(0.18, 0.18, 0.18),
                  mesh="Sphere", mat=bulb, collider=None, shadows=False)
        # A giant tarot card on top.
        piece(f"{name} Card", (x, ground_y + height + 3.4, z), (0, yaw, 0), (1.3, 2.0, 0.08),
              mat=material((1, 1, 1), 0.5, 0.0, (0.35, 0.25, 0.5), 0.6, "Assets/UI/Drive/Tarot/Back.png"), collider=None)
        light(f"{name} Light", (x, ground_y + height - 1.0, z), color, 30.0, 16.0)

    barrel_red = material((0.78, 0.07, 0.04), 0.35, 0.4)
    barrel_band = material((0.95, 0.75, 0.05), 0.4, 0.2, (1.0, 0.7, 0.0), 0.6)

    def barrel(x, z, ground_y):
        root = piece(f"Fuel Drum {x:.1f},{z:.1f}", (x, ground_y + 0.66, z), (0, rng.uniform(0, 360), 0), (0.45, 0.65, 0.45),
                     mesh="Cylinder", mat=barrel_red, collider="convex", mass=3.0,
                     extra=[{"Type": "ScriptComponent", "ScriptName": "ExplosiveBarrel", "ScriptFields": "{}"}])
        piece("Fuel Drum Band", (0, 0.45, 0), scale=(1.02, 0.12, 1.02), mesh="Cylinder", mat=barrel_band, collider=None, parent=root)

    # ---- Casino plaza (the pad at 10, -145) -------------------------------------------------------
    cx, cz = 10.0, -145.0
    piece("Casino Floor", (cx, -0.45, cz), scale=(26, 0.5, 20), mat=material((0.28, 0.04, 0.07), 0.35))
    trim = material((0.9, 0.7, 0.25), 0.25, 1.0, (1.0, 0.7, 0.2), 1.5)
    for name, x, z, sx, sz in (("N", cx, cz + 19.6, 26, 0.25), ("S", cx, cz - 19.6, 26, 0.25),
                               ("E", cx + 25.6, cz, 0.25, 20), ("W", cx - 25.6, cz, 0.25, 20)):
        piece(f"Casino Trim {name}", (x, 0.02, z), scale=(sx, 0.08, sz), mat=trim, collider=None, shadows=False)
    neon_arch("Casino Arch", cx, cz + 21.0, 0.05, 0, 7.0, (1.0, 0.2, 0.6))
    for k, (color, (px, pz)) in enumerate(zip([(1.0, 0.2, 0.6), (1.0, 0.75, 0.2), (0.2, 0.8, 1.0), (0.6, 0.3, 1.0)],
                                              [(-14, -16), (34, -16), (34, 16), (-14, 16)])):
        x, z = cx + px - 10, cz + pz  # posts at the plaza's corners
        piece(f"Casino Post {k}", (x, 2.0, z), scale=(0.25, 2.0, 0.25), mesh="Cylinder", mat=material((0.1, 0.1, 0.1), 0.3, 0.8))
        piece(f"Casino Post Lamp {k}", (x, 4.3, z), scale=(0.45, 0.45, 0.45), mesh="Sphere",
              mat=material(color, 0.3, 0.0, color, 6.0), collider=None, shadows=False)
        light(f"Casino Post Light {k}", (x, 4.3, z), color, 18.0, 16.0)

    # Giant dice, pips on every face (opposite faces add up to seven).
    pips = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)], 6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]}
    faces = {1: ((0, 1, 0), (1, 0, 0), (0, 0, 1)), 6: ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             2: ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 5: ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
             3: ((0, 0, 1), (1, 0, 0), (0, 1, 0)), 4: ((0, 0, -1), (1, 0, 0), (0, 1, 0))}
    pip_mat = material((0.03, 0.03, 0.03), 0.2)
    for k, (dx, dz) in enumerate([(-20, 10), (-12, -10), (-7, 5), (-20, -4)]):
        size = 1.5
        die = piece(f"Giant Die {k}", (cx + dx, 0.05 + size, cz + dz), (0, rng.uniform(0, 90), 0), (size, size, size),
                    mat=material((0.95, 0.93, 0.88), 0.25), mass=40.0)
        for value, (normal, u, v) in faces.items():
            for a, b in pips[value]:
                position = [normal[i] * 1.0 + (u[i] * a + v[i] * b) * 0.5 for i in range(3)]
                flat = [0.04 if normal[i] else 0.17 for i in range(3)]
                piece("Pip", position, scale=flat, mesh="Sphere", mat=pip_mat, collider=None, parent=die, shadows=False)

    # Poker chip towers.
    chip_colors = [(0.75, 0.06, 0.06), (0.08, 0.2, 0.7), (0.06, 0.06, 0.07), (0.05, 0.45, 0.15), (0.45, 0.1, 0.55)]
    for k, (dx, dz) in enumerate([(-22, -14), (-16, 14), (-4, 14), (-4, -14), (-14, 2), (22, 15)]):
        color = chip_colors[k % len(chip_colors)]
        for level in range(12):
            piece(f"Chip {k}-{level}", (cx + dx, 0.05 + 0.15 + level * 0.305, cz + dz), (0, rng.uniform(0, 360), 0), (1.4, 0.15, 1.4),
                  mesh="Cylinder", mat=material(color if level % 2 == 0 else (0.92, 0.9, 0.85), 0.35), collider="convex", mass=4.0)

    # Giant tarot cards stood on edge around a spiral: knock the first one over.
    card = material((1, 1, 1), 0.55, 0.0, None, 0.0, "Assets/UI/Drive/Tarot/Back.png")
    spiral = (cx + 10, cz - 2)
    for k in range(34):
        angle = k * 0.21
        radius = 13.0 - k * 0.22
        x, z = spiral[0] + math.cos(angle) * radius, spiral[1] + math.sin(angle) * radius
        piece(f"Giant Card {k}", (x, 0.05 + 1.6, z), (0, -math.degrees(angle), 0), (1.0, 1.6, 0.06), mat=card, mass=3.0)

    # ---- Mega ramp (east along z = 150 from x = -105) ----------------------------------------------
    pad_y = 1.0
    origin, yaw, rz = (-105.0, 150.0), 90.0, 150.0
    deck = material((0.2, 0.22, 0.25), 0.6, 0.3)
    stripe = material((1.0, 0.45, 0.05), 0.4, 0.0, (1.0, 0.45, 0.05), 2.5)
    sections = [((0, pad_y + 0.03), (34, pad_y + 7.85)), ((34, pad_y + 7.85), (40, pad_y + 11.05))]
    for k, (a, b) in enumerate(sections):
        d, y, scale, pitch = slab("Mega Ramp", a, b, 4.0, None, yaw)
        x, z = along(origin, yaw, d)
        piece(f"Mega Ramp {k}", (x, y, z), (pitch, yaw, 0), scale, mat=deck)
        for side in (-1, 1):
            sx, sz = along(origin, yaw, d, side * 3.75)
            piece(f"Mega Ramp Stripe {k} {side}", (sx, y + 0.02, sz), (pitch, yaw, 0), (0.12, scale[1], scale[2]),
                  mat=stripe, collider=None, shadows=False)
    # Supports under the climb, and a block under the kicker.
    for k in range(5):
        dist = 6 + k * 6.5
        top = pad_y + 7.85 * dist / 34 - 1.1
        for side in (-1, 1):
            x, z = along(origin, yaw, dist, side * 3.3)
            if top > pad_y + 0.3:
                piece(f"Mega Ramp Support {k} {side}", (x, (pad_y + top) / 2, z), scale=(0.35, (top - pad_y) / 2, 0.35),
                      mat=material((0.3, 0.3, 0.32), 0.5, 0.7))
    x, z = along(origin, yaw, 37.5)
    piece("Mega Ramp Kicker Block", (x, pad_y + 4.0, z), (0, yaw, 0), (3.6, 4.0, 2.4), mat=material((0.3, 0.3, 0.32), 0.5, 0.7))
    # Floodlight pylons either side of the lip.
    for side in (-1, 1):
        x, z = along(origin, yaw, 40, side * 7.0)
        piece(f"Mega Ramp Pylon {side}", (x, pad_y + 9, z), scale=(0.3, 9, 0.3), mesh="Cylinder", mat=material((0.15, 0.15, 0.16), 0.4, 0.8))
        piece(f"Mega Ramp Pylon Lamp {side}", (x, pad_y + 18.4, z), scale=(0.9, 0.5, 0.9), mat=material((1, 1, 1), 0.3, 0.0, (1.0, 0.95, 0.8), 10.0),
              collider=None, shadows=False)
        light(f"Mega Ramp Pylon Light {side}", (x, pad_y + 17.5, z), (1.0, 0.95, 0.8), 40.0, 24.0)
    # The ring of fire over the gap (the ring's plane faces along the run).
    ring_d, ring_y, ring_r = 50.0, pad_y + 15.0, 4.5
    rx, rz2 = along(origin, yaw, ring_d)
    ember = material((1.0, 0.4, 0.1), 0.5, 0.0, (1.0, 0.45, 0.1), 6.0)
    for k in range(16):
        a = k / 16 * math.tau
        piece(f"Fire Ring {k}", (rx, ring_y + math.cos(a) * ring_r, rz2 + math.sin(a) * ring_r), (math.degrees(a), 0, 0),
              (0.22, 0.22, 0.95), mat=ember, collider=None, shadows=False)
        if k % 2 == 0:
            fire(f"Fire Ring Flame {k}", (rx, ring_y + math.cos(a) * ring_r, rz2 + math.sin(a) * ring_r))
    light("Fire Ring Light", (rx, ring_y, rz2), (1.0, 0.5, 0.15), 45.0, 16.0)
    # The landing: a deck 14 m past the lip and a long run down. Fall short and you hit its face.
    x, z = along(origin, yaw, 57.0)
    piece("Mega Ramp Landing Deck", (x, pad_y + 4.0, z), (0, yaw, 0), (4.0, 4.0, 3.0), mat=deck)
    d, y, scale, pitch = slab("Landing", (60.0, pad_y + 8.0), (100.0, pad_y + 0.03), 4.0, None, yaw)
    x, z = along(origin, yaw, d)
    piece("Mega Ramp Landing", (x, y, z), (pitch, yaw, 0), scale, mat=deck)
    # Drums in the pit, and a row waiting at the end of the run.
    for i in range(3):
        for j in range(3):
            barrel(*along(origin, yaw, 44.5 + i * 3.2, (j - 1) * 2.4), pad_y)
    for j in range(7):
        barrel(*along(origin, yaw, 124.0, (j - 3) * 1.25), pad_y)

    # ---- Bowling alley (x = 155, rolling toward -z) ----------------------------------------------------
    bx, lane_y = 155.0, -1.0
    piece("Bowling Lane", (bx, lane_y - 0.45, -45), scale=(5, 0.5, 48), mat=material((0.72, 0.5, 0.28), 0.2))
    gutter = material((0.15, 0.15, 0.17), 0.3, 0.8)
    for side in (-1, 1):
        piece(f"Bowling Gutter {side}", (bx + side * 5.2, lane_y + 0.1, -45), scale=(0.2, 0.15, 48), mat=gutter)
    arrows = material((0.1, 0.4, 1.0), 0.3, 0.0, (0.2, 0.5, 1.0), 3.0)
    for k in range(7):
        piece(f"Bowling Arrow {k}", (bx + (k - 3) * 1.2, lane_y + 0.06, -30 + abs(k - 3) * 1.5), (0, 45, 0), (0.25, 0.02, 0.25),
              mat=arrows, collider=None, shadows=False)
    piece("Bowling Foul Line", (bx, lane_y + 0.06, -8), scale=(5, 0.02, 0.12), mat=material((1, 0.2, 0.1), 0.3, 0.0, (1, 0.2, 0.1), 3.0),
          collider=None, shadows=False)
    neon_arch("Bowling Arch", bx, 2.0, lane_y + 0.05, 0, 6.5, (0.2, 0.6, 1.0))
    piece("Bowling Ball", (bx, lane_y + 2.05, -12), scale=(2, 2, 2), mesh="Sphere", mat=material((0.08, 0.1, 0.45), 0.08, 0.3),
          collider="sphere", mass=30.0)
    pin = material((0.96, 0.95, 0.92), 0.25)
    band = material((0.8, 0.05, 0.05), 0.3)
    for row in range(4):
        for i in range(row + 1):
            root = piece(f"Bowling Pin {row}-{i}", (bx + (i - row / 2) * 3.0, lane_y + 2.45, -72 - row * 2.6), scale=(1.6, 2.4, 1.6),
                         mesh="Capsule", mat=pin, collider="convex", mass=6.0)
            for y in (0.22, 0.32):
                piece("Pin Band", (0, y, 0), scale=(0.52, 0.03, 0.52), mesh="Cylinder", mat=band, collider=None, parent=root, shadows=False)
    for k, z in enumerate((-20, -45, -70)):
        light(f"Bowling Light {k}", (bx, lane_y + 7, z), (0.6, 0.75, 1.0), 25.0, 18.0)

    # ---- Fuel depot (-152, -60): tanks and drums; one bang sets the lot off ----------------------------
    fx, fz = -152.0, -60.0
    piece("Depot Floor", (fx, -0.45, fz), scale=(13, 0.5, 15), mat=material((0.42, 0.42, 0.4), 0.85))
    for k, dz in enumerate((-9, 9)):
        tank = piece(f"Fuel Tank {k}", (fx - 7, 3.55, fz + dz), scale=(3.0, 3.5, 3.0), mesh="Cylinder", mat=material((0.9, 0.9, 0.88), 0.3, 0.5),
                     collider="convex")
        piece("Fuel Tank Band", (0, 0.3, 0), scale=(1.01, 0.12, 1.01), mesh="Cylinder", mat=barrel_red, collider=None, parent=tank)
    for i in range(5):
        for j in range(6):
            barrel(fx + 1 + i * 1.3, fz - 3.25 + j * 1.3, 0.05)
    # A trail of drums leading out of the depot like a fuse.
    for k in range(6):
        barrel(fx + 10 + k * 3.2, fz + math.sin(k * 0.8) * 2.0, 0.05 if k < 2 else height(fx + 10 + k * 3.2, fz))
    light("Depot Light", (fx, 6, fz), (1.0, 0.6, 0.3), 25.0, 22.0)

    # ---- Stone circle (-150, 160) with a tarot card floating over the altar ---------------------------
    sx, sz, stone_y = -150.0, 160.0, 1.0
    for k in range(12):
        a = k / 12 * math.tau
        tint = rng.uniform(-0.05, 0.05)
        piece(f"Standing Stone {k}", (sx + math.cos(a) * 11, stone_y + 2.6, sz + math.sin(a) * 11), (0, 90 - math.degrees(a), 0),
              (1.4, 2.6, 0.55), mat=material((0.5 + tint, 0.49 + tint, 0.46 + tint), 0.95), mass=60.0)
    for k in range(6):
        a = (2 * k + 0.5) / 12 * math.tau
        piece(f"Lintel {k}", (sx + math.cos(a) * 10.9, stone_y + 5.2 + 0.45, sz + math.sin(a) * 10.9), (0, 90 - math.degrees(a), 0),
              (3.1, 0.45, 0.55), mat=material((0.47, 0.46, 0.43), 0.95), mass=30.0)
    piece("Altar", (sx, stone_y + 0.5, sz), scale=(1.8, 0.5, 1.1), mat=material((0.35, 0.34, 0.33), 0.9))
    piece("Altar Card", (sx, stone_y + 3.2, sz), (0, 30, 0), (0.8, 1.25, 0.05),
          mat=material((1, 1, 1), 0.4, 0.0, (0.5, 0.3, 1.0), 1.2, "Assets/UI/Drive/Tarot/Back.png"), collider=None)
    light("Altar Light", (sx, stone_y + 3.2, sz), (0.6, 0.3, 1.0), 30.0, 14.0)
    return entities


def add_props(scene):
    data = json.loads(scene.read_text())
    kept = [e for e in data["Entities"] if not e["GUID"].startswith(("d71f", "d720"))]
    props = build_props()
    setpieces = build_setpieces()
    data["Entities"] = kept + props + setpieces
    scene.write_text(json.dumps(data, indent=4) + "\n")
    print(f"{scene}: {len(props)} physics props, {len(setpieces)} set piece entities")


def main():
    project = Path(__file__).resolve().parents[1]
    scene = project / "Assets/Scenes/DriveTest.lvl"
    if "--props-only" in sys.argv:
        build_terrain(project)
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
    # Tarot deck on the dash (TarotDeck.cs): Q draws a card, each a weapon, blessing or curse.
    entities.extend(tarot_deck(body))

    # Roadside slot machine (SlotMachine.cs, reels in Assets/UI/Drive/Slots.rml): E to spin, three
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
