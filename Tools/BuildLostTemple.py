#!/usr/bin/env python3
"""Rebuild the Lost Temple demo scene and its shader graphs.

    python3 Tools/BuildLostTemple.py            # scene + graphs
    python3 Tools/BuildLostTemple.py --graphs   # graphs only

Writes Assets/Scenes/LostTemple.lvl, Assets/Scripts/LostTemple/LostTempleShots.cs and
Assets/ShaderGraphs/LostTemple/*.shadergraph, overwriting them, so save custom edits elsewhere
first. A changed graph needs its .sg/ sources regenerated afterwards: save it in Havana, or run the
project-graph test with ME_SHADERGRAPH_UPDATE=1 (see Assets/Scenes/LostTemple.md). Python 3, no
packages.

Synty models keep their original import settings; every part gets an explicit material here
(the FBXs reference textures from other packs by old absolute paths). Part paths come from
Tools/LostTempleParts.json and the explorers' skeletons from Tools/LostTempleRigs.json, both
recorded by loading the models in Havana.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import LostTempleGraphs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCENE = "Assets/Scenes/LostTemple.lvl"
GRAPHS = "Assets/ShaderGraphs/LostTemple/"
KIT = "Assets/Models/Synty/ExplorerKit/"
GEN = KIT + "Models/"
FBX = KIT + "FBX/"
TEX = KIT + "Textures/"
ATLAS = TEX + "Alts/Generic_01_A.png"
EXPLORER = TEX + "PolygonExplorers_Texture_01_A.png"
PARTS = json.loads((ROOT / "Tools/LostTempleParts.json").read_text())

rng = random.Random(1999)


def guid(name):
    return hashlib.sha256(("lost-temple/" + name).encode()).hexdigest()[:16]


def r3(values):
    return [round(float(v), 4) for v in values]


def quat(yaw=0.0, pitch=0.0, roll=0.0):
    """Yaw about +Y, then pitch about +X (positive looks down), then roll about +Z. Degrees."""
    def axis(ax, deg):
        h = math.radians(deg) / 2
        s = math.sin(h)
        return [ax[0] * s, ax[1] * s, ax[2] * s, math.cos(h)]

    def mul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return [aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw,
                aw * bw - ax * bx - ay * by - az * bz]
    q = mul(axis((0, 1, 0), yaw), mul(axis((1, 0, 0), pitch), axis((0, 0, 1), roll)))
    return [round(v, 6) for v in q]


def look_angles(src, dst):
    """Yaw/pitch (degrees) that point +Z from src at dst."""
    dx, dy, dz = dst[0] - src[0], dst[1] - src[1], dst[2] - src[2]
    yaw = math.degrees(math.atan2(dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return yaw, pitch


def rotate_y(point, yaw):
    a = math.radians(yaw)
    x, y, z = point
    return [x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a)]


# ---------------------------------------------------------------------------------------------
# Components


def transform(pos=(0, 0, 0), yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    return {"Type": "Transform", "Position": r3(pos), "Rotation": quat(yaw, pitch, roll), "Scale": r3(scale)}


def standard(texture=None, color=(1, 1, 1), roughness=0.8, metallic=0.0, emissive=(0, 0, 0), emissive_intensity=1.0,
             opacity=1.0, transparent=False, faces=0, normal=None, tiling=(1, 1)):
    material = {"Type": "StandardMaterial", "DiffuseColor": r3(color), "Roughness": roughness, "Metallic": metallic,
                "EmissiveColor": r3(emissive), "EmissiveIntensity": emissive_intensity, "Opacity": opacity,
                "RenderMode": 1 if transparent else 0, "BlendMode": 0, "FaceMode": faces, "Tiling": r3(tiling), "Textures": {}}
    if texture:
        material["Textures"]["Diffuse"] = {"Path": texture, "RenderMode": "Opaque"}
    if normal:
        material["Textures"]["Normal"] = {"Path": normal, "RenderMode": "Opaque"}
    return material


def graph(name, params=None, textures=None):
    return {"Type": "ShaderGraphMaterial", "Graph": GRAPHS + name + ".shadergraph",
            "Params": {k: (list(v) + [0.0] * (4 - len(v)) if isinstance(v, (list, tuple)) else [v, 0.0, 0.0, 0.0])
                       for k, v in (params or {}).items()},
            "Textures": textures or {}}


def mesh(shape, material, shadows=True):
    return {"Type": "Mesh", "MeshType": shape, "CastShadows": shadows, "Material": material}


def model(path, material, shadows=True):
    key = path.split("/")[-1][:-4]
    parts = {}
    for index, part in enumerate(PARTS[key]):
        chosen = material(index) if callable(material) else material
        parts[part] = {"Type": "Mesh", "MeshType": "Model", "CastShadows": shadows, "Material": chosen}
    return {"Type": "Model", "ModelPath": path, "Compact": True, "Parts": parts}


def light(kind, color, intensity, range_=10.0, shadows=False, inner=20.0, outer=32.0, **extra):
    data = {"Type": "Light", "LightType": kind, "Color": r3(color), "Intensity": intensity, "Range": range_,
            "CastShadows": shadows, "InnerConeAngle": inner, "OuterConeAngle": outer, "ShadowBias": 0.6, "ShadowNormalBias": 2.0}
    data.update(extra)
    return data


def particles(**fields):
    data = {"Type": "ParticleSystem", "Looping": True, "Duration": 5.0, "EmissionRate": 20.0, "BurstCount": 0,
            "MaxParticles": 400, "SimulationSpace": "World", "Shape": "Sphere", "ShapeRadius": 0.2, "ConeAngle": 15.0,
            "BoxSize": [1.0, 1.0, 1.0], "EmitFromShell": False, "Lifetime": [1.0, 2.0], "Speed": [0.2, 0.5],
            "Size": [0.1, 0.2], "Rotation": [0.0, 360.0], "AngularVelocity": [-30.0, 30.0], "StartColor": [1, 1, 1],
            "StartColor2": [1, 1, 1], "StartAlpha": 1.0, "Intensity": 1.0, "EndSize": 1.0, "EndColor": [1, 1, 1],
            "EndAlpha": 0.0, "FadeIn": 0.1, "Gravity": 0.0, "Drag": 0.0, "NoiseStrength": 0.0, "NoiseFrequency": 1.0,
            "Texture": "", "Blend": "Additive", "Alignment": "Billboard", "StretchFactor": 0.1, "FlipbookColumns": 1,
            "FlipbookRows": 1, "FlipbookFps": 0.0, "SoftParticleDistance": 0.3, "Graph": "", "Lit": False}
    for key, value in fields.items():
        data[key] = r3(value) if isinstance(value, (list, tuple)) else value
    return data


def decal(size, albedo="", graph_name="", color=(1, 1, 1), normal="", roughness=0.6, metallic=0.0, opacity=1.0,
          emissive=(1, 1, 1), emissive_intensity=0.0, sort=0, angle_fade=70.0, params=None):
    data = {"Type": "Decal", "Albedo": albedo, "NormalMap": normal, "Color": r3(color), "Size": r3(size), "Roughness": roughness,
            "Metallic": metallic, "Opacity": opacity, "EmissiveColor": r3(emissive), "EmissiveIntensity": emissive_intensity,
            "NormalStrength": 1.0, "SortOrder": sort, "AngleFade": angle_fade, "AngleFadeWidth": 20.0,
            "Graph": GRAPHS + graph_name + ".shadergraph" if graph_name else ""}
    if params:
        data["GraphParams"] = {"Params": {k: list(v) + [0.0] * (4 - len(v)) if isinstance(v, (list, tuple)) else [v, 0.0, 0.0, 0.0]
                                          for k, v in params.items()}, "Textures": {}}
    return data


def script(name, **fields):
    return {"Type": "ScriptComponent", "ScriptName": name, "ScriptFields": json.dumps(fields)}


# ---------------------------------------------------------------------------------------------
# Scene graph


class Scene:
    def __init__(self):
        self.entities = []
        self.names = {}

    def entity(self, name, components, parent=None):
        count = self.names.get(name, 0)
        self.names[name] = count + 1
        entity = {"Name": name, "GUID": guid(name + "#" + str(count)), "Components": components}
        if parent:
            entity["Parent"] = parent["GUID"]
        self.entities.append(entity)
        return entity

    def group(self, name, pos=(0, 0, 0), yaw=0.0, parent=None):
        return self.entity(name, [transform(pos, yaw)], parent)


def kit_material(key, tint=(1, 1, 1), roughness=0.8):
    texture = EXPLORER if key.startswith(("SM_Prop_", "SM_Wep_", "SM_Chr_", "SM_Veh_", "SK_")) else ATLAS
    return standard(texture, tint, roughness)


def place(scene, name, key, pos, yaw=0.0, scale=1.0, material=None, parent=None, shadows=True, pitch=0.0, roll=0.0, extra=()):
    folder = FBX if key.startswith(("SM_Prop_", "SM_Wep_", "SM_Chr_", "SM_Veh_", "SK_")) else GEN
    if key.startswith("SM_Bld_Base"):
        folder = GEN + "Base/"
    path = folder + key + ".fbx"
    return scene.entity(name, [transform(pos, yaw, pitch, roll, scale), model(path, material or kit_material(key), shadows)] + list(extra), parent)


def stone(**params):
    values = {"Stone Tint": [0.66, 0.65, 0.6], "Moss Amount": 0.5, "Tile": 0.35, "Roughness": 0.85}
    values.update({k.replace("_", " "): v for k, v in params.items()})
    return graph("AncientStone", values)


def foliage(sway_height=5.0, strength=0.08, tint=(0.68, 1.0, 0.5), speed=1.3, cutout=False):
    return graph("FoliageCutout" if cutout else "Foliage",
                 {"Sway Height": sway_height, "Wind Strength": strength, "Tint": list(tint), "Wind Speed": speed})


# ---------------------------------------------------------------------------------------------
# Layout constants (metres; +X east, +Y up, +Z north). A December sun sets in the west-south-west,
# ten degrees up: it rakes across the temple's stair face from the left of the hero shot (which
# looks north) and throws the western trees' shadows across the clearing.

TEMPLE = (-5.0, 0.0, 20.0)
TEMPLE_YAW = 5.0
POOL = (13.0, 0.0, 25.0)
POOL_RADIUS = 6.0
WATER_Y = 0.22
CAMP = (11.0, 0.0, 0.0)
TIERS = [(16.0, 1.9), (13.0, 1.9), (10.0, 1.9), (7.2, 1.2)]
TEMPLE_TOP = sum(height for _, height in TIERS)


def temple_point(local):
    """A point given in the temple's frame, in world space."""
    x, y, z = rotate_y(local, TEMPLE_YAW)
    return (TEMPLE[0] + x, TEMPLE[1] + y, TEMPLE[2] + z)


# LostTempleCamera's shots (written to LostTempleShots.cs): name, camera position, look-at point.
SHOTS = [
    ("the camp and the temple, the sun raking in from the left", (12.0, 2.4, -9.0), (-3.5, 5.5, 20.0)),
    ("the camp fire and the map table", (6.5, 1.5, -5.5), (11.5, 0.9, 1.5)),
    ("up the torch-lit stairs", temple_point((-1.8, 1.1, -21.0)), temple_point((0.0, TEMPLE_TOP + 1.4, -1.7))),
    ("the shrine door and the idol", temple_point((0.9, TEMPLE_TOP + 1.6, -6.0)), temple_point((0.0, TEMPLE_TOP + 1.2, 1.5))),
    ("the plunge pool and the falls", (7.0, 2.6, 11.5), (13.5, 3.5, 31.0)),
    ("high over the gorge", (28.0, 16.0, -20.0), (-2.0, 2.0, 18.0)),
    ("into the low sun, across the pool to the temple", (22.0, 3.2, 21.0), (-30.0, 6.0, 19.0)),
]
HERO_CAMERA, HERO_TARGET = SHOTS[0][1], SHOTS[0][2]
# Where the ground-level shots stand (kept clear of undergrowth).
SHOT_CAMERAS = [shot[1] for shot in SHOTS if shot[1][1] < 10.0]


def write_shots():
    def vec(v):
        return "new Vector3(%s)" % ", ".join("%.2ff" % c for c in v)
    lines = ["using ScriptCore;", "",
             "// Generated by Tools/BuildLostTemple.py: where LostTempleCamera's shots stand and look.",
             "public static class LostTempleShots", "{",
             "    public static readonly Vector3[] From =", "    {"]
    lines += ["        %s, // %d %s" % (vec(shot[1]), i + 1, shot[0]) for i, shot in enumerate(SHOTS)]
    lines += ["    };", "", "    public static readonly Vector3[] To =", "    {"]
    lines += ["        %s," % vec(shot[2]) for shot in SHOTS]
    lines += ["    };", "}", ""]
    # Only rewrite on change: a rewritten script makes a running editor hot-reload the scripts.
    path = ROOT / "Assets/Scripts/LostTemple/LostTempleShots.cs"
    text = "\n".join(lines)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def build_camera(scene):
    yaw, pitch = look_angles(HERO_CAMERA, HERO_TARGET)
    sky = {"CloudAltitude": 1800.0, "CloudCoverage": 0.42, "CloudDensity": 0.9, "CloudThickness": 2200.0,
           "Latitude": 14.0, "Month": 11, "MoonAscendingNode": 124.68, "MoonBrightness": 1.0, "MoonOrbitInclination": 5.145,
           "MoonPhase": 0.35, "MoonSize": 2.2, "StarBrightness": 1.0, "SunSize": 2.4, "Time": 17.2, "TimeScale": 0.0,
           "Turbidity": 3.2, "WindDirection": 70.0, "WindSpeed": 6.0}
    post = {"Type": "PostProcess", "Tonemapper": "ACES", "ExposureCompensation": 0.35, "AutoExposure": True,
            "AutoExposureMinEV": -1.0, "AutoExposureMaxEV": 2.5, "AutoExposureSpeed": 1.5,
            "Bloom": True, "BloomThreshold": 1.0, "BloomIntensity": 0.12, "BloomRadius": 1.0,
            "AmbientOcclusion": True, "AORadius": 0.7, "AOIntensity": 1.0,
            "FXAA": False, "TemporalAA": True, "TemporalSharpness": 0.35,
            "Fog": True, "FogColor": [0.24, 0.23, 0.25], "FogDensity": 0.026, "FogHeight": 0.0, "FogHeightFalloff": 0.16,
            "FogStartDistance": 1.0, "FogMaxOpacity": 0.92, "FogSunIntensity": 1.8, "FogAnisotropy": 0.5,
            "VolumetricFog": True, "VolumetricDistance": 70.0, "VolumetricSteps": 48,
            "Saturation": 1.08, "Contrast": 1.1, "Temperature": 0.02, "Tint": 0.0, "Gamma": 1.0, "Lift": 0.0, "Gain": 1.0,
            "VignetteIntensity": 0.32, "VignetteSmoothness": 0.65,
            "Graphs": [GRAPHS + "LensDirt.shadergraph"]}
    camera = {"Type": "Camera", "ClearType": "Procedural", "ClearColor": [0.3, 0.35, 0.45], "Far": 900.0, "Near": 0.1,
              "FieldOfView": 52.0, "IsCurrent": True, "Projection": "Perspective", "OrthographicSize": 5.0, "ProceduralSky": sky}
    scene.entity("Main Camera", [transform(HERO_CAMERA, yaw, pitch), camera, post,
                                 script("LostTempleCamera")])


def build_sun(scene):
    scene.entity("Sun", [transform((0, 20, 0), -70.0, 12.0),
                         light("Directional", (1.0, 0.8, 0.58), 8.0, shadows=True, DirectionalSource="Automatic",
                               ShadowDistance=80.0, ShadowBias=0.5, ShadowNormalBias=2.5)])


def build_ground(scene):
    ground = scene.group("Ground")
    floor = graph("JungleFloor", {"Pool Center": list(POOL), "Pool Radius": POOL_RADIUS, "Tile": 0.22, "Grass Amount": 0.72})
    # A 160 m square (the plane primitive spans -1..1).
    scene.entity("Jungle Floor", [transform((0, 0, 8), scale=(80, 1, 80)), mesh("Plane", floor)], ground)


def build_temple(scene):
    temple = scene.group("Temple", TEMPLE, TEMPLE_YAW)
    blocks = scene.group("Pyramid", parent=temple)

    def carved(**params):
        values = {"Masonry": 1.0, "Frame_Yaw": TEMPLE_YAW, "Block_Size": [1.25, 0.425]}
        values.update(params)
        return stone(**values)
    stone_main = carved()
    stone_steps = carved(Moss_Amount=0.35, Block_Size=[0.9, 6.9 / 18])

    def block(name, center, size, material=stone_main, yaw=0.0, pitch=0.0, roll=0.0, parent=blocks):
        # Primitives span -1..1, so scale by half the size in metres.
        return scene.entity(name, [transform(center, yaw, pitch, roll, [v / 2 for v in size]), mesh("Cube", material)], parent)

    # Four tiers and the shrine on top; the stair runs up the front (-Z) face.
    tiers = TIERS
    y = 0.0
    for index, (size, height) in enumerate(tiers):
        block("Tier %d" % (index + 1), (0, y + height / 2, 0), (size, height, size))
        # A cornice lip at each tier's top edge.
        block("Tier %d Cornice" % (index + 1), (0, y + height - 0.12, 0), (size + 0.35, 0.24, size + 0.35), carved(Moss_Amount=0.7, Block_Size=[0.8, 0.24]))
        y += height
    top = y
    steps = 18
    front = -tiers[0][0] / 2 - 4.5
    back = -tiers[-1][0] / 2 + 0.2
    rise = top / steps
    run = (back - front) / steps
    stairs = scene.group("Stairs", parent=temple)
    for i in range(steps):
        z0 = front + run * i
        height = rise * (i + 1)
        block("Step %02d" % (i + 1), (0, height / 2, (z0 + back) / 2), (3.6, height, back - z0), stone_steps, parent=stairs)
    slope = math.degrees(math.atan2(top, back - front))
    length = math.hypot(top, back - front)
    for side in (-1, 1):
        block("Balustrade %s" % ("L" if side < 0 else "R"), (side * 2.15, top / 2 + 0.25, (front + back) / 2),
              (0.7, 0.9, length + 0.6), carved(Moss_Amount=0.65, Block_Size=[1.4, 0.9]), pitch=-slope, parent=stairs)

    # Shrine walls with a doorway facing the stairs, a lintel and a roof comb.
    shrine = scene.group("Shrine", (0, top, 0.6), parent=temple)
    wall = carved(Moss_Amount=0.3, Tile=0.45, Block_Size=[0.85, 0.34])
    sw, sd, sh, t = 5.2, 4.6, 3.4, 0.55
    block("Back Wall", (0, sh / 2, sd / 2 - t / 2), (sw, sh, t), wall, parent=shrine)
    block("Left Wall", (-sw / 2 + t / 2, sh / 2, 0), (t, sh, sd), wall, parent=shrine)
    block("Right Wall", (sw / 2 - t / 2, sh / 2, 0), (t, sh, sd), wall, parent=shrine)
    door = 1.7
    for side in (-1, 1):
        block("Front Wall %s" % ("L" if side < 0 else "R"), (side * (door / 2 + (sw / 2 - door / 2) / 2), sh / 2, -sd / 2 + t / 2),
              ((sw - door) / 2, sh, t), wall, parent=shrine)
    block("Lintel", (0, sh - 0.45, -sd / 2 + t / 2), (door + 0.1, 0.9, t + 0.1), wall, parent=shrine)
    block("Roof", (0, sh + 0.3, 0), (sw + 0.6, 0.6, sd + 0.6), carved(Moss_Amount=0.8, Block_Size=[0.9, 0.3]), parent=shrine)
    block("Roof Comb", (0, sh + 1.6, 0.9), (3.4, 2.0, 0.5), carved(Moss_Amount=0.55, Block_Size=[0.7, 0.5]), parent=shrine)
    block("Floor", (0, 0.05, 0), (sw - 0.2, 0.1, sd - 0.2), carved(Moss_Amount=0.0, Tile=0.6, Block_Size=[0.7, 0.7]), parent=shrine)

    # The idol on its plinth inside the shrine, lit from below by its own glow.
    place(scene, "Plinth", "SM_Prop_Plinth_01", (0, 0.1, 0.9), 0.0, 1.0, kit_material("SM_Prop_Plinth_01", roughness=0.6), shrine)
    place(scene, "Golden Idol", "SM_Prop_Idle_01", (0, 1.18, 0.9), 180.0, 2.3, graph("IdolGold"), shrine)
    scene.entity("Idol Light", [transform((0, 1.9, 0.2)), light("Point", (0.35, 1.0, 0.8), 9.0, 9.0, shadows=True),
                                script("Flicker", Strength=0.12, Speed=0.6, Seed=3.0)], shrine)
    scene.entity("Spirit Wisps", [transform((0, 1.5, 0.5)), particles(
        Graph=GRAPHS + "SpiritWisp.shadergraph", Shape="Sphere", ShapeRadius=1.3, EmissionRate=9.0, MaxParticles=80,
        Lifetime=[3.0, 5.5], Speed=[0.05, 0.25], Size=[0.12, 0.28], StartColor=[0.3, 1.0, 0.8], StartColor2=[0.5, 0.8, 1.0],
        EndColor=[0.4, 0.7, 1.0], Intensity=3.0, Gravity=-0.012, NoiseStrength=0.7, NoiseFrequency=0.6, FadeIn=0.3,
        EndSize=0.6)], shrine)
    scene.entity("Shrine Glow", [transform((0, 1.7, -sd / 2 + 0.2), 180.0),
                                 light("Rectangle", (1.0, 0.62, 0.3), 3.0, 7.0, RectangleWidth=door - 0.1, RectangleHeight=2.2)], shrine)
    scene.entity("Rune Wall", [transform((0, 1.7, sd / 2 - t - 0.05), 0.0, 0.0), decal((2.6, 2.6, 0.5), graph_name="RuneCircle",
                                                                                   params={"Glow Intensity": 5.0})], shrine)
    # Guardian statues at the foot of the stairs and pillars at the shrine door.
    for side in (-1, 1):
        x = side * 3.2
        place(scene, "Guardian Statue", "SM_Gen_Prop_Statue_05", (x, 0.0, front + 0.8), 180.0 + side * 8, 1.15, stone(Moss_Amount=0.45, Tile=0.9), temple)
        place(scene, "Shrine Pillar", "SM_Bld_Base_Pillar_02", (side * (door / 2 + 0.35), 0.0, -sd / 2 - 0.25), 0.0, (1.0, 1.08, 1.0),
              stone(Moss_Amount=0.4, Tile=0.8), shrine)
    ledge = (tiers[0][0] + tiers[1][0]) / 4  # halfway across the first tier's ledge
    for i, (x, z) in enumerate([(-ledge, -ledge), (ledge, -ledge), (-ledge, ledge), (ledge, ledge)]):
        place(scene, "Tier Statue", "SM_Gen_Prop_Statue_0%d" % (i % 4 + 1), (x, tiers[0][1], z),
              180.0 + math.degrees(math.atan2(x, -z)) * 0.0, 1.0, stone(Moss_Amount=0.55, Tile=0.9), temple)

    # Torches up the stair balustrades.
    torches = scene.group("Torches", parent=temple)
    for side in (-1, 1):
        for step in (5, 13):
            z = front + run * (step + 0.5)
            yb = rise * step + 0.95
            pos = (side * 2.15, yb, z)
            torch = scene.group("Torch", pos, parent=torches)
            place(scene, "Torch Body", "SM_Prop_Torch_01", (0, 0.4, 0), 0.0, 1.4, kit_material("SM_Prop_Torch_01"), torch)
            scene.entity("Torch Flame", [transform((0, 1.15, 0)), particles(
                Graph=GRAPHS + "Flame.shadergraph", Texture=TEX + "FX/Generic_Candle_Flame_01.png", Shape="Cone",
                ShapeRadius=0.06, ConeAngle=8.0, EmissionRate=26.0, Lifetime=[0.35, 0.6], Speed=[0.5, 0.9],
                Size=[0.22, 0.32], EndSize=0.4, StartColor=[1.0, 0.75, 0.4], StartColor2=[1.0, 0.6, 0.25],
                EndColor=[1.0, 0.35, 0.1], Intensity=2.5, NoiseStrength=0.6, NoiseFrequency=2.0, Rotation=[-10.0, 10.0],
                AngularVelocity=[-20.0, 20.0], SoftParticleDistance=0.1)], torch)
            scene.entity("Torch Light", [transform((0, 1.35, 0)), light("Point", (1.0, 0.55, 0.22), 6.0, 7.0),
                                         script("Flicker", Strength=0.3, Speed=1.2, Seed=float(step * side))], torch)
    # Gold offerings at the foot of the stairs, glowing inside the open chest.
    offerings = scene.group("Offerings", (0, 0, front - 0.6), parent=temple)
    gold = standard(None, (1.0, 0.76, 0.34), 0.22, 1.0)
    place(scene, "Treasure Chest", "SM_Gen_Prop_Chest_01", (1.0, 0.0, 0.0), 160.0, 1.0,
          lambda i: [standard(ATLAS, (1, 1, 1), 0.7), gold, standard(ATLAS, (1, 1, 1), 0.7)][i % 3], offerings)
    scene.entity("Chest Glow", [transform((1.0, 0.55, 0.0), 160.0), light("Box", (1.0, 0.72, 0.3), 2.5, 2.2, Size=[0.8, 0.2, 0.45])], offerings)
    for i, (key, x, z, yaw) in enumerate([("SM_Gen_Prop_Coin_Pile_01", -0.4, 0.3, 20), ("SM_Gen_Prop_Coin_Stack_02", 0.0, -0.5, 0),
                                          ("SM_Gen_Prop_Coin_Pile_02", 1.7, -0.6, 70), ("SM_Gen_Prop_Coin_Stack_01", -1.2, -0.2, 40),
                                          ("SM_Gen_Prop_Coin_Pile_01", 0.6, -1.1, 140)]):
        place(scene, "Gold", key, (x, 0.0, z), yaw, 1.0, gold, offerings)
    for i, (key, x, z) in enumerate([("SM_Gen_Prop_Pot_03", -2.3, 0.4), ("SM_Gen_Prop_Pot_01", -2.9, -0.3), ("SM_Gen_Prop_Pot_05", 2.6, 0.5),
                                     ("SM_Gen_Prop_Skull_01", 2.2, -0.9), ("SM_Gen_Prop_Pot_02", 3.2, 0.1)]):
        place(scene, "Offering", key, (x, 0.0, z), rng.uniform(0, 360), 1.0, kit_material(key, roughness=0.7), offerings)

    # Ruin dressing: fallen blocks, rubble and creepers.
    ruins = scene.group("Ruins", parent=temple)
    for i, (x, z, s, yaw, tilt) in enumerate([(-9.3, -3.5, 1.1, 20, 14), (9.4, 1.5, 0.9, 65, -9), (-9.6, 4.0, 0.7, 5, 22),
                                              (9.0, -9.2, 1.3, 40, 6), (-4.6, -9.6, 0.6, 75, 18)]):
        block("Fallen Block", (x, s * 0.4, z), (s * 1.6, s * 0.9, s * 1.1), stone(Moss_Amount=0.75), yaw, tilt, 0, ruins)
    for i, (key, x, z, yaw, scale) in enumerate([("SM_Gen_Env_Rock_03", -8.6, -6.0, 30, 1.0), ("SM_Gen_Env_Rock_Pebbles_05", 4.5, -9.0, 0, 1.2),
                                                 ("SM_Gen_Env_Rock_Pebbles_02", -3.9, -11.5, 50, 1.0), ("SM_Gen_Env_Rock_01", 8.8, -3.5, 120, 0.8)]):
        place(scene, "Rubble", key, (x, 0.0, z), yaw, scale, stone(Moss_Amount=0.6, Tile=0.9), ruins)
    # Creepers on the tier faces (half sizes 8, 6.5, 5 and 3.6 m), just proud of the stone.
    half = [size / 2 + 0.06 for size, _ in tiers]
    for i, (key, pos, yaw) in enumerate([("SM_Gen_Env_Ivy_08", (-4.2, 1.0, -half[0]), 180), ("SM_Gen_Env_Ivy_10", (4.4, 2.8, -half[1]), 180),
                                         ("SM_Gen_Env_Ivy_13", (-half[0], 1.1, 2.0), -90), ("SM_Gen_Env_Ivy_09", (half[1], 2.9, -1.0), 90),
                                         ("SM_Gen_Env_Ivy_11", (-half[2], 4.8, 1.0), -90), ("SM_Gen_Env_Ivy_08", (3.0, 6.2, -half[3]), 180)]):
        place(scene, "Creeper", key, pos, yaw, 1.0, foliage(2.0, 0.03, cutout=True), ruins)
    for i, (key, pos, yaw) in enumerate([("SM_Gen_Env_Vines_04", (-3.0, 5.6, -half[2] - 0.1), 180), ("SM_Gen_Env_Vines_05", (2.9, 6.8, -half[3] - 0.1), 180),
                                         ("SM_Gen_Env_Vines_03", (-1.4, top + sh + 0.4, -sd / 2 + 0.3), 180)]):
        place(scene, "Hanging Vines", key, pos, yaw, 1.2, foliage(-3.0, 0.05), ruins)
    scene.entity("Stair Rune", [transform((0, 0.0, front - 3.4), 0.0, 90.0), decal((4.6, 4.6, 1.0), graph_name="RuneCircle")], temple)
    # Primitives span -1..1: a 1.3 m wide, 9 m column standing on the rune circle.
    scene.entity("Spirit Beam", [transform((0, 5.0, front - 3.4), scale=(0.38, 5.0, 0.38)), mesh("Cylinder", graph("SpiritBeam", {"Intensity": 0.22, "Beam Color": [0.1, 1.0, 0.72]}), False)], temple)
    scene.entity("Rune Light", [transform((0, 0.6, front - 3.4)), light("Point", (0.3, 1.0, 0.8), 3.0, 5.0)], temple)
    for i, (pos, yaw, size) in enumerate([((-1.0, rise * 6, front + run * 6.0), 30, 1.8), ((5.5, 2.8, -tiers[1][0] / 2), 0, 2.4),
                                          ((-tiers[1][0] / 2, 2.9, -1.0), 90, 2.2)]):
        pitch = 90.0 if i == 0 else 0.0
        scene.entity("Crack", [transform(pos, yaw, pitch), decal((size, size, 0.6), TEX + "Decals/Generic_Decal_Crack_01.png",
                                                                                normal=TEX + "Decals/Generic_Decal_Crack_01_Normals.png",
                                                                                color=(0.35, 0.32, 0.28), roughness=0.9)], temple)
    return top


def build_gorge(scene):
    gorge = scene.group("Gorge")
    rock = stone(Moss_Amount=0.6, Tile=0.45, Stone_Tint=[0.58, 0.56, 0.52])
    wet_rock = stone(Moss_Amount=0.65, Tile=0.45, Stone_Tint=[0.55, 0.55, 0.52], Wet_Height=1.2)
    cliffs = [
        # The north wall; the falls come out of the middle one.
        ("SM_Gen_Env_Cliff_04", (POOL[0] + 0.5, -0.8, 39.5), 180, 1.3, wet_rock),
        ("SM_Gen_Env_Cliff_01", (1.0, -1.2, 42.0), 190, 1.35, rock),
        ("SM_Gen_Env_Cliff_02", (-11.0, -1.0, 43.0), 175, 1.45, rock),
        ("SM_Gen_Env_Cliff_03", (27.0, -1.0, 36.0), 145, 1.3, wet_rock),
        ("SM_Gen_Env_Cliff_02", (-24.0, -1.0, 42.0), 150, 1.5, rock),
        # The east wall behind the camp.
        ("SM_Gen_Env_Cliff_01", (32.0, -1.2, 22.0), 100, 1.35, rock),
        ("SM_Gen_Env_Cliff_03", (33.0, -1.0, 8.0), 85, 1.3, rock),
        ("SM_Gen_Env_Cliff_04", (35.0, -1.0, -8.0), 95, 1.2, rock),
        ("SM_Gen_Env_Cliff_01", (30.0, -1.2, -20.0), 60, 1.3, rock),
        # Westward, low sun: rock stacks either side of the light's path to the temple, and the arch.
        ("SM_Gen_Env_Cliff_Pillar_01", (-31.0, -0.5, -16.0), 30, 1.4, rock),
        ("SM_Gen_Env_Cliff_Arch_02", (-31.0, -0.5, 30.0), 90, 1.7, rock),
        ("SM_Gen_Env_Cliff_Pillar_01", (-35.0, -0.5, 37.0), 110, 1.1, rock),
    ]
    for key, pos, yaw, scale, material in cliffs:
        place(scene, "Cliff", key, pos, yaw, scale, material, gorge)
    for key, pos, yaw, scale in [("SM_Gen_Env_Background_Mountain_02", (-20.0, -6.0, 200.0), 185, 1.6),
                                 ("SM_Gen_Env_Background_Mountain_03", (-190.0, -8.0, 60.0), 95, 1.8),
                                 ("SM_Gen_Env_Background_Mountain_01", (130.0, -6.0, 180.0), 210, 1.5),
                                 ("SM_Gen_Env_Background_Mountain_02", (-170.0, -10.0, -70.0), 60, 1.7)]:
        place(scene, "Distant Ridge", key, pos, yaw, scale, stone(Moss_Amount=0.75, Tile=0.04, Stone_Tint=[0.5, 0.52, 0.5]), gorge, shadows=False)


def build_pool(scene):
    pool = scene.group("Plunge Pool", POOL)
    scene.entity("Water", [transform((0, WATER_Y, 0), scale=(POOL_RADIUS * 1.05, 0.01, POOL_RADIUS * 1.05)),
                           mesh("Cylinder", graph("TempleWater", {"Foam Center": [POOL[0] + 0.5, 0.0, POOL[2] + 4.6], "Foam Radius": 3.4}), False)], pool)
    scene.entity("Caustics", [transform((0, WATER_Y - 0.5, 0), 0.0, 90.0), decal((POOL_RADIUS * 2.1, POOL_RADIUS * 2.1, 1.0), graph_name="Caustics",
                                                                                 angle_fade=80.0, sort=1, params={"Intensity": 0.9})], pool)
    # A ring of mossy boulders hides the water's edge.
    ring = scene.group("Pool Rocks", parent=pool)
    keys = ["SM_Gen_Env_Rock_01", "SM_Gen_Env_Rock_02", "SM_Gen_Env_Rock_05", "SM_Gen_Env_Rock_03", "SM_Gen_Env_Rock_06", "SM_Gen_Env_Rock_07"]
    count = 26
    for i in range(count):
        a = 2 * math.pi * i / count + rng.uniform(-0.06, 0.06)
        rr = POOL_RADIUS + rng.uniform(-0.3, 0.5)
        pos = (math.sin(a) * rr, -0.5 + rng.uniform(-0.15, 0.1), math.cos(a) * rr)
        place(scene, "Pool Rock", keys[i % len(keys)], pos, rng.uniform(0, 360), rng.uniform(0.6, 1.0),
              stone(Moss_Amount=0.55, Tile=0.6, Wet_Height=0.55, Stone_Tint=[0.66, 0.62, 0.55]), ring)
    for i, (x, z, s) in enumerate([(-2.0, -1.5, 1.0), (1.5, 2.5, 0.8), (3.2, -1.0, 0.6), (-3.5, 1.8, 0.9)]):
        place(scene, "Lily Pads", "SM_Gen_Env_Lilypads_0%d" % (i % 3 + 1), (x, WATER_Y + 0.01, z), rng.uniform(0, 360), s,
              kit_material("SM_Gen_Env_Lilypads_01", roughness=0.4), pool, shadows=False)
    for i, (x, z) in enumerate([(-1.0, 3.2), (2.8, 1.0), (-3.0, -0.5)]):
        place(scene, "Stepping Stone", "SM_Gen_Env_Rock_03", (x, -0.55, z), rng.uniform(0, 360), 0.6,
              stone(Moss_Amount=0.6, Tile=0.7, Wet_Height=0.7), pool)

    # The falls: the mesh hangs from its lip and curves out towards the pool.
    # The import mirrors FBX Z, so the sheet curves out along -Z: no turn needed to face the pool.
    falls = scene.group("Waterfall", (POOL[0] + 0.5, 11.0, POOL[2] + 9.4), 0.0)
    place(scene, "Falling Water", "SM_Gen_Env_Waterfall_01", (0, 0, 0), 0.0, (1.15, 1.04, 1.0), graph("Waterfall", {"Base Height": -10.0}), falls, shadows=False)
    scene.entity("Spray", [transform((0, -10.2, -4.3)), particles(
        Shape="Box", BoxSize=[4.0, 0.3, 1.5], EmissionRate=60.0, MaxParticles=600, Lifetime=[1.8, 3.2], Speed=[0.4, 1.2],
        Size=[0.7, 1.4], EndSize=2.4, StartColor=[0.85, 0.9, 0.92], StartColor2=[0.95, 0.95, 0.95], EndColor=[0.9, 0.92, 0.95],
        StartAlpha=0.28, EndAlpha=0.0, Gravity=-0.03, Drag=0.6, NoiseStrength=0.6, NoiseFrequency=0.4, Blend="Alpha", Lit=True,
        Texture=TEX + "FX/Generic_Circle_Soft_01.png", SoftParticleDistance=1.0, FadeIn=0.15)], falls)
    scene.entity("Splash", [transform((0, -10.0, -4.4)), particles(
        Shape="Box", BoxSize=[3.5, 0.1, 0.8], EmissionRate=90.0, MaxParticles=500, Lifetime=[0.5, 1.0], Speed=[1.5, 3.0],
        ConeAngle=35.0, Size=[0.05, 0.12], EndSize=0.5, StartColor=[0.9, 0.95, 1.0], StartColor2=[1, 1, 1], StartAlpha=0.7,
        Gravity=0.6, Blend="Alpha", Lit=True, Texture=TEX + "FX/Generic_Circle_Soft_01.png", Alignment="Stretched", StretchFactor=0.08)], falls)
    for i, (x, y, z, key) in enumerate([(-3.2, -2.0, -0.6, "SM_Gen_Env_Vines_02"), (3.0, -1.0, -0.5, "SM_Gen_Env_Vines_01"),
                                        (-4.2, -4.5, -1.0, "SM_Gen_Env_Ivy_13"), (3.9, -5.5, -0.8, "SM_Gen_Env_Ivy_10")]):
        place(scene, "Falls Creeper", key, (x, y, z), 0.0, 1.2, foliage(-2.0, 0.04, cutout=key.startswith("SM_Gen_Env_Ivy")), falls)


def build_jungle(scene):
    jungle = scene.group("Jungle")
    trees = [
        # West, between the setting sun and the clearing: their shadows stripe the ground and the camp,
        # with a gap left along the light so the sun still reaches the temple.
        ("SM_Gen_Env_Tree_01", (-13.3, 0, -3.3), 1.4), ("SM_Gen_Env_Tree_03", (-17.5, 0, -7.0), 1.6),
        ("SM_Gen_Env_Tree_01", (-20.0, 0, -6.8), 1.7), ("SM_Gen_Env_Tree_02", (-17.9, 0, 32.8), 1.5), ("SM_Gen_Env_Tree_Dead_03", (-25.6, 0, 29.1), 1.1),
        ("SM_Gen_Env_Tree_01", (-33.1, 0, 25.0), 1.8), ("SM_Gen_Env_Tree_03", (-11.0, 0, -11.0), 1.4), ("SM_Gen_Env_Tree_02", (-26.0, 0, -12.0), 1.6),
        ("SM_Gen_Env_Tree_03", (-24.6, 0, -9.5), 1.7), ("SM_Gen_Env_Tree_01", (-20.0, 0, 38.0), 1.4),
        # East, under the cliffs.
        ("SM_Gen_Env_Tree_01", (24.0, 0, 15.0), 1.3), ("SM_Gen_Env_Tree_03", (26.0, 0, 3.0), 1.5), ("SM_Gen_Env_Tree_02", (22.0, 0, 30.0), 1.2),
        ("SM_Gen_Env_Tree_01", (25.0, 0, -9.0), 1.5), ("SM_Gen_Env_Tree_Dead_02", (4.0, 0, 37.0), 1.2), ("SM_Gen_Env_Tree_01", (-6.0, 0, 37.0), 1.1),
        # South, behind the camera.
        ("SM_Gen_Env_Tree_02", (12.0, 0, -15.0), 1.6), ("SM_Gen_Env_Tree_03", (-3.0, 0, -19.0), 1.5), ("SM_Gen_Env_Tree_01", (20.0, 0, -18.0), 1.7),
        ("SM_Gen_Env_Tree_02", (-14.0, 0, -20.0), 1.5),
    ]
    for key, pos, scale in trees:
        place(scene, "Jungle Tree", key, pos, rng.uniform(0, 360), scale * rng.uniform(0.9, 1.1), foliage(6.0 * scale, 0.06), jungle)
    under = [("SM_Gen_Env_Bush_Large_01", 2.2), ("SM_Gen_Env_Bush_Large_02", 2.0), ("SM_Gen_Env_Bush_Large_03", 2.0),
             ("SM_Gen_Env_Bush_01", 1.2), ("SM_Gen_Env_Bush_02", 1.2), ("SM_Gen_Env_Bush_03", 1.2), ("SM_Gen_Env_Bush_04", 1.2)]
    spots = [(-14.0, -2.0), (-18.0, 6.0), (-15.0, 26.0), (-21.0, 17.0), (-10.0, -7.0), (21.0, 19.0), (22.0, 8.0), (20.0, 1.0),
             (18.0, -9.0), (-6.0, -14.0), (6.0, -16.0), (-24.0, 7.0), (2.0, 33.0), (21.0, 26.0), (-12.0, 34.0), (24.0, -3.0),
             (-6.0, 33.0), (-25.0, 25.0), (14.0, -18.0), (-13.0, 11.0), (9.0, 34.0)]
    for i, (x, z) in enumerate(spots):
        key, h = under[i % len(under)]
        place(scene, "Undergrowth", key, (x, 0, z), rng.uniform(0, 360), rng.uniform(0.9, 1.3), foliage(h, 0.05), jungle)
    small = ["SM_Gen_Env_Fern_01", "SM_Gen_Env_Fern_02", "SM_Gen_Env_Fern_03", "SM_Gen_Env_Grass_Tall_01", "SM_Gen_Env_Grass_Tall_03",
             "SM_Gen_Env_Flowers_04", "SM_Gen_Env_Flowers_07", "SM_Gen_Env_Grass_04", "SM_Gen_Env_Shrub_02", "SM_Gen_Env_Flowers_01"]
    placed = 0
    attempts = 0
    while placed < 240 and attempts < 4000:
        attempts += 1
        x, z = rng.uniform(-30, 30), rng.uniform(-20, 36)
        # Keep the temple footprint, its stair approach, the pool and the camp clear.
        tx, tz = x - TEMPLE[0], z - TEMPLE[2]
        lx, lz = rotate_y((tx, 0, tz), -TEMPLE_YAW)[0], rotate_y((tx, 0, tz), -TEMPLE_YAW)[2]
        if abs(lx) < 9.5 and -19 < lz < 9.5:
            continue
        if math.hypot(x - POOL[0], z - POOL[2]) < POOL_RADIUS + 1.2:
            continue
        if math.hypot(x - CAMP[0], z - CAMP[2]) < 4.8:
            continue
        if any(math.hypot(x - cx, z - cz) < 3.5 for cx, _, cz in SHOT_CAMERAS):
            continue
        key = small[placed % len(small)]
        place(scene, "Ground Cover", key, (x, 0, z), rng.uniform(0, 360), rng.uniform(0.9, 1.5), foliage(1.2, 0.04), jungle)
        placed += 1
    # Foreground dressing for the opening shot.
    for key, pos, scale in [("SM_Gen_Env_Fern_02", (10.2, 0, -6.4), 1.3), ("SM_Gen_Env_Grass_Tall_03", (14.6, 0, -6.0), 1.1),
                            ("SM_Gen_Env_Fern_03", (11.4, 0, -4.6), 1.0), ("SM_Gen_Env_Flowers_04", (13.4, 0, -4.9), 1.1),
                            ("SM_Gen_Env_Fern_01", (15.6, 0, -4.0), 1.4)]:
        place(scene, "Foreground Plant", key, pos, rng.uniform(0, 360), scale, foliage(1.2, 0.04), jungle)
    for key, pos, scale in [("SM_Gen_Env_Rock_Pebbles_05", (7.2, 0, -6.8), 1.0), ("SM_Gen_Env_Rock_03", (16.5, -0.3, -5.2), 0.7)]:
        place(scene, "Foreground Rock", key, pos, rng.uniform(0, 360), scale, stone(Moss_Amount=0.6, Tile=0.9), jungle)
    for i, (key, pos, yaw, scale) in enumerate([("SM_Gen_Env_Grass_06", (-15.0, 0, 13.0), 30, 1.0), ("SM_Gen_Env_Grass_07", (21.0, 0, 12.0), 70, 1.0),
                                                ("SM_Gen_Env_Grass_06", (-4.0, 0, -13.0), 150, 1.0), ("SM_Gen_Env_Grass_07", (-19.0, 0, -3.0), 10, 1.1),
                                                ("SM_Gen_Env_Grass_06", (3.0, 0, 31.0), 100, 1.0)]):
        place(scene, "Grass Field", key, pos, yaw, scale, foliage(0.8, 0.05), jungle)
    # Dead wood and glowing mushrooms by the water.
    for i, (key, pos, yaw, scale) in enumerate([("SM_Gen_Env_Log_01", (6.0, 0.0, 30.0), 70, 1.0), ("SM_Gen_Env_Stump_02", (20.5, 0, 17.0), 20, 1.0),
                                                ("SM_Gen_Env_Log_02", (-11.0, 0.25, -3.0), 15, 1.1), ("SM_Gen_Env_Root_02", (19.0, 0, 20.5), 200, 1.4),
                                                ("SM_Gen_Env_Stump_01", (-13.0, 0, 30.0), 0, 1.2)]):
        place(scene, "Deadwood", key, pos, yaw, scale, kit_material(key, roughness=0.9), jungle)
    shrooms = scene.group("Glow Mushrooms", parent=jungle)
    for i, (x, z) in enumerate([(6.2, 28.4), (5.6, 29.8), (7.2, 30.4), (19.6, 18.6), (20.4, 16.6), (19.0, 15.8), (5.0, 27.5)]):
        place(scene, "Glow Mushroom", "SM_Gen_Env_Mushroom_0%d" % (i % 3 + 1), (x, 0, z), rng.uniform(0, 360), rng.uniform(0.6, 1.1),
              graph("GlowMushroom", {"Cap Height": 0.2}), shrooms)
    for i, (x, z) in enumerate([(6.2, 29.2), (19.8, 17.2)]):
        scene.entity("Mushroom Glow", [transform((x, 0.5, z)), light("Point", (0.25, 0.8, 1.0), 2.0, 3.5)], shrooms)


def build_camp(scene):
    camp = scene.group("Expedition Camp", CAMP)
    wood = lambda key: kit_material(key, roughness=0.85)
    # The jeep, headlights on, nosed towards the temple.
    jeep_yaw = look_angles((CAMP[0] + 4.0, 0, CAMP[2] + 5.0), (TEMPLE[0], 0, TEMPLE[2]))[0]
    jeep = scene.group("Jeep", (4.0, 0.0, 5.0), jeep_yaw - CAMP[0] * 0, parent=camp)
    place(scene, "4x4", "SM_Veh_4x4_Car_01", (0, 0, 0), 0.0, 1.0, lambda i: kit_material("SM_Veh_4x4_Car_01", roughness=0.55), jeep)
    for side in (-1, 1):
        scene.entity("Headlight", [transform((side * 0.68, 1.05, 2.45), 0.0, 6.0),
                                   light("Spot", (1.0, 0.9, 0.75), 18.0, 30.0, shadows=True, inner=14.0, outer=26.0)], jeep)
        scene.entity("Headlight Lens", [transform((side * 0.68, 1.05, 2.42), scale=(0.11, 0.11, 0.02)),
                                        mesh("Sphere", standard(None, (1, 1, 1), 0.2, emissive=(1.0, 0.92, 0.8), emissive_intensity=18.0), False)], jeep)
    scene.entity("Tyre Tracks", [transform((0.0, 0.0, -6.0), 0.0, 90.0), decal((2.6, 9.0, 1.0), TEX + "Decals/Generic_Decals_Tyre_01.png",
                                                                                  color=(0.25, 0.2, 0.16), roughness=0.95, opacity=0.8)], jeep)
    scene.entity("Puddle", [transform((-1.8, 0.0, -2.5), 30.0, 90.0), decal((2.4, 2.4, 0.8), TEX + "Decals/Generic_Decal_Pool_01.png",
                                                                             color=(0.08, 0.07, 0.06), roughness=0.05, sort=2)], jeep)
    # Camp fire with flames, embers and lit smoke.
    fire = scene.group("Camp Fire", (-2.0, 0.0, 1.5), parent=camp)
    for i in range(9):
        a = i / 9 * 2 * math.pi
        place(scene, "Fire Stone", "SM_Gen_Env_Rock_03", (math.sin(a) * 0.72, -0.08, math.cos(a) * 0.72), rng.uniform(0, 360), 0.32,
              stone(Moss_Amount=0.0, Tile=1.5, Stone_Tint=[0.45, 0.42, 0.4]), fire)
    for yaw in (0, 60, 120):
        place(scene, "Fire Log", "SM_Gen_Env_Log_02", (0, 0.1, 0), yaw, (0.25, 0.25, 0.22), kit_material("SM_Gen_Env_Log_02", roughness=0.95), fire,
              roll=8.0)
    scene.entity("Embers Bed", [transform((0, 0.02, 0), scale=(0.32, 0.03, 0.32)),
                                mesh("Sphere", standard(None, (0.05, 0.02, 0.01), 0.9, emissive=(1.0, 0.3, 0.05), emissive_intensity=2.5))], fire)
    scene.entity("Flames", [transform((0, 0.15, 0)), particles(
        Graph=GRAPHS + "Flame.shadergraph", Texture=TEX + "FX/Generic_Candle_Flame_01.png", Shape="Cone", ShapeRadius=0.22, ConeAngle=12.0,
        EmissionRate=80.0, MaxParticles=200, Lifetime=[0.45, 0.85], Speed=[0.8, 1.4], Size=[0.35, 0.6], EndSize=0.3,
        StartColor=[1.0, 0.75, 0.4], StartColor2=[1.0, 0.55, 0.2], EndColor=[1.0, 0.3, 0.08], Intensity=3.0, Gravity=-0.05,
        NoiseStrength=0.45, NoiseFrequency=1.5, Rotation=[-15.0, 15.0], SoftParticleDistance=0.15)], fire)
    scene.entity("Embers", [transform((0, 0.3, 0)), particles(
        Shape="Sphere", ShapeRadius=0.35, EmissionRate=18.0, Lifetime=[1.5, 3.0], Speed=[0.6, 1.6], Size=[0.025, 0.05], EndSize=0.3,
        StartColor=[1.0, 0.55, 0.15], StartColor2=[1.0, 0.8, 0.3], EndColor=[1.0, 0.2, 0.0], Intensity=8.0, Gravity=-0.12,
        NoiseStrength=2.0, NoiseFrequency=1.2, Alignment="Stretched", StretchFactor=0.06, Texture=TEX + "FX/Generic_Circle_Soft_01.png")], fire)
    scene.entity("Smoke", [transform((0, 1.2, 0)), particles(
        Shape="Sphere", ShapeRadius=0.2, EmissionRate=5.0, Lifetime=[4.0, 6.5], Speed=[0.35, 0.6], Size=[0.4, 0.7], EndSize=4.5,
        StartColor=[0.3, 0.29, 0.28], StartColor2=[0.4, 0.38, 0.36], EndColor=[0.5, 0.48, 0.47], StartAlpha=0.16, EndAlpha=0.0,
        Gravity=-0.04, Drag=0.3, NoiseStrength=0.5, NoiseFrequency=0.3, Blend="Alpha", Lit=True, FadeIn=0.2,
        Texture=TEX + "FX/Generic_Circle_Soft_01.png", SoftParticleDistance=0.6)], fire)
    scene.entity("Fire Light", [transform((0, 0.8, 0)), light("Point", (1.0, 0.5, 0.2), 14.0, 11.0, shadows=True),
                                script("Flicker", Strength=0.28, Speed=1.0, Seed=11.0)], fire)
    # Map table under a tube lamp hung from a pole, with the expedition kit around it.
    table = scene.group("Map Table", (2.5, 0.0, -1.0), 25.0, parent=camp)
    place(scene, "Table", "SM_Gen_Prop_Table_01", (0, 0, 0), 0.0, 1.0, wood("SM_Gen_Prop_Table_01"), table)
    for name, key, pos, yaw in [("Map", "SM_Prop_Map_01", (0.0, 0.75, -0.1), 10), ("Compass", "SM_Prop_Compass_01", (0.45, 0.75, 0.1), 40),
                                ("Binoculars", "SM_Prop_Binoculars_01", (-0.6, 0.75, 0.05), -30), ("Mug", "SM_Gen_Prop_Mug_01", (0.8, 0.75, -0.25), 0),
                                ("Revolver", "SM_Wep_Pistol_Revolver_01", (-0.25, 0.76, -0.4), 80), ("Flashlight", "SM_Prop_Flashlight_01", (0.7, 0.79, 0.25), 0)]:
        place(scene, name, key, pos, yaw, 1.0, (lambda k: (lambda i: kit_material(k, roughness=0.6)))(key), table)
    place(scene, "Chair", "SM_Gen_Prop_Chair_01", (0.3, 0.0, -1.0), 190.0, 1.0, wood("SM_Gen_Prop_Chair_01"), table)
    scene.entity("Lamp Pole", [transform((1.25, 1.2, 0.55), scale=(0.025, 1.2, 0.025)), mesh("Cylinder", standard(None, (0.15, 0.15, 0.15), 0.5, 0.8))], table)
    scene.entity("Lamp Arm", [transform((0.6, 2.35, 0.55), 0.0, 0.0, 90.0, (0.02, 0.7, 0.02)), mesh("Cylinder", standard(None, (0.15, 0.15, 0.15), 0.5, 0.8))], table)
    scene.entity("Tube Lamp", [transform((0.15, 2.15, 0.55), 0.0, 0.0, 90.0, (0.03, 0.45, 0.03)),
                               mesh("Cylinder", standard(None, (1, 1, 1), 0.3, emissive=(0.85, 0.95, 1.0), emissive_intensity=1.0), False)], table)
    scene.entity("Tube Light", [transform((0.15, 2.1, 0.55)), light("Bar", (0.85, 0.95, 1.0), 1.6, 5.0, Length=0.85, Radius=0.03)], table)
    kit = scene.group("Supplies", (3.5, 0.0, -3.5), -20.0, parent=camp)
    for name, key, pos, yaw in [("Crate", "SM_Gen_Prop_Crate_01", (0, 0, 0), 5), ("Crate", "SM_Gen_Prop_Crate_03", (0.1, 0.954, 0.1), 30),
                                ("Crate", "SM_Gen_Prop_Crate_02", (1.3, 0, 0.3), -10), ("Barrel", "SM_Gen_Prop_Barrel_Wood_01", (-1.0, 0, 0.6), 0),
                                ("Sacks", "SM_Gen_Prop_Sack_Stack_01", (2.3, 0, 1.2), 60), ("Sack", "SM_Gen_Prop_Sack_02", (-1.1, 0, -0.6), 20),
                                ("Bedroll", "SM_Prop_Bedroll_01", (-2.6, 0.08, 1.9), 80), ("Bag", "SM_Prop_Bag_01", (-1.9, 0, 2.6), 10),
                                ("Pickaxe", "SM_Gen_Wep_Pickaxe_01", (1.0, 0.0, -0.75), 0), ("Spade", "SM_Gen_Wep_Spade_01", (1.5, 0.0, -0.7), 0),
                                ("Rope", "SM_Gen_Prop_Rope_02", (0.4, 0.0, 1.6), 0), ("Lantern Barrel", "SM_Gen_Prop_Barrel_Metal_01", (-2.0, 0, -0.1), 0)]:
        tilt = -12.0 if key in ("SM_Gen_Wep_Pickaxe_01", "SM_Gen_Wep_Spade_01") else 0.0
        place(scene, name, key, pos, yaw, 1.0, (lambda k: (lambda i: kit_material(k, roughness=0.8)))(key), kit, pitch=tilt)


# ---------------------------------------------------------------------------------------------
# Characters. The Synty explorers have no animation clips here, so they're posed by hand: the
# expanded skeleton is written into the scene (a saved Model reuses its node entities by name) with
# some bones turned. Poses aim a bone at a direction in model space (the rig faces -Z, left is +X).

RIGS = json.loads((ROOT / "Tools/LostTempleRigs.json").read_text())


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz]


def qconj(q):
    return [-q[0], -q[1], -q[2], q[3]]


def qrot(q, v):
    return qmul(qmul(q, [v[0], v[1], v[2], 0.0]), qconj(q))[:3]


def qarc(a, b):
    """The shortest rotation taking direction a to direction b."""
    def norm(v):
        length = math.sqrt(sum(c * c for c in v)) or 1.0
        return [c / length for c in v]
    a, b = norm(a), norm(b)
    cross = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    q = cross + [1.0 + sum(x * y for x, y in zip(a, b))]
    length = math.sqrt(sum(c * c for c in q))
    return [c / length for c in q]


def qaxis(axis, degrees):
    h = math.radians(degrees) / 2
    return [axis[0] * math.sin(h), axis[1] * math.sin(h), axis[2] * math.sin(h), math.cos(h)]


def posed_skeleton(key, aims, turns):
    """Local transforms for the rig with bones aimed at model-space directions (aims: bone -> (child, dir))
    or turned about a model-space axis (turns: bone -> (axis, degrees)), plus the posed world poses."""
    nodes = [dict(n) for n in RIGS[key]["Nodes"]]
    index = {n["name"]: i for i, n in enumerate(nodes)}
    world = []
    for i, n in enumerate(nodes):
        parent_pos, parent_rot = world[n["parent"]] if n["parent"] >= 0 else ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0])
        pos = [a + b for a, b in zip(parent_pos, qrot(parent_rot, n["pos"]))]
        rot = qmul(parent_rot, n["rot"])
        turn = None
        if n["name"] in aims:
            child, direction = aims[n["name"]]
            current = qrot(rot, nodes[index[child]]["pos"])
            turn = qarc(current, direction)
        elif n["name"] in turns:
            turn = qaxis(*turns[n["name"]])
        if turn:
            rot = qmul(turn, rot)
            n["rot"] = [round(c, 6) for c in qmul(qconj(parent_rot), rot)]
        world.append((pos, rot))
    return nodes, index, world


def character(scene, name, key, pos, facing, aims=None, turns=None, attachments=(), parent=None):
    """An explorer standing at pos, facing the compass direction facing (degrees, 0 = +Z)."""
    rig = RIGS[key]
    nodes, index, world = posed_skeleton(key, aims or {}, turns or {})
    root = scene.entity(name, [transform(pos, facing + 180.0),
                               {"Type": "Model", "ModelPath": rig["ModelPath"], "Compact": False,
                                "BakedImportScale": rig["BakedImportScale"]}], parent)
    entities = []
    for n in nodes:
        components = [{"Type": "Transform", "Position": n["pos"], "Rotation": n["rot"], "Scale": n["scale"]}]
        for c in n["comps"]:
            if c["Type"] == "Mesh":
                c = dict(c, Material=standard(EXPLORER, (1, 1, 1), 0.7))
            components.append(c)
        owner = entities[n["parent"]] if n["parent"] >= 0 else root
        entities.append(scene.entity(n["name"], components, owner))
    # Attachments are modelled at their bone's pivot, aligned with the character.
    for bone, attach_key in attachments:
        _, rot = world[index[bone]]
        scene.entity(attach_key, [{"Type": "Transform", "Position": [0.0, 0.0, 0.0], "Rotation": [round(c, 6) for c in qconj(rot)], "Scale": [1.0, 1.0, 1.0]},
                                  model(FBX + attach_key + ".fbx", standard(EXPLORER, (1, 1, 1), 0.7))], entities[index[bone]])
    return root, nodes, index, world


def build_explorers(scene):
    camp = scene.group("Explorers")
    # The surveyor leans over the map table, reading the map.
    table_yaw = 25.0
    table = [CAMP[0] + rotate_y((2.5, 0, -1.0), 0)[0], 0.0, CAMP[2] - 1.0]
    spot = rotate_y((-0.35, 0.0, 0.95), table_yaw)
    character(scene, "Surveyor", "SK_Chr_Explorer_Female_01", (table[0] + spot[0], 0.0, table[2] + spot[2]), table_yaw + 180.0,
              aims={"spine_02": ("spine_03", (0.0, 0.93, -0.36)),
                    "UpperArm_L": ("lowerarm_l", (0.32, -0.62, -0.72)), "lowerarm_l": ("Hand_L", (0.05, -0.55, -0.83)),
                    "UpperArm_R": ("lowerarm_r", (-0.32, -0.62, -0.72)), "lowerarm_r": ("Hand_R", (-0.05, -0.55, -0.83))},
              turns={"head": ((1.0, 0.0, 0.0), -22.0)},
              attachments=[("head", "SM_Chr_Attach_Hair_Female_Hat_01"), ("head", "SM_Chr_Attach_Hat_Female_01"),
                           ("spine_03", "SM_Chr_Attach_Backpack_01")], parent=camp)
    # The leader by the fire, shining a flashlight up at the temple.
    leader_pos = (CAMP[0] - 3.6, 0.0, CAMP[2] + 2.6)
    facing = look_angles(leader_pos, temple_point((0.0, TEMPLE_TOP, -4.0)))[0]
    beam = (0.0, -0.05, -1.0)
    root, nodes, index, world = character(
        scene, "Expedition Leader", "SK_Chr_Explorer_Male_01", leader_pos, facing,
        aims={"UpperArm_R": ("lowerarm_r", (-0.18, -0.3, -0.94)), "lowerarm_r": ("Hand_R", beam),
              "UpperArm_L": ("lowerarm_l", (0.22, -0.97, 0.05)), "lowerarm_l": ("Hand_L", (0.15, -0.85, -0.5))},
        turns={"head": ((1.0, 0.0, 0.0), 8.0)},
        attachments=[("head", "SM_Chr_Attach_Hair_Male_Hat_01"), ("head", "SM_Chr_Attach_Hat_Hunter_01"),
                     ("head", "SM_Chr_Attach_Beard_01"), ("spine_03", "SM_Chr_Attach_Backpack_01")], parent=camp)
    hand, _ = world[index["Hand_R"]]
    torch_at = [hand[0], hand[1], hand[2] - 0.12]
    yaw, pitch = look_angles((0, 0, 0), beam)
    scene.entity("Flashlight", [transform(torch_at, yaw, pitch - 90.0, scale=1.0), model(FBX + "SM_Prop_Flashlight_01.fbx", standard(EXPLORER, (1, 1, 1), 0.5))], root)
    scene.entity("Flashlight Beam", [transform([torch_at[0], torch_at[1], torch_at[2] - 0.15], yaw, pitch),
                                      light("Spot", (0.95, 0.97, 1.0), 22.0, 34.0, shadows=True, inner=7.0, outer=13.0)], root)


def build_atmosphere(scene):
    air = scene.group("Atmosphere")
    scene.entity("Pollen in the Light", [transform((-2.0, 4.0, 14.0)), particles(
        Shape="Box", BoxSize=[30.0, 8.0, 30.0], EmissionRate=90.0, MaxParticles=900, Lifetime=[6.0, 10.0], Speed=[0.02, 0.1],
        Size=[0.02, 0.045], EndSize=1.0, StartColor=[1.0, 0.95, 0.85], StartColor2=[1.0, 0.9, 0.75], EndColor=[1.0, 0.95, 0.85],
        StartAlpha=0.8, EndAlpha=0.0, FadeIn=0.3, NoiseStrength=0.25, NoiseFrequency=0.2, Blend="Alpha", Lit=True,
        Texture=TEX + "FX/Generic_Circle_Soft_01.png", SoftParticleDistance=0.0)], air)
    scene.entity("Falling Leaves", [transform((-4.0, 11.0, 12.0)), particles(
        Shape="Box", BoxSize=[36.0, 2.0, 30.0], EmissionRate=7.0, MaxParticles=200, Lifetime=[9.0, 14.0], Speed=[0.1, 0.3],
        Size=[0.12, 0.2], EndSize=1.0, StartColor=[0.75, 0.6, 0.25], StartColor2=[0.45, 0.6, 0.2], EndColor=[0.6, 0.45, 0.2],
        StartAlpha=1.0, EndAlpha=0.0, FadeIn=0.05, Gravity=0.018, Drag=0.8, NoiseStrength=1.2, NoiseFrequency=0.35,
        AngularVelocity=[-120.0, 120.0], Blend="Alpha", Lit=True, Texture=TEX + "FX/Generic_Leaf_01.png", SoftParticleDistance=0.0)], air)
    flies = scene.group("Fireflies", parent=air)
    for i, (x, y, z) in enumerate([(7.0, 1.2, 18.0), (5.5, 0.8, 26.0), (18.0, 1.4, 18.0), (9.0, 1.6, 14.0), (-12.0, 1.0, 8.0),
                                   (19.5, 1.0, 27.0), (-13.0, 1.5, 22.0), (14.5, 0.9, 13.5), (4.0, 1.4, 31.0), (20.0, 1.2, 8.0)]):
        scene.entity("Firefly", [transform((x, y, z), scale=0.02), light("Point", (0.75, 1.0, 0.35), 0.6, 1.6),
                                 mesh("Sphere", standard(None, (0.9, 1.0, 0.5), 0.5, emissive=(0.8, 1.0, 0.3), emissive_intensity=40.0), False),
                                 script("Wander", Radius=1.6, Speed=0.35, Seed=float(i))], flies)
    scene.entity("Firefly Swarm", [transform((8.0, 1.2, 18.0)), particles(
        Shape="Box", BoxSize=[26.0, 2.0, 22.0], EmissionRate=14.0, MaxParticles=160, Lifetime=[3.0, 6.0], Speed=[0.05, 0.2],
        Size=[0.03, 0.05], EndSize=1.0, StartColor=[0.75, 1.0, 0.3], StartColor2=[1.0, 0.9, 0.35], EndColor=[0.75, 1.0, 0.3],
        Intensity=12.0, FadeIn=0.4, NoiseStrength=0.8, NoiseFrequency=0.5, Texture=TEX + "FX/Generic_Circle_Soft_01.png")], air)


def build(write=True):
    scene = Scene()
    build_camera(scene)
    build_sun(scene)
    build_ground(scene)
    build_temple(scene)
    build_gorge(scene)
    build_pool(scene)
    build_jungle(scene)
    build_camp(scene)
    build_explorers(scene)
    build_atmosphere(scene)
    document = {"Version": 2, "Cores": [], "Entities": scene.entities}
    if write:
        (ROOT / SCENE).write_text(json.dumps(document, indent=1) + "\n")
    return document


def write_graphs():
    folder = ROOT / GRAPHS
    folder.mkdir(parents=True, exist_ok=True)
    for name, make in LostTempleGraphs.GRAPHS.items():
        (folder / (name + ".shadergraph")).write_text(json.dumps(make().document(), indent=4) + "\n")


if __name__ == "__main__":
    write_graphs()
    if "--graphs" not in sys.argv:
        build()
        write_shots()
        print("wrote", SCENE)
