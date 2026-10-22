#!/usr/bin/env python3
"""Rebuild the Launch Night office scene, its animation sequences and its shader graphs.

    python3 Tools/BuildLaunchNight.py            # scene + sequences + graphs
    python3 Tools/BuildLaunchNight.py --graphs   # graphs only

Writes Assets/Scenes/LaunchNight.lvl, Assets/Animations/LaunchNight/*.sequence and
Assets/ShaderGraphs/LaunchNight/*.shadergraph, overwriting them. A changed graph needs its .sg/
sources regenerated afterwards (save it in Havana, or run the project-graph test with
ME_SHADERGRAPH_UPDATE=1; see Assets/Scenes/LaunchNight.md). Python 3, no packages.

3:47 AM at Moonshot Games, thirteen minutes before the gold master is due. The build server is on
fire. Everything is made from the Synty Office Pack; every model part gets an explicit material
(the FBXs reference .psd textures that aren't shipped). Part paths come from
Tools/LaunchNightParts.json, skeletons from Tools/LaunchNightRigs.json (both recorded by loading
the models in Havana) and model bounds from Tools/LaunchNightBounds.json (the pack's OBJ files).

Coordinates are metres: +X east, +Y up, +Z north. The floor is 25 x 17.5 m with a 3 m ceiling.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import LaunchNightAudio  # noqa: E402
import LaunchNightGraphs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCENE = "Assets/Scenes/LaunchNight.lvl"
GRAPHS = "Assets/ShaderGraphs/LaunchNight/"
ANIMATIONS = "Assets/Animations/LaunchNight/"
PACK = "Assets/Models/Synty/OfficePack/"
FBX = PACK + "FBX/"
TEX = PACK + "Textures/"
ATLAS = TEX + "PolygonOffice_Texture_01_A.png"
ATLAS_B = TEX + "PolygonOffice_Texture_01_B.png"
ATLAS_C = TEX + "PolygonOffice_Texture_01_C.png"
NET = TEX + "Net_Alpha.tga"
FX = "Assets/Models/Synty/ExplorerKit/Textures/FX/"
SOFT = FX + "Generic_Circle_Soft_01.png"
FLAME_TEX = FX + "Generic_Candle_Flame_01.png"
FLAME_GRAPH = "Assets/ShaderGraphs/LostTemple/Flame.shadergraph"
PARTS = json.loads((ROOT / "Tools/LaunchNightParts.json").read_text())
RIGS = json.loads((ROOT / "Tools/LaunchNightRigs.json").read_text())
BOUNDS = json.loads((ROOT / "Tools/LaunchNightBounds.json").read_text())

FPS = 30
CEILING = 3.0
rng = random.Random(4471)


def guid(name):
    return hashlib.sha256(("launch-night/" + name).encode()).hexdigest()[:16]


def r3(values):
    return [round(float(v), 4) for v in values]


# ---------------------------------------------------------------------------------------------
# Rotations. Models face -Z; "facing" is the compass direction a model's front points at
# (0 = north/+Z, 90 = east/+X), so a model facing f has yaw f + 180.


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz]


def qconj(q):
    return [-q[0], -q[1], -q[2], q[3]]


def qrot(q, v):
    return qmul(qmul(q, [v[0], v[1], v[2], 0.0]), qconj(q))[:3]


def qaxis(axis, degrees):
    h = math.radians(degrees) / 2
    length = math.sqrt(sum(c * c for c in axis)) or 1.0
    return [axis[0] / length * math.sin(h), axis[1] / length * math.sin(h), axis[2] / length * math.sin(h), math.cos(h)]


def quat(yaw=0.0, pitch=0.0, roll=0.0):
    """Yaw about +Y, then pitch about +X (positive tips +Z down), then roll about +Z. Degrees."""
    q = qmul(qaxis((0, 1, 0), yaw), qmul(qaxis((1, 0, 0), pitch), qaxis((0, 0, 1), roll)))
    return [round(v, 6) for v in q]


def qarc(a, b):
    """The shortest rotation taking direction a to direction b."""
    def norm(v):
        length = math.sqrt(sum(c * c for c in v)) or 1.0
        return [c / length for c in v]
    a, b = norm(a), norm(b)
    d = sum(x * y for x, y in zip(a, b))
    if d < -0.9999:
        return qaxis((0, 1, 0) if abs(a[1]) < 0.9 else (1, 0, 0), 180.0)
    cross = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    q = cross + [1.0 + d]
    length = math.sqrt(sum(c * c for c in q))
    return [c / length for c in q]


def look_angles(src, dst):
    """Yaw/pitch (degrees) that point +Z from src at dst (cameras, lights)."""
    dx, dy, dz = dst[0] - src[0], dst[1] - src[1], dst[2] - src[2]
    return math.degrees(math.atan2(dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))


def aim_y(direction):
    """The rotation pointing +Y (a particle emitter's axis) along a direction."""
    return [round(c, 6) for c in qarc((0, 1, 0), direction)]


def look(src, dst, roll=0.0):
    yaw, pitch = look_angles(src, dst)
    return quat(yaw, pitch, roll)


def compass(dx, dz):
    return math.degrees(math.atan2(dx, dz))


def sub3(a, b):
    return [x - y for x, y in zip(a, b)]


def add3(a, b):
    return [x + y for x, y in zip(a, b)]


def scale3(a, s):
    return [x * s for x in a]


def length3(a):
    return math.sqrt(sum(x * x for x in a))


def norm3(a):
    n = length3(a) or 1.0
    return [x / n for x in a]


# ---------------------------------------------------------------------------------------------
# Components


def transform(pos=(0, 0, 0), yaw=0.0, pitch=0.0, roll=0.0, scale=1.0, rotation=None):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    return {"Type": "Transform", "Position": r3(pos), "Rotation": rotation or quat(yaw, pitch, roll), "Scale": r3(scale)}


def standard(texture=ATLAS, color=(1, 1, 1), roughness=0.75, metallic=0.0, emissive=(0, 0, 0), emissive_intensity=1.0,
             opacity=1.0, transparent=False, faces=0, cutout=False):
    material = {"Type": "StandardMaterial", "DiffuseColor": r3(color), "Roughness": roughness, "Metallic": metallic,
                "EmissiveColor": r3(emissive), "EmissiveIntensity": emissive_intensity, "Opacity": opacity,
                "RenderMode": 1 if transparent else 0, "BlendMode": 0, "FaceMode": faces, "Textures": {}}
    if texture:
        material["Textures"]["Diffuse"] = {"Path": texture, "RenderMode": "Cutout" if cutout else "Opaque"}
    if cutout:
        material["AlphaCutoff"] = 0.5
    return material


def glass(tint=(0.1, 0.14, 0.15), opacity=0.18, roughness=0.04):
    return standard(None, tint, roughness, opacity=opacity, transparent=True, faces=2)


def graph(name, params=None, textures=None):
    path = name if name.startswith("Assets/") else GRAPHS + name + ".shadergraph"
    return {"Type": "ShaderGraphMaterial", "Graph": path,
            "Params": {k: (list(v) + [0.0] * (4 - len(v)) if isinstance(v, (list, tuple)) else [v, 0.0, 0.0, 0.0])
                       for k, v in (params or {}).items()},
            "Textures": textures or {}}


def graph_params(params):
    return {"Params": {k: (list(v) + [0.0] * (4 - len(v)) if isinstance(v, (list, tuple)) else [v, 0.0, 0.0, 0.0])
                       for k, v in params.items()}, "Textures": {}}


def mesh(shape, material, shadows=True):
    return {"Type": "Mesh", "MeshType": shape, "CastShadows": shadows, "Material": material}


def light(kind, color, intensity, range_=6.0, shadows=False, inner=20.0, outer=32.0, **extra):
    data = {"Type": "Light", "LightType": kind, "Color": r3(color), "Intensity": intensity, "Range": range_,
            "CastShadows": shadows, "InnerConeAngle": inner, "OuterConeAngle": outer, "ShadowBias": 0.6, "ShadowNormalBias": 1.5}
    data.update(extra)
    return data


def particles(**fields):
    data = {"Type": "ParticleSystem", "Looping": True, "Duration": 5.0, "EmissionRate": 20.0, "BurstCount": 0,
            "MaxParticles": 400, "SimulationSpace": "World", "Shape": "Sphere", "ShapeRadius": 0.2, "ConeAngle": 15.0,
            "BoxSize": [1.0, 1.0, 1.0], "EmitFromShell": False, "Lifetime": [1.0, 2.0], "Speed": [0.2, 0.5],
            "Size": [0.1, 0.2], "Rotation": [0.0, 360.0], "AngularVelocity": [-30.0, 30.0], "StartColor": [1, 1, 1],
            "StartColor2": [1, 1, 1], "StartAlpha": 1.0, "Intensity": 1.0, "EndSize": 1.0, "EndColor": [1, 1, 1],
            "EndAlpha": 0.0, "FadeIn": 0.1, "Gravity": 0.0, "Drag": 0.0, "NoiseStrength": 0.0, "NoiseFrequency": 1.0,
            "Texture": SOFT, "Blend": "Additive", "Alignment": "Billboard", "StretchFactor": 0.1, "FlipbookColumns": 1,
            "FlipbookRows": 1, "FlipbookFps": 0.0, "SoftParticleDistance": 0.2, "Graph": "", "Lit": False}
    for key, value in fields.items():
        data[key] = r3(value) if isinstance(value, (list, tuple)) else value
    return data


def sound(scene, name, clip, pos, parent, volume=1.0, near=1.0, far=10.0, spatial=1.0):
    """A looping ambient AudioSource (clips from Tools/LaunchNightAudio.py). 3D sources fade out to
    silence at `far`, so the quiet ones don't pile up across the floor."""
    return scene.entity(name, [transform(pos), {
        "Type": "AudioSource", "FilePath": LaunchNightAudio.path(clip), "Bus": "SFX", "Volume": volume, "Pitch": 1.0,
        "Mute": False, "PlayOnAwake": True, "Loop": True, "SpatialBlend": spatial, "MinDistance": near, "MaxDistance": far,
        "Rolloff": "LinearSquare", "DopplerLevel": 0.0, "Priority": 128, "MaxOneShots": 1}], parent)


def decal(size, albedo="", graph_name="", color=(1, 1, 1), roughness=0.6, opacity=1.0, sort=0, angle_fade=70.0, params=None):
    data = {"Type": "Decal", "Albedo": albedo, "NormalMap": "", "Color": r3(color), "Size": r3(size), "Roughness": roughness,
            "Metallic": 0.0, "Opacity": opacity, "EmissiveColor": [1, 1, 1], "EmissiveIntensity": 0.0,
            "NormalStrength": 1.0, "SortOrder": sort, "AngleFade": angle_fade, "AngleFadeWidth": 20.0,
            "Graph": GRAPHS + graph_name + ".shadergraph" if graph_name else ""}
    if params:
        data["GraphParams"] = graph_params(params)
    return data


# ---------------------------------------------------------------------------------------------
# Materials for Synty parts, by the slot the pack's material list gives each mesh.


def load_slots():
    slots, prefab, mesh_name = {}, None, None
    for line in (ROOT / (PACK + "MaterialList_PolygonOffice.txt")).read_text().splitlines():
        text = line.strip()
        if text.startswith("Prefab Name:"):
            prefab = text.split(":", 1)[1].strip()
            slots[prefab] = {}
        elif text.startswith("Mesh Name:") and prefab:
            mesh_name = text.split(":", 1)[1].strip()
            slots[prefab][mesh_name] = []
        elif text.startswith("Slot:") and prefab and mesh_name:
            slots[prefab][mesh_name].append(text.split(":", 1)[1].split("(")[0].strip().replace("PolygonOffice_", ""))
    return slots


SLOTS = load_slots()
SCREEN_OFF = standard(None, (0.006, 0.006, 0.008), 0.35)


def part_slot(key, part):
    node = part.split("/")[-2].split("#")[0]
    index = int(part.split("#")[-1])
    slots = SLOTS.get(key, {}).get(node, [])
    return slots[index] if index < len(slots) else "Material_01_A"


def part_materials(key, atlas=ATLAS, tint=(1, 1, 1), roughness=0.75, screens=(), overrides=None):
    """Materials for every part of a model: atlas, glass, screens (in order: screens[i] for the i-th
    screen slot, off when missing), or overrides[part index]."""
    result = []
    screen_index = 0
    for index, part in enumerate(PARTS[key]["Parts"]):
        if overrides and index in overrides:
            result.append(overrides[index])
            continue
        slot = part_slot(key, part)
        if "Glass" in slot:
            result.append(glass())
        elif slot.startswith("Material_Screen"):
            result.append(screens[screen_index] if screen_index < len(screens) and screens[screen_index] else SCREEN_OFF)
            screen_index += 1
        elif slot.startswith("Material_Net"):
            result.append(standard(NET, (1, 1, 1), 0.8, cutout=True, faces=2))
        else:
            result.append(standard(atlas, tint, roughness))
    return result


def model(key, materials=None, shadows=True, **material_args):
    materials = materials or part_materials(key, **material_args)
    parts = {}
    for index, part in enumerate(PARTS[key]["Parts"]):
        parts[part] = {"Type": "Mesh", "MeshType": "Model", "CastShadows": shadows, "Material": materials[index]}
    return {"Type": "Model", "ModelPath": PARTS[key]["ModelPath"], "Compact": True, "BakedImportScale": 0.01, "Parts": parts}


# ---------------------------------------------------------------------------------------------
# Scene graph and sequences


class Scene:
    def __init__(self):
        self.entities = []
        self.names = {}
        self.clips = {}

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

    def clip(self, name, seconds, autoplay=True):
        """A new clip, played by its own entity under Sequences (one Sequence per entity)."""
        if not hasattr(self, "sequences"):
            self.sequences = self.group("Sequences")
        player = self.entity(name, [transform()], self.sequences)
        self.clips[name] = Clip(self, name, seconds, player, autoplay)
        return self.clips[name]


class Clip:
    """A .sequence asset (tracks against named slots) plus the player that binds the slots."""

    def __init__(self, scene, name, seconds, player, autoplay):
        self.scene = scene
        self.name = name
        self.frames = int(round(seconds * FPS))
        self.player = player
        self.autoplay = autoplay
        self.tracks = []
        self.slots = {}

    def slot(self, entity, label=None):
        if entity["GUID"] not in self.slots:
            base = label or entity["Name"]
            used = set(self.slots.values())
            name, suffix = base, 2
            while name in used:
                name, suffix = "%s %d" % (base, suffix), suffix + 1
            self.slots[entity["GUID"]] = name
        return self.slots[entity["GUID"]]

    def track(self, entity, component, prop, keys, label=None):
        """keys: [(seconds, value, interpolation)]; values are numbers or lists (padded to 4)."""
        def pad(value):
            value = list(value) if isinstance(value, (list, tuple)) else [value]
            return [round(float(v), 5) for v in value] + [0.0] * (4 - len(value))
        frames = {}
        for seconds, value, interpolation in keys:
            frame = max(0, min(self.frames, int(round(seconds * FPS))))
            frames[frame] = {"Frame": frame, "Value": pad(value), "Interpolation": interpolation}
        self.tracks.append({"Binding": self.slot(entity, label), "Component": component, "Property": prop, "Enabled": True,
                            "Keys": [frames[f] for f in sorted(frames)]})

    @property
    def path(self):
        return ANIMATIONS + self.name.replace(" ", "") + ".sequence"

    def asset(self):
        return {"Version": 1, "Name": self.name, "FrameRate": FPS, "DurationFrames": self.frames, "Tracks": self.tracks}

    def component(self):
        return {"Type": "Sequence", "Clip": self.path, "Clips": [{"Name": self.name, "Clip": self.path}],
                "Bindings": [{"Slot": slot, "Target": target} for target, slot in self.slots.items()],
                "PlayOnStart": self.autoplay, "Loop": True, "Speed": 1.0}


def spin_keys(seconds, axis=(0, 1, 0), turns=1.0, steps=8, base=(0, 0, 0, 1), phase=0.0):
    """Linear rotation keys for a constant spin about a parent-space axis (steps per turn)."""
    count = max(2, int(steps * turns))
    keys = []
    for i in range(count + 1):
        t = i / count
        q = qmul(qaxis(axis, 360.0 * turns * t + phase), base)
        keys.append((seconds * t, q, "Linear"))
    return keys


def flicker_keys(seconds, base, low, high, step=0.1, seed=0, drop=0.0, interpolation="Linear"):
    """Random intensity keys between low and high every step seconds; drop = chance of going dark."""
    r = random.Random(seed)
    keys = []
    t = 0.0
    while t < seconds - 1e-6:
        value = base * (0.02 if r.random() < drop else r.uniform(low, high))
        keys.append((t, value, interpolation))
        t += step
    keys.append((seconds, keys[0][1], interpolation))
    return keys


# ---------------------------------------------------------------------------------------------
# Placement. put() stands a model with its bounding box's bottom centre on a point.


def bounds(key):
    lo, hi = BOUNDS[key]
    return lo, hi


def put(scene, name, key, at, facing=180.0, scale=1.0, parent=None, pitch=0.0, roll=0.0, materials=None,
        shadows=True, extra=(), anchor="bottom", **material_args):
    """Place key so its bounds' bottom centre (anchor "bottom"), centre or top centre sits at `at`."""
    lo, hi = bounds(key)
    s = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
    y = {"bottom": lo[1], "center": (lo[1] + hi[1]) / 2, "top": hi[1]}[anchor]
    centre = [(lo[0] + hi[0]) / 2 * s[0], y * s[1], (lo[2] + hi[2]) / 2 * s[2]]
    rotation = quat(facing + 180.0, pitch, roll)
    position = sub3(at, qrot(rotation, centre))
    return scene.entity(name, [transform(position, scale=s, rotation=rotation),
                               model(key, materials, shadows, **material_args)] + list(extra), parent)


def place(scene, name, key, pos, yaw=0.0, scale=1.0, parent=None, pitch=0.0, roll=0.0, materials=None, shadows=True,
          extra=(), **material_args):
    """Place a model by its pivot (walls, floors and ceilings have corner pivots)."""
    return scene.entity(name, [transform(pos, yaw, pitch, roll, scale), model(key, materials, shadows, **material_args)] + list(extra), parent)


def size(key):
    lo, hi = bounds(key)
    return [h - l for l, h in zip(lo, hi)]


def top(key, scale=1.0):
    return bounds(key)[1][1] * scale


def box(scene, name, center, dims, material, parent=None, yaw=0.0, pitch=0.0, roll=0.0, shadows=True, shape="Cube", extra=()):
    """A primitive by its centre and full size in metres (primitives span -1..1)."""
    return scene.entity(name, [transform(center, yaw, pitch, roll, [d / 2 for d in dims]), mesh(shape, material, shadows)] + list(extra), parent)


# ---------------------------------------------------------------------------------------------
# Characters. Expanded skeletons are written into the scene (a saved Model reuses its node
# entities by name), so poses hold in the editor and sequences can animate the bones. Poses are
# given in model space: the rig faces -Z, its left is +X; Y up.

ARM = {"L": ("UpperArm_L", "lowerarm_l", "Hand_L"), "R": ("UpperArm_R", "lowerarm_r", "Hand_R")}
LEG = {"L": ("Thigh_L", "calf_l", "Foot_L"), "R": ("Thigh_R", "calf_r", "Foot_R")}


def rest_pose(key):
    nodes = RIGS[key]["Nodes"]
    world = []
    for n in nodes:
        parent_pos, parent_rot = world[n["parent"]] if n["parent"] >= 0 else ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0])
        world.append((add3(parent_pos, qrot(parent_rot, n["pos"])), qmul(parent_rot, n["rot"])))
    return world


HIP = (0.0, 0.876, 0.0)  # the rigs' pelvis in the rest pose; leaning pivots here


def solve_pose(key, pose, frame=(0.0, 0.0, 0.0, 1.0)):
    """Local transforms of a posed rig, plus the posed model-space (pos, rot) of every node.

    pose: bone -> one of
      ("turn", axis, degrees)       turn the bone about a model-space axis
      ("aim", joint, direction)     point the bone at a model-space direction, measured to `joint`
      ("at", joint, point)          point the bone so `joint` lies towards a model-space point
      ("reach", side, point, pole)  two-bone IK: arm ("L"/"R") or leg ("LL"/"LR") reaching point
    Bones are processed root first, so a bent spine carries the arms with it. Directions and
    points are in the upright frame: model space with the body's lean (frame) about HIP undone.
    """
    inverse = qconj(list(frame))

    def direction(v):
        return qrot(inverse, v)

    def point(v):
        return add3(qrot(inverse, sub3(v, HIP)), HIP)
    nodes = [dict(n) for n in RIGS[key]["Nodes"]]
    index = {n["name"]: i for i, n in enumerate(nodes)}
    rest = rest_pose(key)
    pending = dict(pose)
    # Expand reach into an aim of the upper bone (resolved when it is reached) and the lower.
    for bone, spec in list(pending.items()):
        if spec[0] == "reach":
            del pending[bone]
            side, goal, pole = spec[1], spec[2], spec[3]
            chain = ARM[side] if side in ARM else LEG[side[1]]
            pending[chain[0]] = ("ik", chain, goal, pole)
    world = []
    for i, n in enumerate(nodes):
        parent_pos, parent_rot = world[n["parent"]] if n["parent"] >= 0 else ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0])
        pos = add3(parent_pos, qrot(parent_rot, n["pos"]))
        rot = qmul(parent_rot, n["rot"])
        spec = pending.get(n["name"])
        if spec:
            def offset(joint):
                # The joint's position relative to this bone, in the bone's frame, from the rest pose.
                rest_pos, rest_rot = rest[i]
                return qrot(qconj(rest_rot), sub3(rest[index[joint]][0], rest_pos))

            turn = None
            if spec[0] == "turn":
                turn = qaxis(direction(spec[1]), spec[2])
            elif spec[0] == "aim":
                turn = qarc(qrot(rot, offset(spec[1])), direction(spec[2]))
            elif spec[0] == "at":
                turn = qarc(qrot(rot, offset(spec[1])), sub3(point(spec[2]), pos))
            elif spec[0] == "ik":
                upper, lower, end = spec[1]
                target, pole = point(spec[2]), direction(spec[3])
                l1 = length3(sub3(rest[index[lower]][0], rest[index[upper]][0]))
                l2 = length3(sub3(rest[index[end]][0], rest[index[lower]][0]))
                to = sub3(target, pos)
                d = min(length3(to), (l1 + l2) * 0.999)
                axis = norm3(to)
                # Elbow/knee: along the reach by a, then off it towards the pole by h.
                a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
                h = math.sqrt(max(l1 * l1 - a * a, 0.0))
                pole_dir = norm3(sub3(pole, scale3(axis, sum(p * q for p, q in zip(pole, axis)))))
                joint = add3(pos, add3(scale3(axis, a), scale3(pole_dir, h)))
                turn = qarc(qrot(rot, offset(lower)), sub3(joint, pos))
                pending[lower] = ("at", end, spec[2])
            if turn:
                rot = qmul(turn, rot)
                n["rot"] = [round(c, 6) for c in qmul(qconj(parent_rot), rot)]
        world.append((pos, rot))
    return nodes, index, world


def office_skin(key):
    """The atlas for a character: the pack's characters share PolygonOffice_Texture_01_A."""
    return standard(ATLAS, (1, 1, 1), 0.7)


class Character:
    def __init__(self, scene, name, key, pos, facing, pose, parent=None, lift=0.0, lean=0.0, skin=None):
        """A character standing at pos facing a compass direction. lean tips the whole body back
        (degrees) about its hips' axis; lift raises it (for sitting, lying)."""
        self.scene, self.name, self.key = scene, name, key
        self.frame = qaxis((1, 0, 0), lean)
        self.yaw = quat(facing + 180.0)
        self.rotation = qmul(self.yaw, self.frame)
        self.pos = [pos[0], pos[1] + lift, pos[2]]
        # Lean about the hips: the root moves so the pelvis stays put.
        root = add3(add3(self.pos, HIP), scale3(qrot(self.rotation, HIP), -1.0))
        rig = RIGS[key]
        self.nodes, self.index, self.world = solve_pose(key, pose, self.frame)
        self.root = scene.entity(name, [transform(root, rotation=[round(c, 6) for c in self.rotation]),
                                        {"Type": "Model", "ModelPath": rig["ModelPath"], "Compact": False,
                                         "BakedImportScale": rig["BakedImportScale"]}], parent)
        self.bones = []
        for n in self.nodes:
            components = [{"Type": "Transform", "Position": n["pos"], "Rotation": n["rot"], "Scale": n["scale"]}]
            for c in n["comps"]:
                if c["Type"] == "Mesh":
                    c = {k: v for k, v in c.items() if k != "ImportedMaterialDefaults"}
                    c["Material"] = skin or office_skin(key)
                components.append(c)
            owner = self.bones[n["parent"]] if n["parent"] >= 0 else self.root
            self.bones.append(scene.entity(n["name"], components, owner))

    def bone(self, name):
        return self.bones[self.index[name]]

    def to_world(self, upright_point):
        return add3(self.pos, qrot(self.yaw, upright_point))

    def joint(self, name):
        """A joint's posed position in the upright frame."""
        return add3(qrot(self.frame, sub3(self.world[self.index[name]][0], HIP)), HIP)

    def attach(self, bone, key, upright_pos, upright_rot=(0, 0, 0, 1), name=None, materials=None, scale=1.0, extra=()):
        """Parent a prop to a bone, posed in the upright frame (so it follows animated bones)."""
        pos, rot = self.world[self.index[bone]]
        model_pos = add3(qrot(qconj(self.frame), sub3(upright_pos, HIP)), HIP)
        model_rot = qmul(qconj(self.frame), list(upright_rot))
        local_pos = qrot(qconj(rot), sub3(model_pos, pos))
        local_rot = qmul(qconj(rot), model_rot)
        return self.scene.entity(name or key, [transform(local_pos, scale=scale, rotation=[round(c, 6) for c in local_rot]),
                                               model(key, materials)] + list(extra), self.bone(bone))

    def wear(self, bone, key):
        """Synty attachments are modelled at their bone's pivot, aligned with the character."""
        _, rot = self.world[self.index[bone]]
        return self.scene.entity(key, [transform((0, 0, 0), rotation=[round(c, 6) for c in qconj(rot)]), model(key)], self.bone(bone))

    def local_rotation(self, pose, bone):
        """A bone's local rotation under another pose (for animation keys)."""
        nodes, index, _ = solve_pose(self.key, pose, self.frame)
        return nodes[index[bone]]["rot"]


def seated(extra=None, knee_spread=0.12, foot_forward=0.62, hip=(0.0, 0.0)):
    """Legs for sitting on a 0.47 m seat (the root is lowered by SIT_LIFT)."""
    pose = {}
    for side, x in (("L", 1), ("R", -1)):
        foot = (x * (0.1 + knee_spread * 0.4), 0.08 - SIT_LIFT, -foot_forward)
        pose[LEG[side][0]] = ("reach", "L" + side, foot, (x * knee_spread, 0.6, -1.0))
        pose[LEG[side][2]] = ("aim", "ball_" + side.lower(), (0.0, -0.25, -1.0))
    pose.update(extra or {})
    return pose


SIT_LIFT = -0.38  # pelvis 0.876 standing -> ~0.5 seated


# ---------------------------------------------------------------------------------------------
# The building

W, D = 25.0, 17.5


def wall(scene, key, x, z, direction, parent, **material_args):
    """A 2.5 m wall segment from (x, z) running E/N/W/S (corner pivot, 0.15 m thick to its right).
    Synty walls are single-sided: only the face on their right (local -Z) side renders, so run each
    wall with the room on its right."""
    yaw = {"E": 0.0, "N": -90.0, "W": 180.0, "S": 90.0}[direction]
    return place(scene, key.replace("SM_Bld_", ""), key, (x, 0, z), yaw, parent=parent, **material_args)


def wall_run(scene, keys, x, z, direction, parent, overrides=None):
    dx, dz = {"E": (2.5, 0), "N": (0, 2.5), "W": (-2.5, 0), "S": (0, -2.5)}[direction]
    out = []
    for i, key in enumerate(keys):
        if key:
            out.append(wall(scene, key, x + dx * i, z + dz * i, direction, parent, **((overrides or {}).get(i, {}))))
    return out


RIGHT = {"E": (0.0, -1.0), "N": (1.0, 0.0), "W": (0.0, 1.0), "S": (-1.0, 0.0)}
STEP = {"E": (2.5, 0.0), "N": (0.0, 2.5), "W": (-2.5, 0.0), "S": (0.0, -2.5)}
OPPOSITE = {"E": "W", "W": "E", "N": "S", "S": "N"}


def partition(scene, keys, x, z, direction, parent, blinds=False):
    """An interior glass wall seen from both rooms. Synty walls render one face only (their right), so
    each segment gets a mirrored twin facing the other room; blinds=True hangs blinds in both."""
    (dx, dz), (rx, rz) = STEP[direction], RIGHT[direction]
    for i, key in enumerate(keys):
        if not key:
            continue
        start = (x + dx * i, z + dz * i)
        thickness = -bounds(key)[0][2]
        twin = (start[0] + dx + rx * thickness, start[1] + dz + rz * thickness)
        wall(scene, key, start[0], start[1], direction, parent)
        # The twin's glass is nearly clear, so the two panes don't double the tint.
        twin_glass = {i: glass(opacity=0.05) for i, part in enumerate(PARTS[key]["Parts"]) if "Glass" in part_slot(key, part)}
        wall(scene, key, twin[0], twin[1], OPPOSITE[direction], parent, overrides=twin_glass)
        if blinds:
            for (bx, bz), d in ((start, direction), (twin, OPPOSITE[direction])):
                wall(scene, "SM_Bld_Wall_Glass_Window_Blinds_Down_01", bx, bz, d, parent)


def build_shell(scene):
    shell = scene.group("Building")
    floors = scene.group("Floors", parent=shell)
    for ix in range(10):
        for iz in range(7):
            x, z = ix * 2.5, iz * 2.5
            key = "SM_Bld_Floor_Carpet_01"
            if x < 7.5 and z < 7.5 and not (z >= 5.0 and x >= 2.5):
                key = "SM_Bld_Floor_Tiles_01"
            if x < 7.5 and z >= 12.5:
                key = "SM_Bld_Floor_Wood_01"
            tint = (1, 1, 1)
            if x >= 17.5 and z >= 12.5:
                # The server room's raised floor (SM_Bld_Floor_Panel_01 is only a trim strip).
                key, tint = "SM_Bld_Floor_Concrete_01", (0.55, 0.57, 0.6)
            place(scene, "Floor", key, (x, 0, z + 2.5), parent=floors, roughness=0.9, tint=tint)
    ceiling = scene.group("Ceiling", parent=shell)
    holes = {(22.5, 10.0)}  # the panel that fell in the corridor
    for ix in range(10):
        for iz in range(7):
            x, z = ix * 2.5, iz * 2.5
            if (x, z) in holes:
                continue
            place(scene, "Ceiling Tile", "SM_Bld_Ceiling_Panel_01", (x, CEILING, z + 2.5), parent=ceiling, shadows=False, roughness=0.95)
    # Above the fallen panel: the void, ducting and cables.
    box(scene, "Ceiling Void", (23.75, CEILING + 0.4, 11.25), (2.5, 0.05, 2.5), standard(None, (0.02, 0.02, 0.02), 1.0), ceiling)
    walls = scene.group("Walls", parent=shell)
    blank, glass_wall, glass_door = "SM_Bld_Wall_Blank_01", "SM_Bld_Wall_Glass_01", "SM_Bld_Wall_Glass_Door_01"
    # North: the boss's windows, floor-to-ceiling storm glass over the pit, the server room's blank wall.
    north = scene.group("North Wall", parent=walls)
    window = "SM_Bld_Wall_Blank_Window_01"
    wall_run(scene, [window, window, window], 0.0, D, "E", north,
             {i: {"overrides": {1: graph("RainGlass", {"Opacity": 0.14})}} for i in range(3)})
    wall_run(scene, [glass_wall] * 4, 7.5, D, "E", north, {i: {"overrides": {1: graph("RainGlass")}} for i in range(4)})
    wall_run(scene, [blank] * 3, 17.5, D, "E", north)
    for i in range(3):
        place(scene, "Window Blinds", "SM_Bld_Wall_Window_Blinds_Down_01", (2.5 * i, 0, D), parent=north)
    # South: blank, with the lift.
    south = scene.group("South Wall", parent=walls)
    keys = [blank] * 10
    keys[5] = None
    wall_run(scene, keys, W, 0.0, "W", south)
    # The lift's wall piece carries its shaft on +Z: turn it so the shaft is behind the wall.
    place(scene, "Lift Wall", "SM_Bld_Wall_Blank_Elevator_01", (12.5, 0, 0.0), 180.0, parent=south)
    place(scene, "Lift Car", "SM_Bld_Elevator_01", (12.5, 0, -0.15), 180.0, parent=south)
    # West and east outer walls.
    west = scene.group("West Wall", parent=walls)
    wall_run(scene, [blank] * 7, 0.0, 0.0, "N", west)
    east = scene.group("East Wall", parent=walls)
    wall_run(scene, [blank] * 7, W, D, "S", east)
    # The facade outside the storm glass: slab edges and cladding over the blank wall sections, so the
    # building reads from the opening shot (the walls render from inside only).
    facade = scene.group("Facade", parent=walls)
    cladding = standard(None, (0.05, 0.055, 0.06), 0.35, metallic=0.6)
    box(scene, "Slab Edge", (W / 2, -0.35, D + 0.2), (W + 0.6, 0.7, 0.4), cladding, facade)
    box(scene, "Slab Edge", (W / 2, CEILING + 0.4, D + 0.2), (W + 0.6, 0.8, 0.4), cladding, facade)
    for x0, x1 in ((0.0, 7.5), (17.5, W)):
        box(scene, "Cladding", ((x0 + x1) / 2, CEILING / 2, D + 0.1), (x1 - x0 + 0.3, CEILING, 0.2), cladding, facade)
    for x in (7.5, 10.0, 12.5, 15.0, 17.5):
        box(scene, "Mullion", (x, CEILING / 2, D + 0.06), (0.12, CEILING, 0.12), cladding, facade)
    # Interior glass: the boss's office (blinds down), the server room, the conference room.
    inner = scene.group("Interior Glass", parent=walls)
    # The boss's office: glass walls with the blinds down (the blinds models are only the slats).
    partition(scene, [glass_wall, None, glass_wall], 0.0, 12.65, "E", inner, blinds=True)
    partition(scene, [None, glass_door, None], 0.0, 12.65, "E", inner)
    partition(scene, [glass_wall, glass_wall], 7.35, 12.65, "N", inner, blinds=True)
    partition(scene, [glass_wall, glass_door, glass_wall], 17.5, 12.65, "E", inner)
    partition(scene, [glass_wall, glass_wall], 17.5, 12.65, "N", inner)
    partition(scene, [glass_wall, glass_door, glass_wall], 17.5, 7.5, "E", inner)
    partition(scene, [glass_wall, glass_wall, glass_wall], 17.5, 0.0, "N", inner)
    for x, z in [(7.5, 12.5), (17.5, 12.5), (17.5, 7.5), (7.5, D - 0.1), (17.5, D - 0.1)]:
        put(scene, "Pillar", "SM_Bld_Pillar_Interior_01", (x, 0, z), parent=walls)
    return shell


def ceiling_light(scene, name, x, z, parent, on=0.0, color=(1.0, 0.96, 0.9), intensity=6.0, flicker=None):
    """A recessed panel; on = its brightness (0 off). Returns the light entity if lit."""
    put(scene, name + " Panel", "SM_Bld_Ceiling_Panel_Light_01", (x, CEILING - 0.035, z), parent=parent, shadows=False,
        materials=[standard(ATLAS, (1, 1, 1), 0.5, emissive=color, emissive_intensity=on * 3.0)])
    if on <= 0:
        return None
    return scene.entity(name, [transform((x, CEILING - 0.08, z), pitch=90.0),
                               light("Rectangle", color, intensity * on, 7.0, RectangleWidth=0.9, RectangleHeight=0.9)], parent)


def build_lighting(scene):
    lights = scene.group("Ceiling Lights")
    out = {}
    # Most of the floor sleeps: motion sensors gave up hours ago. A few panels are still on.
    lit = {(13.75, 8.75): ("Hero Panel", 1.0), (8.75, 8.75): ("Sleeper Panel", 0.25), (21.25, 11.25): ("Corridor Panel", 0.8),
           (3.75, 3.75): ("Kitchen Panel", 0.5), (11.25, 16.25): ("Rage Quit Panel", 0.3), (13.75, 1.25): ("Lobby Panel", 0.15)}
    for x in [1.25 + 2.5 * i for i in range(10)]:
        for z in [1.25 + 2.5 * i for i in range(7)]:
            if 17.5 < x and 12.5 < z:
                continue  # the server room has its own strips
            if x == 23.75 and z == 11.25:
                continue  # the hole
            name, on = lit.get((x, z), ("Ceiling Panel", 0.0))
            light_entity = ceiling_light(scene, name, x, z, lights, on)
            if light_entity:
                out[name] = light_entity
    return out


# ---------------------------------------------------------------------------------------------
# Outside: the storm, rain on the glass and the city 30 floors down.


def build_outside(scene):
    outside = scene.group("Outside")
    city = scene.group("City", parent=outside)
    r = random.Random(77)
    towers = []
    for i in range(70):
        x = r.uniform(-260, 300)
        z = r.uniform(70, 520)
        if abs(x - 12) < 30 and z < 110:
            continue
        w, d = r.uniform(18, 45), r.uniform(18, 45)
        h = r.uniform(40, 210) * (1.0 + 0.6 * math.exp(-((x - 40) / 120) ** 2))
        towers.append((x, z, w, d, h))
    for x, z, w, d, h in towers:
        base = -95.0
        box(scene, "Tower", (x, base + h / 2, z), (w, h, d), graph("CityWindows", {"Intensity": r.uniform(2.5, 5.0)}), city, shadows=False)
        if h > 120:
            scene.entity("Aircraft Warning Light", [transform((x, base + h + 0.8, z), scale=0.8), mesh("Sphere", graph("BlinkLight", {
                "Intensity": 60.0, "Rate": 0.6, "Duty": 0.35, "Phase": r.random()}), False)], city)
    # Street glow far below, so the towers stand on something.
    box(scene, "Street Haze", (20, -96, 260), (700, 1, 500), standard(None, (0.02, 0.02, 0.02), 1.0, emissive=(1.0, 0.55, 0.25), emissive_intensity=0.06), city, shadows=False)
    # Rain: a dense sheet just outside the glass (where the opening shot looks through it) and a
    # lighter one further out. Streaks are thin, so they need size and brightness to read at night.
    rain_look = dict(Shape="Box", ConeAngle=0.0, Size=[0.03, 0.045], EndSize=1.0, StartColor=[0.55, 0.6, 0.75],
                     StartColor2=[0.7, 0.75, 0.9], EndColor=[0.55, 0.6, 0.75], StartAlpha=0.75, EndAlpha=0.5, FadeIn=0.05,
                     Gravity=9.0, Blend="Additive", Alignment="Stretched", StretchFactor=0.11, Rotation=[0, 0],
                     AngularVelocity=[0, 0], SoftParticleDistance=0.0)
    # The near sheet stays in a band just outside the glass: the opening shot's camera comes to
    # within 1.1 m of it, and a streak passing the lens fills the frame.
    rain = scene.entity("Rain", [transform((12.5, 4.0, 17.85)), particles(
        BoxSize=[20.0, 1.0, 0.5], EmissionRate=2200.0, MaxParticles=6000, Lifetime=[0.9, 1.2], Speed=[6.0, 8.0], Intensity=1.6,
        **dict(rain_look, Size=[0.004, 0.007], StretchFactor=0.045, StartAlpha=0.6))], outside)
    far_rain = scene.entity("Rain (Far)", [transform((12.5, 6.0, 30.0)), particles(
        BoxSize=[40.0, 1.0, 16.0], EmissionRate=1500.0, MaxParticles=6000, Lifetime=[1.2, 1.6], Speed=[6.0, 8.0], Intensity=1.4,
        **rain_look)], outside)
    # Speed is along the shape's +Y; turn the emitter over so it rains down (with a little wind).
    rain["Components"][0]["Rotation"] = quat(0.0, 180.0 - 3.0)
    far_rain["Components"][0]["Rotation"] = quat(0.0, 180.0 - 8.0)
    # Lightning: bolts far out over the city, scaled to nothing between flashes by the Storm clip.
    bolts = []
    for i, (x, z, h, seed) in enumerate([(-70.0, 330.0, 260.0, 3.0), (95.0, 420.0, 300.0, 11.0), (20.0, 260.0, 220.0, 7.0)]):
        bolts.append(scene.entity("Lightning Bolt", [transform((x, h / 2 - 95.0, z), scale=(h * 0.12, 1.0, h / 2), pitch=-90.0),
                                                      mesh("Plane", graph("Lightning", {"Seed": seed}), False)], outside))
    # With a procedural sky every directional light follows the sun or moon, so the flash is a
    # distant spot through the storm glass (its shadows throw the mullions across the pit).
    flash_at = (13.0, 7.5, 46.0)
    flash = scene.entity("Lightning Flash", [transform(flash_at, *look_angles(flash_at, (12.5, 0.0, 10.0))),
                                             light("Spot", (0.72, 0.8, 1.0), 0.0, 90.0, shadows=True, inner=14.0, outer=24.0,
                                                   ShadowBias=0.4, ShadowNormalBias=1.0)], outside)
    scene.entity("Moonlight", [transform((12.5, 30.0, 60.0)), light("Directional", (0.45, 0.55, 0.85), 0.35, 100.0, shadows=True,
                                                                     ShadowDistance=40.0)], outside)
    storm = scene.clip("Storm", 23.0)
    # Rain on the glass and the thunder, timed to this clip's flashes; the floor's room tone.
    sound(scene, "Storm Sound", "Storm", (12.5, 1.5, 15.0), outside, volume=0.9, spatial=0.0)
    sound(scene, "Room Tone", "OfficeAir", (12.5, 1.5, 8.0), outside, volume=0.22, spatial=0.0)
    # Two flash groups per loop: a double strike and a long rolling one.
    def strike(times, peak):
        keys = []
        for start, length, value in times:
            keys += [(start - 0.02, 0.0, "Hold"), (start, value * peak, "Hold"), (start + length, 0.0, "Hold")]
        return keys
    pattern = [(3.0, 0.08, 1.0), (3.2, 0.05, 0.5), (3.35, 0.12, 0.8), (14.0, 0.1, 0.7), (14.25, 0.3, 1.0), (14.7, 0.06, 0.4)]
    storm.track(flash, "Light", "Intensity", [(0.0, 0.0, "Hold")] + strike(pattern, 2500.0) + [(23.0, 0.0, "Hold")])
    # The whole frame blinks with each strike, wherever the tour is.
    camera = next(e for e in scene.entities if e["Name"] == "Main Camera")
    base = next(c for c in camera["Components"] if c["Type"] == "PostProcess")["ExposureCompensation"]
    exposure = [(0.0, base, "Hold")]
    for start, length, value in pattern:
        exposure += [(start, base + 1.1 * value, "Hold"), (start + length, base, "Hold")]
    storm.track(camera, "PostProcess", "ExposureCompensation", exposure + [(23.0, base, "Hold")], label="Camera")
    for i, bolt in enumerate(bolts):
        windows = [pattern[:3], pattern[3:], pattern[3:5]][i]
        on = list(bolt["Components"][0]["Scale"])
        hidden = [0.001, 0.001, 0.001]
        keys = [(0.0, hidden, "Hold")]
        for start, length, _ in windows:
            keys += [(start, on, "Hold"), (start + length, hidden, "Hold")]
        storm.track(bolt, "Transform", "Scale", keys + [(23.0, hidden, "Hold")], label="Bolt %d" % (i + 1))
        bolt["Components"][0]["Scale"] = hidden
    return outside, storm


# ---------------------------------------------------------------------------------------------
# Desks


def monitor_glow(scene, at, facing, parent, color=(0.55, 0.7, 1.0), intensity=0.8, range_=2.6):
    """A soft fill in front of a lit screen, so it lights the face looking at it."""
    f = math.radians(facing)
    pos = (at[0] + math.sin(f) * 0.12, at[1] + 0.3, at[2] + math.cos(f) * 0.12)
    return scene.entity("Screen Glow", [transform(pos), light("Point", color, intensity, range_)], parent)


def front(at, facing, distance, dy=0.0, side=0.0):
    """A point `distance` in front of `at` along a compass facing, `side` to its right."""
    f = math.radians(facing)
    return (at[0] + math.sin(f) * distance + math.cos(f) * side, at[1] + dy, at[2] + math.cos(f) * distance - math.sin(f) * side)


def desk(scene, name, seat, facing, parent, monitor="SM_Prop_Computer_Monitor_01", screens=(), chair="SM_Prop_Chair_03",
         chair_turn=0.0, chair_back=0.0, chair_entity_name=None, items=(), lamp=None, glow=None, keyboard=True):
    """A workstation for someone sitting at `seat` facing `facing`; returns the desk group.
    items: (key, forward, side, yaw, [y]) relative to the desk top centre (forward away from the seat)."""
    group = scene.group(name, parent=parent)
    centre = front(seat, facing, 0.62)
    put(scene, "Desk", "SM_Prop_Desk_01", centre, facing + 180.0, parent=group)
    top_y = top("SM_Prop_Desk_01")
    screen_at = front((centre[0], top_y, centre[2]), facing, 0.22)
    if monitor:
        put(scene, "Monitor", monitor, screen_at, facing + 180.0, parent=group, screens=screens)
        if glow:
            monitor_glow(scene, (screen_at[0], top_y + 0.35, screen_at[2]), facing + 180.0, group, *glow)
    if keyboard:
        put(scene, "Keyboard", "SM_Prop_Computer_Keyboard_01", front((centre[0], top_y, centre[2]), facing, -0.12), facing + 180.0, parent=group)
        put(scene, "Mouse", "SM_Prop_Computer_Mouse_01", front((centre[0], top_y, centre[2]), facing, -0.12, side=0.42), facing + 180.0, parent=group)
    if chair:
        chair_at = front(seat, facing, -chair_back)
        put(scene, chair_entity_name or "Chair", chair, chair_at, facing + chair_turn, parent=group, atlas=ATLAS)
    for item in items:
        key, forward, side, yaw = item[:4]
        y = item[4] if len(item) > 4 else top_y
        put(scene, key.replace("SM_Prop_", "").replace("_", " "), key, front((centre[0], y, centre[2]), facing, forward, side=side),
            facing + 180.0 + yaw, parent=group)
    if lamp:
        put(scene, "Desk Lamp", "SM_Prop_DeskLamp_06", front((centre[0], top_y, centre[2]), facing, 0.2, side=-0.75), facing + 160.0, parent=group)
        scene.entity("Desk Lamp Light", [transform(front((centre[0], top_y + 0.45, centre[2]), facing, 0.1, side=-0.6),
                                                   *look_angles(front((0, top_y + 0.45, 0), facing, 0.1, side=-0.6), front((0, top_y, 0), facing, -0.1, side=-0.2))),
                                         light("Spot", lamp, 2.5, 3.5, shadows=True, inner=30.0, outer=55.0)], group)
    return group


def pod(scene, name, cx, cz, parent, seats):
    """Four desks back to back around a low divider; seats: {slot: kwargs} with slots NW, NE, SW, SE
    (north-row seats face south, south-row seats face north)."""
    group = scene.group(name, parent=parent)
    for x in (cx - 1.0, cx + 1.0):
        put(scene, "Divider", "SM_Prop_CubicalWall_01", (x, 0, cz), 0.0, parent=group)
    out = {}
    for slot, (dx, dz, facing) in {"SW": (-1, -1, 0.0), "SE": (1, -1, 0.0), "NW": (-1, 1, 180.0), "NE": (1, 1, 180.0)}.items():
        kwargs = dict(seats.get(slot, {}))
        seat = (cx + dx * 1.0, 0.0, cz + dz * 1.32)
        out[slot] = (seat, facing)
        if kwargs.pop("skip", False):
            continue
        desk(scene, "%s %s" % (name, slot), seat, facing, group, **kwargs)
    return group, out


def energy_pyramid(scene, at, facing, parent):
    """Ten empty cans: four, three, two, one."""
    group = scene.group("Energy Drink Pyramid", parent=parent)
    w, h = 0.12, top("SM_Prop_EnergyDrink_01")
    for row, count in enumerate([4, 3, 2, 1]):
        for i in range(count):
            side = (i - (count - 1) / 2) * w
            p = front((at[0], at[1] + row * h, at[2]), facing, 0.0, side=side)
            put(scene, "Can", "SM_Prop_EnergyDrink_01", p, facing + rng.uniform(-30, 30), parent=group)
    return group


def build_pit(scene, ceiling_lights):
    pit = scene.group("Dev Pit")
    code = lambda seed, speed=0.6, brightness=2.2: graph("CodeScreen", {"Seed": seed, "Scroll Speed": speed, "Brightness": brightness})
    cool = ((0.5, 0.65, 1.0), 0.9, 2.8)
    mess = [("SM_Prop_Cup_Coffee_Disposable_Closed_01", -0.25, 0.65, 0), ("SM_Prop_Can_Soda_01", -0.3, -0.7, 0)]
    # Pod D (south-east): the last developer still typing, and the one who went home mid-compile.
    pod_d, seats_d = pod(scene, "Pod D", 14.75, 9.0, pit, {
        "SW": dict(monitor="SM_Prop_Computer_Monitor_Triple_01", screens=[code(1.0, 0.9), code(2.0, 1.6), code(3.0, 0.4)],
                   chair="SM_Prop_Chair_04", lamp=(1.0, 0.82, 0.6), glow=cool, chair_back=0.08,
                   items=[("SM_Prop_Cup_Coffee_Disposable_Closed_01", -0.28, 0.66, 10), ("SM_Prop_Cup_01", -0.05, -0.85, 40),
                          ("SM_Prop_Pills_01", -0.32, -0.62, 0)]),
        "SE": dict(screens=[code(5.0, 2.5, 1.6)], chair="SM_Prop_Chair_04", chair_turn=35.0, chair_back=0.5, glow=((0.5, 0.65, 1.0), 0.8, 2.2),
                   items=[("SM_Prop_Cup_02", -0.2, 0.6, 0), ("SM_Prop_Plant_09", 0.25, 0.75, 0), ("SM_Prop_Photo_01", 0.2, -0.75, 20)]),
        "NW": dict(chair="SM_Prop_Chair_04", items=[("SM_Prop_Plant_11", 0.22, 0.7, 0), ("SM_Prop_Folder_Holder_01", 0.25, -0.75, 0)]),
        "NE": dict(chair="SM_Prop_Chair_04", chair_turn=-20.0, items=[("SM_Prop_Book_Group_01", 0.25, 0.3, 0)]),
    })
    hero_seat, hero_facing = seats_d["SW"]
    desk_centre = front(hero_seat, hero_facing, 0.62)
    energy_pyramid(scene, front((desk_centre[0], top("SM_Prop_Desk_01"), desk_centre[2]), hero_facing, 0.05, side=0.62), hero_facing + 180.0, pod_d)
    for i in range(14):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.25, 1.1)
        p = (hero_seat[0] + 0.7 + math.cos(a) * rr, 0.0, hero_seat[2] - 0.3 + math.sin(a) * rr * 0.6)
        put(scene, "Crumpled Paper", "SM_Prop_Rubbish_01", p, rng.uniform(0, 360), parent=pod_d)
    put(scene, "Bin", "SM_Prop_Bin_01", (hero_seat[0] + 0.75, 0, hero_seat[2] + 0.15), 0.0, parent=pod_d)
    for i, (dx, dz) in enumerate([(-0.55, 0.15), (-0.7, -0.15), (-0.45, -0.3)]):
        put(scene, "Empty Can", "SM_Prop_EnergyDrink_01", (hero_seat[0] + dx, 0.05 if i else 0.0, hero_seat[2] + dz), rng.uniform(0, 360),
            pitch=90.0 if i else 0.0, parent=pod_d, anchor="center" if i else "bottom")
    # Pod C (south-west): asleep on the keyboard.
    pod_c, seats_c = pod(scene, "Pod C", 10.25, 9.0, pit, {
        "SW": dict(screens=[graph("Screensaver", {"Brightness": 1.4})], chair="SM_Prop_Chair_03", glow=((0.6, 0.5, 1.0), 0.45, 2.4), chair_back=0.12,
                   items=[("SM_Prop_Cup_01", -0.3, 0.6, 0), ("SM_Prop_Cup_Styrofoam_01", -0.15, 0.78, 0), ("SM_Prop_Pills_01", -0.32, -0.55, 0),
                          ("SM_Prop_Note_01", 0.12, -0.15, 0, top("SM_Prop_Desk_01") + 0.45), ("SM_Prop_Plant_11", 0.25, -0.75, 0)]),
        "SE": dict(chair="SM_Prop_Chair_03", chair_back=0.3, items=[("SM_Prop_Cup_Coffee_Disposable_Closed_01", -0.2, 0.6, 0),
                                                                     ("SM_Prop_Party_Hat_01", 0.1, -0.5, 0)]),
        "NW": dict(chair="SM_Prop_Chair_03", items=[("SM_Prop_Calculator_01", -0.2, 0.5, 15), ("SM_Prop_Lunchbox_01", 0.15, -0.7, 0)]),
        "NE": dict(chair="SM_Prop_Chair_03", chair_turn=60.0, chair_back=0.7, items=[("SM_Prop_Figure_Knight_01", 0.25, 0.8, 30),
                                                                                    ("SM_Prop_PuzzleCube_01", -0.25, 0.55, 20)]),
    })
    # Pod A (north-west): the rage quit. Pod B (north-east): QA.
    pod_a, seats_a = pod(scene, "Pod A", 10.25, 14.9, pit, {
        "NE": dict(monitor=None, keyboard=False, chair=None,
                   items=[("SM_Prop_Box_01", 0.05, 0.25, 15), ("SM_Prop_Paper_01", -0.25, -0.4, 5)]),
        "NW": dict(chair="SM_Prop_Chair_02", items=[("SM_Prop_Plant_03", 0.25, 0.6, 0), ("SM_Prop_Photo_02", 0.22, -0.7, 15)]),
        "SW": dict(chair="SM_Prop_Chair_02", chair_turn=-25.0, chair_back=0.4, items=[("SM_Prop_Cup_02", -0.2, 0.6, 0), ("SM_Prop_Party_Hat_02", 0.1, -0.6, 0)]),
        "SE": dict(chair="SM_Prop_Chair_02", screens=[code(9.0, 0.2, 1.0)], glow=((0.5, 0.65, 1.0), 0.5, 2.0),
                   items=[("SM_Prop_Stapler_01", -0.25, 0.55, 30)]),
    })
    quit_seat, quit_facing = seats_a["NE"]
    quit_centre = front(quit_seat, quit_facing, 0.62)
    # The monitor went over the divider... no: onto the floor, still on, face up.
    put(scene, "Thrown Monitor", "SM_Prop_Computer_Monitor_02", (quit_seat[0] + 0.55, 0.12, quit_seat[2] - 0.15), 200.0, pitch=-80.0,
        parent=pod_a, screens=[graph("BlueScreen")], anchor="center")
    scene.entity("BSOD Glow", [transform((quit_seat[0] + 0.55, 0.45, quit_seat[2] - 0.15)), light("Point", (0.2, 0.45, 1.0), 1.0, 2.5)], pod_a)
    put(scene, "Thrown Keyboard", "SM_Prop_Computer_Keyboard_01", (quit_seat[0] - 0.4, 0.0, quit_seat[2] + 0.55), 130.0, roll=8.0, parent=pod_a)
    for i in range(7):
        put(scene, "Letter", "SM_Prop_Paper_01", (quit_seat[0] + rng.uniform(-0.9, 0.9), 0.002 + i * 0.001, quit_seat[2] + rng.uniform(-0.6, 0.9)),
            rng.uniform(0, 360), parent=pod_a)
    box_top = (quit_centre[0], top("SM_Prop_Desk_01") + top("SM_Prop_Box_01") - 0.02, quit_centre[2])
    put(scene, "Desk Plant (packed)", "SM_Prop_Plant_09", front(box_top, quit_facing, 0.12, side=0.32), 0.0, parent=pod_a)
    put(scene, "Photo (packed)", "SM_Prop_Photo_01", front(box_top, quit_facing, 0.05, side=0.15), 160.0, pitch=-25.0, parent=pod_a)
    put(scene, "Mug (packed)", "SM_Prop_Cup_Pens_01", front(box_top, quit_facing, -0.05, side=0.35), 40.0, parent=pod_a)
    spinning_chair = put(scene, "Spinning Chair", "SM_Prop_Chair_02", front(quit_seat, quit_facing, -0.35), quit_facing, parent=pod_a)
    pod_b, seats_b = pod(scene, "Pod B", 14.75, 14.9, pit, {
        "NW": dict(screens=[code(7.0, 0.3, 1.3)], chair="SM_Prop_Chair_06", glow=((0.5, 0.65, 1.0), 0.6, 2.0),
                   items=[("SM_Wep_ToyGun_Rifle_01", -0.25, 0.3, 80), ("SM_Wep_ToyGun_SMG_01", -0.3, -0.6, 120), ("SM_Prop_Figure_Goblin_01", 0.25, 0.75, 20)]),
        "NE": dict(chair="SM_Prop_Chair_06", items=[("SM_Prop_Laptop_01", -0.05, 0.0, 0), ("SM_Prop_Lunchbox_01", 0.1, 0.65, 10)], monitor=None,
                   keyboard=False),
        "SW": dict(chair="SM_Prop_Chair_06", chair_turn=15.0, items=[("SM_Prop_Spaceship_01", 0.25, 0.7, 40), ("SM_Prop_Party_Hat_03", 0.0, -0.6, 0)]),
        "SE": dict(chair="SM_Prop_Chair_06", items=[("SM_Prop_Plant_02", 0.25, 0.75, 0), ("SM_Prop_Cup_01", -0.2, -0.6, 0)]),
    })
    qa_seat, qa_facing = seats_b["NW"]
    qa_screen = front((qa_seat[0], top("SM_Prop_Desk_01"), qa_seat[2]), qa_facing, 0.84)
    for i in range(9):
        side = -0.36 + (i % 5) * 0.18
        up = 0.62 if i < 5 else 0.12
        p = front((qa_screen[0], top("SM_Prop_Desk_01") + up, qa_screen[2]), qa_facing, 0.0 if i < 5 else 0.05, side=side)
        put(scene, "Sticky Note", "SM_Prop_Note_0%d" % (i % 5 + 1), p, qa_facing + rng.uniform(-12, 12), parent=pod_b)
    # Foam darts everywhere: the nerf war of 1 AM.
    for i in range(16):
        p = (rng.uniform(9.0, 16.5), 0.012, rng.uniform(11.0, 13.4))
        box(scene, "Foam Dart", p, (0.018, 0.018, 0.07), standard(None, (1.0, 0.45, 0.05), 0.8), pit, yaw=rng.uniform(0, 360), pitch=90.0)
    # The hanging TVs over the aisle: the gold master countdown, and the build dashboard on the back.
    tv_at = (12.5, 2.25, 12.0)
    tvs = scene.group("Hanging TVs", tv_at, parent=pit)
    lo, hi = bounds("SM_Prop_TV_Wall_01")
    put(scene, "Countdown TV", "SM_Prop_TV_Wall_01", (0, 0, -0.13), 180.0, parent=tvs, anchor="center",
        screens=[graph("Countdown", {"Brightness": 2.2})])
    put(scene, "Build Status TV", "SM_Prop_TV_Wall_01", (0, 0, 0.13), 0.0, parent=tvs, anchor="center",
        screens=[graph("BuildStatus", {"Brightness": 1.8})])
    for side in (-0.6, 0.6):
        box(scene, "TV Pole", (side, (CEILING - tv_at[1]) / 2 + 0.4, 0), (0.03, CEILING - tv_at[1] - 0.4, 0.03), standard(None, (0.2, 0.2, 0.22), 0.4, 0.8), tvs)
    scene.entity("Countdown Glow", [transform((0, -0.7, -0.4)), light("Point", (1.0, 0.15, 0.08), 0.5, 3.5)], tvs)
    scene.entity("Status Glow", [transform((0, -0.3, 0.5)), light("Point", (1.0, 0.2, 0.15), 0.4, 3.5)], tvs)
    # The war-room whiteboard on wheels.
    board = put(scene, "Whiteboard", "SM_Prop_Whiteboard_02", (12.4, 0, 11.35), 200.0, parent=pit)
    scene.entity("Whiteboard Marker", [transform((12.4, 1.25, 11.33), 20.0), decal((1.5, 1.02, 0.25), graph_name="Whiteboard", sort=1)], pit)
    put(scene, "Plant", "SM_Prop_Plant_05", (8.2, 0, 11.6), 90.0, parent=pit)
    put(scene, "Plant", "SM_Prop_Plant_01", (16.9, 0, 6.0), 0.0, scale=1.3, parent=pit)
    put(scene, "Coat Rack", "SM_Prop_CoatRack_01", (17.0, 0, 11.9), 0.0, parent=pit)
    put(scene, "Printer", "SM_Prop_Printer_01", (8.4, 0.75, 6.0), 90.0, parent=pit)
    put(scene, "Printer Table", "SM_Prop_Table_01", (8.6, 0, 6.0), 90.0, scale=(0.5, 1, 0.5), parent=pit)
    put(scene, "Swiss Ball", "SM_Prop_SwissBall_01", (12.6, 0, 6.3), 0.0, parent=pit)
    return pit, dict(hero=(hero_seat, hero_facing), sleeper=seats_c["SW"], quit=(quit_seat, quit_facing),
                     chair=spinning_chair, tv=tvs, qa=(qa_seat, qa_facing))


# ---------------------------------------------------------------------------------------------
# The server room: BUILD-01 is on fire, the sprinklers are going, and nobody is coming.


def beacon(scene, name, at, parent, clip, phase=0.0):
    group = scene.group(name, at, parent=parent)
    box(scene, "Beacon Base", (0, 0.03, 0), (0.12, 0.06, 0.12), standard(None, (0.1, 0.1, 0.1), 0.5), group, shape="Cylinder")
    box(scene, "Beacon Dome", (0, 0.1, 0), (0.1, 0.12, 0.1), standard(None, (1.0, 0.1, 0.05), 0.2, emissive=(1.0, 0.08, 0.03),
                                                                      emissive_intensity=30.0, opacity=0.9), group, shape="Sphere", shadows=False)
    rotor = scene.group("Beacon Rotor", (0, 0.1, 0), parent=group)
    for yaw in (0.0, 180.0):
        scene.entity("Beacon Beam", [transform((0, 0, 0), yaw, 12.0), light("Spot", (1.0, 0.06, 0.02), 40.0, 12.0, inner=8.0, outer=22.0)], rotor)
    scene.entity("Beacon Spill", [transform((0, 0.05, 0)), light("Point", (1.0, 0.06, 0.03), 1.6, 3.5)], group)
    clip.track(rotor, "Transform", "Rotation", spin_keys(clip.frames / FPS, turns=round(clip.frames / FPS / 1.25), phase=phase), label=name + " Rotor")
    return group


def build_server_room(scene):
    room = scene.group("Server Room")
    clip = scene.clip("Server Room Alarm", 5.0)
    racks = scene.group("Racks", parent=room)
    rack_keys = ["SM_Prop_Server_Cabinet_01_Full", "SM_Prop_Server_Cabinet_02_Full"]
    burning = None
    rack_list = []
    for i in range(7):
        x = 18.25 + i * 0.95
        if i == 2:
            # BUILD-01: scorched, door hanging open.
            burning = put(scene, "BUILD-01", "SM_Prop_Server_Cabinet_01", (x, 0, 16.85), 180.0, parent=racks,
                          materials=[standard(ATLAS, (0.16, 0.13, 0.12), 1.0)] * len(PARTS["SM_Prop_Server_Cabinet_01"]["Parts"]))
        else:
            put(scene, "Rack", rack_keys[i % 2], (x, 0, 16.85), 180.0, parent=racks)
        rack_list.append((x, 16.85))
    for i in range(4):
        x = 21.4 + i * 0.95
        put(scene, "Rack", rack_keys[(i + 1) % 2], (x, 0, 14.75), 180.0, parent=racks)
        rack_list.append((x, 14.75))
    # Status LEDs on every rack front; red and strobing near the fire.
    for i, (x, z) in enumerate(rack_list):
        alarm = 1.0 if abs(x - 20.15) < 1.5 and z > 16 else 0.0
        box(scene, "Rack LEDs", (x, 1.08, z - 0.515), (0.62, 1.6, 0.008), graph("ServerLEDs", {"Seed": float(i), "Alarm": alarm}), racks, shadows=False)
    fire_at = (20.15, 2.04, 16.75)
    fire = scene.group("Fire", fire_at, parent=room)
    scene.entity("Flames", [transform((0, 0, 0)), particles(
        Graph=FLAME_GRAPH, Texture=FLAME_TEX, Shape="Box", BoxSize=[0.8, 0.05, 0.8], EmissionRate=140.0, MaxParticles=400,
        Lifetime=[0.45, 0.9], Speed=[0.8, 1.6], Size=[0.35, 0.65], EndSize=0.35, StartColor=[1.0, 0.75, 0.4],
        StartColor2=[1.0, 0.55, 0.2], EndColor=[1.0, 0.3, 0.08], Intensity=3.5, Gravity=-0.3, NoiseStrength=0.5,
        NoiseFrequency=1.5, Rotation=[-15.0, 15.0], SoftParticleDistance=0.15)], fire)
    scene.entity("Front Flames", [transform((0, -1.1, -0.52)), particles(
        Graph=FLAME_GRAPH, Texture=FLAME_TEX, Shape="Box", BoxSize=[0.55, 0.9, 0.05], EmissionRate=50.0, MaxParticles=200,
        Lifetime=[0.35, 0.6], Speed=[0.4, 0.9], Size=[0.16, 0.3], EndSize=0.3, StartColor=[1.0, 0.7, 0.35],
        StartColor2=[1.0, 0.5, 0.15], EndColor=[1.0, 0.25, 0.05], Intensity=3.0, Gravity=-0.6, NoiseStrength=0.6,
        NoiseFrequency=2.0, SoftParticleDistance=0.1)], fire)
    scene.entity("Sparks", [transform((0, -0.8, -0.5), rotation=aim_y((0.2, 0.5, -1.0))), particles(
        Shape="Cone", ShapeRadius=0.15, ConeAngle=35.0, EmissionRate=45.0, MaxParticles=200, Lifetime=[0.4, 1.1], Speed=[1.5, 3.5],
        Size=[0.015, 0.03], EndSize=0.4, StartColor=[1.0, 0.75, 0.3], StartColor2=[1.0, 0.9, 0.6], EndColor=[1.0, 0.3, 0.05],
        Intensity=10.0, Gravity=4.0, Alignment="Stretched", StretchFactor=0.05, Rotation=[0, 0], AngularVelocity=[0, 0])], fire)
    scene.entity("Smoke", [transform((0, 0.5, 0)), particles(
        Shape="Sphere", ShapeRadius=0.3, EmissionRate=14.0, MaxParticles=300, Lifetime=[5.0, 8.0], Speed=[0.3, 0.6], Size=[0.5, 0.9],
        EndSize=5.0, StartColor=[0.16, 0.15, 0.15], StartColor2=[0.25, 0.24, 0.23], EndColor=[0.3, 0.3, 0.3], StartAlpha=0.45, EndAlpha=0.0,
        Gravity=-0.03, Drag=0.9, NoiseStrength=0.6, NoiseFrequency=0.3, Blend="Alpha", Lit=True, FadeIn=0.15, SoftParticleDistance=0.6)], fire)
    sound(scene, "Fire Sound", "Fire", (0, -0.4, -0.3), fire, volume=1.0, near=1.5, far=16.0)
    sound(scene, "Server Hum", "ServerHum", (21.3, 1.2, 15.8), room, volume=0.55, near=2.0, far=12.0)
    sound(scene, "Sprinkler Sound", "Sprinklers", (21.0, 2.0, 14.5), room, volume=0.6, near=1.5, far=11.0)
    sound(scene, "Fire Alarm", "Alarm", (21.25, 2.72, 12.5), room, volume=0.4, near=3.0, far=32.0)
    fire_light = scene.entity("Fire Light", [transform((0, 0.2, -0.7)), light("Point", (1.0, 0.45, 0.15), 18.0, 10.0, shadows=True)], fire)
    clip.track(fire_light, "Light", "Intensity", flicker_keys(5.0, 18.0, 0.55, 1.15, 0.08, seed=5))
    # The smoke pours out under the door frame into the pit, along the ceiling.
    scene.entity("Smoke Under Ceiling", [transform((21.25, 2.7, 12.9), rotation=aim_y((0.0, 0.15, -1.0))), particles(
        Shape="Box", BoxSize=[1.6, 0.1, 0.2], EmissionRate=5.0, MaxParticles=120, Lifetime=[6.0, 9.0], Speed=[0.25, 0.45],
        Size=[0.5, 0.8], EndSize=4.0, StartColor=[0.2, 0.2, 0.2], StartColor2=[0.28, 0.27, 0.26], EndColor=[0.32, 0.32, 0.32],
        StartAlpha=0.3, EndAlpha=0.0, Gravity=-0.01, Drag=0.4, NoiseStrength=0.4, NoiseFrequency=0.3, Blend="Alpha", Lit=True,
        FadeIn=0.2, SoftParticleDistance=0.6)], room)
    # Sprinklers: three heads, streaks of water, splashes and standing water out past the door.
    for i, (x, z) in enumerate([(18.9, 14.0), (20.6, 15.6), (23.3, 13.6)]):
        put(scene, "Sprinkler", "SM_Prop_Sprinkler", (x, CEILING - 0.17, z), 0.0, parent=room, anchor="bottom")
        scene.entity("Sprinkler Spray", [transform((x, CEILING - 0.2, z), pitch=180.0), particles(
            Shape="Cone", ShapeRadius=0.03, ConeAngle=55.0, EmissionRate=420.0, MaxParticles=1200, Lifetime=[0.7, 1.0], Speed=[1.0, 2.2],
            Size=[0.008, 0.014], EndSize=1.0, StartColor=[0.75, 0.8, 0.9], StartColor2=[0.9, 0.92, 1.0], EndColor=[0.8, 0.85, 0.95],
            StartAlpha=0.55, EndAlpha=0.4, FadeIn=0.02, Gravity=9.8, Blend="Alpha", Lit=True, Alignment="Stretched",
            StretchFactor=0.06, Rotation=[0, 0], AngularVelocity=[0, 0], SoftParticleDistance=0.0)], room)
        scene.entity("Splash", [transform((x, 0.02, z)), particles(
            Shape="Box", BoxSize=[2.0, 0.02, 2.0], EmissionRate=120.0, MaxParticles=400, Lifetime=[0.2, 0.4], Speed=[0.6, 1.3],
            ConeAngle=40.0, Size=[0.01, 0.02], EndSize=0.5, StartColor=[0.8, 0.85, 0.95], StartColor2=[1, 1, 1], StartAlpha=0.6,
            Gravity=6.0, Blend="Alpha", Lit=True, Alignment="Stretched", StretchFactor=0.04)], room)
    scene.entity("Flooded Floor", [transform((21.25, 0.0, 15.0), 0.0, 90.0), decal((7.6, 5.4, 0.6), graph_name="FloodWater",
                                                                                   params={"Ripples": 1.0, "Edge Noise": 0.15})], room)
    scene.entity("Flood Into Corridor", [transform((21.0, 0.0, 11.2), 15.0, 90.0), decal((3.6, 3.8, 0.6), graph_name="FloodWater",
                                                                                         params={"Ripples": 0.0, "Edge Noise": 0.5}, sort=1)], room)
    beacon(scene, "Alarm Beacon", (21.25, 2.72, 12.72), room, clip)
    beacon(scene, "Alarm Beacon (Pit)", (21.25, 2.72, 12.28), room, clip, phase=90.0)
    put(scene, "Exit Sign", "SM_Prop_Sign_Exit_01", (19.5, 2.55, 12.66), 0.0, parent=room, anchor="center",
        materials=[standard(ATLAS, (1, 1, 1), 0.5, emissive=(0.2, 1.0, 0.4), emissive_intensity=2.5)])
    put(scene, "Emergency Axe", "SM_Prop_Emergency_Axe_01", (24.83, 1.5, 13.6), -90.0, parent=room, anchor="center")
    put(scene, "Empty Extinguisher", "SM_Prop_Fire_Extinguisher_01", (20.4, 0.08, 13.3), 110.0, roll=90.0, parent=room, anchor="center")
    for i in range(9):
        r = rng.uniform(0.1, 0.25)
        box(scene, "Foam", (rng.uniform(19.4, 21.2), r * 0.3, rng.uniform(13.4, 16.0)), (r * 2, r * 0.6, r * 2),
            standard(None, (0.85, 0.87, 0.86), 0.9), room, shape="Sphere")
    put(scene, "Electrics", "SM_Prop_Wall_Electronics_01", (17.75, 0, 16.2), 90.0, parent=room)
    put(scene, "Cable Tray", "SM_Prop_CableTray_01_Long", (21.25, 2.45, 16.3), 180.0, parent=room)
    for x in (19.0, 22.5):
        box(scene, "Red Strip", (x, CEILING - 0.03, 15.0), (0.1, 0.02, 3.0), standard(None, (0.2, 0.02, 0.02), 0.5, emissive=(1.0, 0.1, 0.05),
                                                                                   emissive_intensity=1.2), room, shadows=False)
    return room, clip, burning


# ---------------------------------------------------------------------------------------------
# The boss's office: champagne on ice, a putting green, the blinds down, on the phone to the board.


def build_boss_office(scene):
    office = scene.group("Boss Office")
    put(scene, "Executive Desk", "SM_Prop_Desk_06", (3.6, 0, 14.7), 180.0, parent=office)
    desk_top = top("SM_Prop_Desk_06")
    put(scene, "Boss Monitor", "SM_Prop_Computer_Monitor_Curved_01", (3.4, 0.75, 15.0), 0.0, parent=office,
        screens=[graph("CCTVServerRoom", {"Brightness": 0.6})])
    put(scene, "Boss Mug", "SM_Prop_Cup_Boss_01", (2.6, 0.75, 14.65), 30.0, parent=office)
    put(scene, "Nameplate", "SM_Prop_NamePlate_01", (3.6, 0.75, 14.4), 180.0, parent=office)
    put(scene, "Newton's Cradle", "SM_Prop_DeskToy_NewtownsCradle_01", (4.4, 0.75, 14.6), 200.0, parent=office)
    put(scene, "Desk Phone", "SM_Prop_Phone_Desk_01", (2.3, 0.75, 14.9), 20.0, parent=office)
    put(scene, "Boss Chair", "SM_Prop_Chair_05", (3.0, 0, 15.75), 30.0, parent=office)
    put(scene, "Shelf", "SM_Prop_Shelf_02", (0.42, 0, 15.0), 90.0, parent=office)
    for i, (key, y, dz) in enumerate([("SM_Prop_Trophy_01", 0.82, -0.6), ("SM_Prop_Globe_01", 0.82, 0.55), ("SM_Prop_Book_Group_03", 0.42, 0.0),
                                      ("SM_Prop_Trophy_01", 1.22, 0.3), ("SM_Prop_Book_Group_01", 1.22, -0.45)]):
        put(scene, key[8:], key, (0.42, y, 15.0 + dz), 90.0, parent=office)
    put(scene, "Stock Chart", "SM_Prop_Poster_Stocks_01", (0.17, 2.1, 15.0), 90.0, parent=office, anchor="center")
    put(scene, "Certificate", "SM_Prop_Certificate_01", (0.17, 1.65, 13.6), 90.0, parent=office)
    put(scene, "Putting Green", "SM_Prop_Minigolf_Green_01", (6.4, 0, 15.0), 180.0, parent=office)
    put(scene, "Golf Flag", "SM_Prop_Minigolf_Flag_01", (6.4, 0.09, 16.1), 180.0, parent=office)
    put(scene, "Golf Ball", "SM_Prop_Minigolf_Ball_01", (6.3, 0.09, 13.9), 0.0, parent=office)
    put(scene, "Putter", "SM_Prop_Minigolf_Club_01", (5.5, 0.72, 14.2), 90.0, roll=12.0, parent=office, anchor="center")
    # Champagne for the launch, on the coffee table, in the corner clear of the door (x 2.5-5).
    table_x = 1.55
    put(scene, "Couch", "SM_Prop_Couch_01", (0.65, 0, 13.55), 90.0, parent=office, atlas=ATLAS_B)
    put(scene, "Coffee Table", "SM_Prop_CoffeeTable_01", (table_x, 0, 13.55), 90.0, parent=office)
    for i, (dx, dz) in enumerate([(-0.15, 0.1), (0.05, -0.12)]):
        put(scene, "Champagne", "SM_Prop_Alcohol_Bottle_01", (table_x + dx, 0.42, 13.55 + dz), 0.0, parent=office)
    for i in range(4):
        put(scene, "Flute", "SM_Prop_Alcohol_Glass_01", (table_x - 0.15 + (i % 2) * 0.3, 0.42, 13.3 + (i // 2) * 0.5), 0.0, parent=office)
    put(scene, "Ceiling Fan", "SM_Prop_CeilingFan_01", (3.75, CEILING, 15.2), 0.0, parent=office, anchor="center",
        materials=part_materials("SM_Prop_CeilingFan_01"))
    put(scene, "Plant", "SM_Prop_Plant_07", (6.4, 0, 17.0), 180.0, scale=0.7, parent=office)
    sound(scene, "Ceiling Fan Sound", "CeilingFan", (3.75, 2.6, 15.2), office, volume=0.35, near=1.0, far=5.0)
    put(scene, "Director Sign", "SM_Prop_Sign_Director_01", (3.75, 2.25, 12.45), 180.0, parent=office, anchor="center")
    scene.entity("Desk Lamp Glow", [transform((4.6, 1.3, 14.9)), light("Point", (1.0, 0.75, 0.45), 4.0, 5.0, shadows=True)], office)
    scene.entity("Office Warmth", [transform((2.0, 2.6, 15.0)), light("Point", (1.0, 0.7, 0.45), 3.0, 6.0)], office)
    put(scene, "Desk Lamp", "SM_Prop_DeskLamp_06", (4.75, 0.75, 14.9), 200.0, parent=office)
    return office


# ---------------------------------------------------------------------------------------------
# The kitchen: a launch party that never happened.


def build_kitchen(scene):
    kitchen = scene.group("Kitchen")
    counter_x = 0.15 + 0.52
    run = [("SM_Prop_Kitchen_Counter_01", 1.0), ("SM_Prop_Kitchen_CounterSink_01", 2.0), ("SM_Prop_Kitchen_Counter_01", 3.0),
           ("SM_Prop_Kitchen_Counter_01", 4.0)]
    for key, z in run:
        put(scene, "Counter", key, (counter_x, 0, z), 90.0, parent=kitchen)
        put(scene, "Wall Cabinet", "SM_Prop_Kitchen_Cabinet_01", (0.15 + 0.36, 1.62, z), 90.0, parent=kitchen)
    put(scene, "Dishes", "SM_Prop_Kitchen_CounterSink_Dishes_01", (counter_x, 0.95, 2.0), 90.0, parent=kitchen)
    put(scene, "Fridge", "SM_Prop_Fridge_02", (0.15 + 0.45, 0, 5.05), 90.0, parent=kitchen)
    counter_top = 0.95
    counter_edge = 0.15 + 1.033
    put(scene, "Milk (Claimed)", "SM_Prop_Milk_Claimed_01", (counter_x + 0.33, counter_top, 3.0), 60.0, parent=kitchen)
    coffee = (counter_x, counter_top, 1.05)
    put(scene, "Coffee Machine", "SM_Prop_CoffeeMachine_01", coffee, 90.0, parent=kitchen)
    # The machine is pouring with nothing under it: from the spout onto the drip tray, over the tray's
    # lip, across the counter and off its edge onto the floor. Points are in the machine's model space
    # (from the pack's OBJ: spouts 0.32 m up, the tray's front lip 0.24 m up and 0.34 m forward).
    lo, hi = bounds("SM_Prop_CoffeeMachine_01")
    machine_rot = quat(90.0 + 180.0)

    def on_machine(p):
        return add3(coffee, qrot(machine_rot, sub3(p, ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2))))
    spout = on_machine((0.17, 0.315, -0.15))
    lip = on_machine((0.17, 0.245, -0.345))
    coffee_colour = dict(StartColor=[0.12, 0.06, 0.02], StartColor2=[0.18, 0.09, 0.03], EndColor=[0.12, 0.06, 0.02], StartAlpha=0.95,
                         EndAlpha=0.9, Blend="Alpha", Lit=True, Alignment="Stretched", Rotation=[0, 0], AngularVelocity=[0, 0],
                         SoftParticleDistance=0.0)
    scene.entity("Coffee From The Spout", [transform(spout, rotation=aim_y((0.0, -1.0, 0.0))), particles(
        Shape="Sphere", ShapeRadius=0.003, EmissionRate=90.0, MaxParticles=60, Lifetime=[0.08, 0.1], Speed=[0.25, 0.35],
        Size=[0.006, 0.009], EndSize=1.0, Gravity=9.8, StretchFactor=0.08, **coffee_colour)], kitchen)
    scene.entity("Coffee Over The Tray", [transform(lip, rotation=aim_y(sub3(on_machine((0.17, 0.2, -0.6)), lip))), particles(
        Shape="Box", BoxSize=[0.06, 0.005, 0.005], EmissionRate=110.0, MaxParticles=150, Lifetime=[0.2, 0.26], Speed=[0.15, 0.3],
        Size=[0.008, 0.014], EndSize=1.0, Gravity=9.8, StretchFactor=0.06, **coffee_colour)], kitchen)
    # Across the counter to its edge, then down to the floor.
    edge = (counter_edge + 0.01, counter_top, lip[2])
    run_centre = ((lip[0] + edge[0]) / 2 - 0.02, counter_top, lip[2])
    scene.entity("Coffee On The Counter", [transform(run_centre, 90.0, 90.0), decal((0.34, edge[0] - lip[0] + 0.14, 0.08), graph_name="FloodWater",
                                                                                   sort=3, params={"Water Color": [0.1, 0.04, 0.01],
                                                                                                   "Ripples": 1.0, "Edge Noise": 0.4})], kitchen)
    scene.entity("Coffee Off The Edge", [transform(edge, rotation=aim_y((1.0, -0.2, 0.0))), particles(
        Shape="Box", BoxSize=[0.005, 0.005, 0.12], EmissionRate=140.0, MaxParticles=300, Lifetime=[0.4, 0.46], Speed=[0.12, 0.25],
        Size=[0.01, 0.016], EndSize=1.0, Gravity=9.8, StretchFactor=0.05, **coffee_colour)], kitchen)
    scene.entity("Coffee Splash", [transform((edge[0] + 0.08, 0.01, edge[2])), particles(
        Shape="Box", BoxSize=[0.15, 0.01, 0.15], EmissionRate=40.0, MaxParticles=80, Lifetime=[0.15, 0.3], Speed=[0.3, 0.6], ConeAngle=40.0,
        Size=[0.006, 0.01], EndSize=0.6, StartColor=[0.12, 0.06, 0.02], StartColor2=[0.2, 0.1, 0.04], StartAlpha=0.8, Gravity=6.0,
        Blend="Alpha", Lit=True, Alignment="Stretched", StretchFactor=0.03)], kitchen)
    put(scene, "Spilled Pot", "SM_Prop_Pot_Spilled_01", (edge[0] + 0.75, 0, edge[2] - 0.45), 120.0, parent=kitchen)
    sound(scene, "Coffee Sound", "Coffee", (edge[0] + 0.05, 0.5, edge[2]), kitchen, volume=0.6, near=0.5, far=6.0)
    scene.entity("Coffee Steam", [transform((counter_x + 0.05, counter_top + 0.75, 1.05)), particles(
        Shape="Sphere", ShapeRadius=0.06, EmissionRate=6.0, MaxParticles=60, Lifetime=[2.0, 3.5], Speed=[0.12, 0.25], Size=[0.08, 0.14],
        EndSize=4.0, StartColor=[0.7, 0.7, 0.7], StartColor2=[0.85, 0.85, 0.85], EndColor=[0.8, 0.8, 0.8], StartAlpha=0.16, EndAlpha=0.0,
        Gravity=-0.05, Drag=0.6, NoiseStrength=0.4, NoiseFrequency=0.6, Blend="Alpha", Lit=True, FadeIn=0.2)], kitchen)
    scene.entity("Coffee Puddle", [transform((edge[0] + 0.45, 0.0, edge[2] + 0.1), 20.0, 90.0), decal((1.6, 1.2, 0.4), graph_name="FloodWater", sort=2,
                                                                                params={"Water Color": [0.1, 0.04, 0.01], "Ripples": 0.0, "Edge Noise": 0.6})], kitchen)
    # The microwave: someone's 2 AM popcorn, still going.
    microwave = (counter_x, counter_top, 3.52)
    put(scene, "Microwave", "SM_Prop_Microwave_01", microwave, 90.0, parent=kitchen)
    sound(scene, "Microwave Sound", "Microwave", (counter_x + 0.1, counter_top + 0.15, microwave[2]), kitchen, volume=0.55, near=0.6, far=6.0)
    micro_light = scene.entity("Microwave Glow", [transform((counter_x + 0.35, counter_top + 0.15, microwave[2])), light("Point", (1.0, 0.55, 0.2), 3.0, 2.5)], kitchen)
    scene.entity("Burnt Popcorn Smoke", [transform((counter_x + 0.3, counter_top + 0.28, microwave[2])), particles(
        Shape="Box", BoxSize=[0.05, 0.05, 0.5], EmissionRate=7.0, MaxParticles=80, Lifetime=[3.0, 5.0], Speed=[0.1, 0.25], Size=[0.1, 0.2],
        EndSize=5.0, StartColor=[0.12, 0.11, 0.1], StartColor2=[0.2, 0.19, 0.18], EndColor=[0.35, 0.34, 0.33], StartAlpha=0.35, EndAlpha=0.0,
        Gravity=-0.06, Drag=0.6, NoiseStrength=0.4, NoiseFrequency=0.5, Blend="Alpha", Lit=True, FadeIn=0.1)], kitchen)
    # Along the counter (z): coffee machine 0.53-1.57, sink 1.5-2.5, toaster, kettle and milk, the
    # microwave 3.24-3.81, the donut boxes 3.88-4.45, the fridge from 4.55.
    put(scene, "Toaster", "SM_Prop_Toaster_01", (counter_x, counter_top, 2.68), 90.0, parent=kitchen)
    put(scene, "Kettle", "SM_Prop_Kettle_01", (counter_x - 0.08, counter_top, 3.0), 120.0, parent=kitchen)
    donuts = 4.16
    for i in range(6):
        put(scene, "Empty Donut Box", "SM_Prop_Donut_Box_01", (counter_x + 0.05, counter_top + i * 0.08, donuts + rng.uniform(-0.02, 0.02)),
            90.0 + rng.uniform(-6, 6), parent=kitchen, scale=(1, 0.22, 1))
    put(scene, "Last Donut", "SM_Prop_Donut_Pink_01", (counter_x + 0.1, counter_top + 6 * 0.08 + 0.01, donuts), 0.0, parent=kitchen)
    # The table: the launch cake, candles still burning, balloons and hats.
    table = (3.7, 0.0, 3.2)
    put(scene, "Party Table", "SM_Prop_Table_Round_01", table, 0.0, parent=kitchen)
    table_top = top("SM_Prop_Table_Round_01")
    put(scene, "Launch Cake", "SM_Prop_Cake_01", (table[0], table_top, table[2]), 0.0, parent=kitchen)
    # The icing is 0.29 m up (the bounds' top is the cake's own centre candle); the candles stand in
    # it between that candle and the ring of cherries.
    icing = table_top + 0.285
    candles = scene.group("Candles", (table[0], icing, table[2]), parent=kitchen)
    for i in range(5):
        a = i / 5 * 2 * math.pi + 0.3
        p = (math.cos(a) * 0.08, 0.035, math.sin(a) * 0.08)
        box(scene, "Candle", p, (0.012, 0.09, 0.012), standard(None, [(1, 0.3, 0.3), (0.3, 0.6, 1), (1, 0.9, 0.3), (0.4, 1, 0.5), (1, 0.5, 1)][i], 0.5),
            candles, shape="Cylinder")
        scene.entity("Candle Flame", [transform((p[0], 0.09, p[2])), particles(
            Graph=FLAME_GRAPH, Texture=FLAME_TEX, Shape="Sphere", ShapeRadius=0.002, EmissionRate=24.0, MaxParticles=24,
            Lifetime=[0.2, 0.35], Speed=[0.03, 0.08], Size=[0.025, 0.04], EndSize=0.5, StartColor=[1.0, 0.8, 0.45], StartColor2=[1.0, 0.65, 0.3],
            EndColor=[1.0, 0.4, 0.1], Intensity=3.0, Gravity=-0.1, Rotation=[-5.0, 5.0], AngularVelocity=[0, 0], SoftParticleDistance=0.02)], candles)
    candle_light = scene.entity("Candle Light", [transform((0, 0.25, 0)), light("Point", (1.0, 0.65, 0.3), 2.2, 3.5, shadows=True)], candles)
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        put(scene, "Party Hat", "SM_Prop_Party_Hat_0%d" % (i % 3 + 1), (table[0] + math.cos(a) * 0.42, table_top, table[2] + math.sin(a) * 0.42),
            rng.uniform(0, 360), parent=kitchen)
        put(scene, "Plate", "SM_Prop_Dishes_01", (table[0] + math.cos(a + 0.5) * 0.38, table_top, table[2] + math.sin(a + 0.5) * 0.38), 0.0, parent=kitchen)
    put(scene, "Air Horn", "SM_Prop_Air_Horn_01", (table[0] - 0.2, table_top, table[2] + 0.35), 40.0, parent=kitchen)
    chairs = []
    balloons = []
    for i, a in enumerate([0.3, 2.2, 4.1]):
        p = (table[0] + math.cos(a) * 0.85, 0.0, table[2] + math.sin(a) * 0.85)
        facing = compass(table[0] - p[0], table[2] - p[2]) + rng.uniform(-25, 25)
        chairs.append(put(scene, "Party Chair", "SM_Prop_Chair_09", p, facing, parent=kitchen))
        back = front(p, facing, -0.25)
        balloon = put(scene, "Balloon", "SM_Prop_Balloon_01", (back[0], 0.85 + 0.92, back[2]), rng.uniform(0, 360), parent=kitchen,
                      anchor="center", materials=[standard(None, [(1.0, 0.15, 0.2), (0.15, 0.5, 1.0), (1.0, 0.8, 0.1)][i], 0.25, metallic=0.1)])
        balloons.append(balloon)
    put(scene, "Bunting", "SM_Prop_Bunting_01", (3.5, 2.75, 2.0), 30.0, parent=kitchen, anchor="bottom")
    put(scene, "Bunting", "SM_Prop_Bunting_02", (3.6, 2.8, 4.6), -20.0, parent=kitchen, anchor="bottom")
    for i in range(5):
        put(scene, "Streamer", "SM_Prop_Streamer_0%d" % (i % 2 + 1), (2.2 + i * 0.8, CEILING - 0.02, 1.0 + (i % 3) * 1.5), rng.uniform(0, 360),
            parent=kitchen, anchor="bottom")
    put(scene, "Vending Machine", "SM_Prop_VendingMachine_01", (5.4, 0, 0.6), 0.0, parent=kitchen,
        materials=[standard(ATLAS, (1, 1, 1), 0.5), glass((0.5, 0.7, 0.9), 0.3)])
    scene.entity("Vending Glow", [transform((5.4, 1.2, 1.2)), light("Point", (0.6, 0.8, 1.0), 2.0, 3.0)], kitchen)
    put(scene, "Water Cooler", "SM_Prop_WaterCooler_01", (6.5, 0, 0.55), 0.0, parent=kitchen)
    put(scene, "Bin", "SM_Prop_Trashbin_01", (2.3, 0, 0.45), 0.0, parent=kitchen)
    for i in range(5):
        put(scene, "Rubbish", "SM_Prop_Rubbish_02", (2.3 + rng.uniform(-0.6, 0.6), 0, 0.6 + rng.uniform(0, 0.5)), rng.uniform(0, 360), parent=kitchen)
    put(scene, "Kitchen Sign", "SM_Prop_Sign_Kitchen_01", (3.5, 2.4, 0.16), 0.0, parent=kitchen, anchor="center")
    return kitchen, candle_light, micro_light, balloons


# ---------------------------------------------------------------------------------------------
# The lounge: arcade, fish, and a developer asleep in a beanbag with the build on his lap.


def build_lounge(scene):
    lounge = scene.group("Lounge")
    put(scene, "Rug", "SM_Prop_Rug_01", (3.4, 0, 9.6), 90.0, parent=lounge, atlas=ATLAS_C)
    put(scene, "Arcade Cabinet", "SM_Prop_ArcadeMachine_01", (0.65, 0, 8.4), 90.0, parent=lounge,
        screens=[graph("ArcadeScreen")])
    sound(scene, "Arcade Sound", "Arcade", (0.9, 1.3, 8.4), lounge, volume=0.35, near=1.0, far=8.0)
    scene.entity("Arcade Glow", [transform((1.3, 1.5, 8.4)), light("Point", (0.7, 0.3, 1.0), 1.0, 3.0)], lounge)
    put(scene, "Beanbag", "SM_Prop_Chair_BeanBag_02", (2.6, 0, 10.0), 135.0, parent=lounge, atlas=ATLAS_B)
    # Back to the boss's glass wall, west of his door.
    put(scene, "Couch", "SM_Prop_Couch_03", (1.35, 0, 12.0), 180.0, parent=lounge, atlas=ATLAS_C)
    put(scene, "Table Football", "SM_Prop_TableFootball_01", (5.2, 0, 7.6), 90.0, parent=lounge)
    put(scene, "Console", "SM_Prop_Console_PlayBox_01", (4.2, 0.0, 10.3), 30.0, parent=lounge)
    put(scene, "Controller", "SM_Prop_Controller_01", (3.6, 0.0, 10.9), 70.0, parent=lounge)
    put(scene, "Wall Shelf", "SM_Prop_Shelf_Wall_01", (0.32, 1.55, 10.6), 90.0, parent=lounge)
    put(scene, "Neon Cactus", "SM_Prop_Neon_Cactus_01", (0.32, 1.55 + 0.06, 10.4), 90.0, parent=lounge,
        materials=[graph("Neon", {"Seed": 2.0})])
    scene.entity("Neon Glow", [transform((0.7, 1.9, 10.4)), light("Point", (0.3, 1.0, 0.4), 0.5, 2.0)], lounge)
    put(scene, "Plant", "SM_Prop_Plant_07", (1.2, 0, 7.0), 90.0, scale=0.8, parent=lounge)
    # The fish tank divides the lounge from the pit.
    tank_at = (7.0, 0, 9.4)
    tank = put(scene, "Fish Tank", "SM_Prop_Fishtank_01", tank_at, 90.0, parent=lounge,
               materials=[standard(ATLAS, (1, 1, 1), 0.6), graph("FishTankWater"), glass((0.2, 0.3, 0.3), 0.12)])
    sound(scene, "Fish Tank Sound", "FishTank", (tank_at[0], 0.9, tank_at[2]), lounge, volume=0.45, near=0.5, far=4.5)
    scene.entity("Tank Light", [transform((tank_at[0], 1.2, tank_at[2])), light("Point", (0.3, 0.8, 1.0), 2.5, 3.0)], lounge)
    scene.entity("Bubbles", [transform((tank_at[0], 0.75, tank_at[2] + 0.4)), particles(
        Shape="Sphere", ShapeRadius=0.02, EmissionRate=10.0, MaxParticles=60, Lifetime=[1.2, 1.6], Speed=[0.2, 0.3], Size=[0.01, 0.02],
        EndSize=1.4, StartColor=[0.7, 0.95, 1.0], StartColor2=[0.9, 1.0, 1.0], EndColor=[0.8, 1.0, 1.0], StartAlpha=0.6, EndAlpha=0.3,
        Gravity=-0.15, NoiseStrength=0.3, NoiseFrequency=3.0, Blend="Additive", Intensity=2.0)], lounge)
    fish = []
    for i, color in enumerate([(1.0, 0.45, 0.05), (1.0, 0.85, 0.1), (0.2, 0.6, 1.0)]):
        fish.append(put(scene, "Fish", "SM_Prop_Fish_01", (tank_at[0], 0.95, tank_at[2]), 0.0, parent=lounge, anchor="center",
                        materials=[standard(ATLAS, color, 0.35)]))
    return lounge, tank_at, fish


# ---------------------------------------------------------------------------------------------
# The conference room, the corridor and the lobby.


def build_conference(scene):
    room = scene.group("Conference Room")
    table = (21.6, 0, 3.75)
    put(scene, "Conference Table", "SM_Prop_Table_Conference_01", table, 180.0, parent=room)
    top_y = top("SM_Prop_Table_Conference_01")
    r = random.Random(9)
    for i, (x, z, facing) in enumerate([(20.3, 2.3, 0), (21.6, 2.25, 0), (22.9, 2.35, 0), (20.3, 5.2, 180), (21.6, 5.3, 180), (22.9, 5.2, 180),
                                        (19.15, 3.75, 90)]):
        put(scene, "Meeting Chair", "SM_Prop_Chair_08", (x + r.uniform(-0.2, 0.2), 0, z + (r.uniform(-0.5, -0.1) if facing == 0 else r.uniform(0.1, 0.5))),
            facing + r.uniform(-50, 50), parent=room)
    projector = (20.3, top_y, 3.75)
    put(scene, "Projector", "SM_Prop_Projector_01", projector, 90.0, parent=room)
    screen = put(scene, "Projector Screen", "SM_Prop_ProjectorScreen_02_Down", (24.82, 2.95, 3.75), -90.0, parent=room, anchor="top",
                 screens=[graph("RoadmapSlide", {"Brightness": 0.7})])
    screen_y = 2.95 - 2.6 / 2 - 0.05
    beam_from = (20.55, top_y + 0.08, 3.75)
    scene.entity("Projector Beam", [transform(beam_from, *look_angles(beam_from, (24.8, screen_y + 0.25, 3.75))),
                                    light("Spot", (0.85, 0.9, 1.0), 25.0, 7.0, shadows=True, inner=11.0, outer=15.0)], room)
    scene.entity("Dust In The Beam", [transform(((beam_from[0] + 24.6) / 2, (beam_from[1] + screen_y) / 2 + 0.2, 3.75)), particles(
        Shape="Box", BoxSize=[3.6, 0.9, 1.2], EmissionRate=25.0, MaxParticles=200, Lifetime=[4.0, 7.0], Speed=[0.01, 0.04],
        Size=[0.006, 0.012], EndSize=1.0, StartColor=[0.9, 0.92, 1.0], StartColor2=[1.0, 1.0, 1.0], EndColor=[0.9, 0.92, 1.0],
        StartAlpha=0.7, EndAlpha=0.0, FadeIn=0.3, NoiseStrength=0.1, NoiseFrequency=0.3, Blend="Alpha", Lit=True)], room)
    scene.entity("Slide Bounce", [transform((24.2, screen_y, 3.75)), light("Point", (0.85, 0.9, 1.0), 0.8, 5.0)], room)
    for key, x, z, yaw in [("SM_Prop_Donut_Box_01", 21.4, 3.5, 20), ("SM_Prop_Phone_Conference_01", 22.2, 3.9, 0), ("SM_Prop_Laptop_02", 22.9, 3.2, 170),
                           ("SM_Prop_NotePad_01", 20.9, 3.1, 10), ("SM_Prop_Cup_Coffee_Disposable_Closed_01", 21.0, 4.5, 0),
                           ("SM_Prop_Cup_Paper_01", 22.6, 4.4, 0), ("SM_Prop_Clipboard_01", 23.1, 4.4, 200), ("SM_Prop_Donut_Choc_01", 21.7, 3.1, 0)]:
        put(scene, key[8:], key, (x, top_y, z), yaw, parent=room)
    put(scene, "Flip Chart", "SM_Prop_Presentation_Chart_01", (24.2, 0, 6.7), -135.0, parent=room)
    put(scene, "Plant", "SM_Prop_Plant_02", (18.1, 0, 0.6), 0.0, parent=room)
    return room


def build_corridor(scene):
    corridor = scene.group("Corridor")
    copier = (24.35, 0, 9.6)
    put(scene, "Photocopier", "SM_Prop_Photocopier_01", copier, -90.0, parent=corridor,
        screens=[graph("BlinkLight", {"Color": [1.0, 0.5, 0.05], "Rate": 2.0, "Duty": 0.5, "Intensity": 6.0})])
    put(scene, "Out Of Order", "SM_Prop_Sign_OutofOrder_01", (24.0, 0.85, 9.6), -90.0, parent=corridor, anchor="center")
    scene.entity("Paper Jam", [transform((23.7, 0.95, 9.9), rotation=aim_y((-1.0, 0.7, 0.1))), particles(
        Graph=GRAPHS + "PaperSheet.shadergraph", Shape="Cone", ShapeRadius=0.05, ConeAngle=25.0, EmissionRate=5.0, MaxParticles=60,
        Lifetime=[3.0, 4.5], Speed=[1.0, 2.0], Size=[0.22, 0.28], EndSize=1.0, StartColor=[0.55, 0.55, 0.58], StartColor2=[0.62, 0.62, 0.65],
        EndColor=[0.55, 0.55, 0.58], StartAlpha=1.0, EndAlpha=1.0, FadeIn=0.0, Gravity=0.8, Drag=1.2, NoiseStrength=0.8,
        NoiseFrequency=0.6, AngularVelocity=[-200.0, 200.0], Blend="Alpha", Lit=True, SoftParticleDistance=0.0)], corridor)
    for i in range(26):
        a = rng.uniform(-1.2, 1.2)
        rr = rng.uniform(0.3, 2.4)
        put(scene, "Copy", "SM_Prop_Paper_0%d" % (i % 3 + 1), (24.0 - math.cos(a) * rr, 0.003 + i * 0.0007, 9.6 + math.sin(a) * rr),
            rng.uniform(0, 360), parent=corridor)
    put(scene, "Paper Pile", "SM_Prop_Paper_Pile_02", (23.6, 0, 9.0), 30.0, parent=corridor)
    put(scene, "Shredder", "SM_Prop_PaperShredder_01", (24.6, 0, 11.6), -90.0, parent=corridor)
    put(scene, "Fax", "SM_Prop_FaxMachine_01", (24.4, 0.75, 8.2), -90.0, parent=corridor)
    put(scene, "Fax Table", "SM_Prop_Table_02", (24.3, 0, 8.2), -90.0, parent=corridor, scale=(0.5, 1, 0.5))
    # The fallen ceiling panel and the cable it brought down, sparking.
    put(scene, "Fallen Panel", "SM_Bld_Ceiling_Panel_01", (23.6, 0.25, 11.2), 15.0, pitch=18.0, roll=-6.0, parent=corridor, anchor="center")
    cable_top = (23.2, CEILING + 0.3, 11.4)
    cable_end = (23.4, 1.25, 11.1)
    mid = [(a + b) / 2 for a, b in zip(cable_top, cable_end)]
    box(scene, "Hanging Cable", mid, (0.02, length3(sub3(cable_top, cable_end)), 0.02), standard(None, (0.02, 0.02, 0.02), 0.6), corridor,
        shape="Cylinder", yaw=compass(cable_end[0] - cable_top[0], cable_end[2] - cable_top[2]),
        pitch=math.degrees(math.atan2(math.hypot(cable_end[0] - cable_top[0], cable_end[2] - cable_top[2]), cable_top[1] - cable_end[1])))
    scene.entity("Cable Sparks", [transform(cable_end), particles(
        Shape="Sphere", ShapeRadius=0.02, EmissionRate=30.0, MaxParticles=120, Lifetime=[0.3, 0.8], Speed=[1.0, 2.5], Size=[0.01, 0.02],
        EndSize=0.3, StartColor=[0.7, 0.85, 1.0], StartColor2=[1.0, 1.0, 1.0], EndColor=[1.0, 0.6, 0.2], Intensity=12.0, Gravity=5.0,
        Alignment="Stretched", StretchFactor=0.04, Rotation=[0, 0], AngularVelocity=[0, 0])], corridor)
    sound(scene, "Spark Sound", "Sparks", cable_end, corridor, volume=0.7, near=0.6, far=9.0)
    sound(scene, "Copier Sound", "Copier", (copier[0], 0.7, copier[2]), corridor, volume=0.5, near=0.8, far=8.0)
    spark_light = scene.entity("Spark Light", [transform(cable_end), light("Point", (0.7, 0.85, 1.0), 4.0, 4.0)], corridor)
    put(scene, "Janitor Cart", "SM_Prop_Janitor_Cart_01", (18.9, 0, 10.6), 70.0, parent=corridor)
    put(scene, "Wet Floor", "SM_Prop_Sign_Wetfloor_01", (21.9, 0, 10.1), 200.0, parent=corridor)
    put(scene, "Wet Floor", "SM_Prop_Sign_Wetfloor_01", (19.9, 0, 12.0), 160.0, parent=corridor)
    put(scene, "Mop Bucket", "SM_Prop_Janitor_Bucket_01", (20.0, 0, 10.7), 0.0, parent=corridor)
    return corridor, spark_light


def guard_chair(guard_desk):
    return (guard_desk[0], 0.0, guard_desk[2] - 0.95)


def build_lobby(scene):
    lobby = scene.group("Lobby")
    put(scene, "Out Of Order", "SM_Prop_Sign_OutofOrder_01", (11.25, 1.5, 0.05), 0.0, parent=lobby, anchor="center")
    put(scene, "Exit Sign", "SM_Prop_Sign_Exit_01", (11.25, 2.75, 0.05), 0.0, parent=lobby, anchor="center",
        materials=[standard(ATLAS, (1, 1, 1), 0.5, emissive=(0.2, 1.0, 0.4), emissive_intensity=2.5)])
    guard_desk = (14.8, 0, 1.9)
    put(scene, "Security Desk", "SM_Prop_Desk_03", guard_desk, 180.0, parent=lobby)
    top_y = top("SM_Prop_Desk_03")
    for i, (dx, graph_name) in enumerate([(-0.6, "CCTVLobby"), (0.0, "CCTVServerRoom"), (0.6, "CCTVLobby")]):
        put(scene, "CCTV Monitor", "SM_Prop_Monitor_Crt_01", (guard_desk[0] + dx, top_y, guard_desk[2] + 0.18), 180.0 + (dx * -20.0), parent=lobby,
            screens=[graph(graph_name, {"Brightness": 0.32 if graph_name == "CCTVLobby" else 0.45})])
    scene.entity("CCTV Glow", [transform((guard_desk[0], top_y + 0.35, guard_desk[2] - 0.3)), light("Point", (0.6, 0.85, 0.7), 0.7, 2.6)], lobby)
    for key, dx, dz, yaw in [("SM_Prop_Cup_Coffee_Disposable_Closed_01", -0.85, -0.25, 0), ("SM_Prop_Donut_Choc_01", 0.85, -0.2, 0),
                             ("SM_Prop_Book_Magazine_01", 0.4, -0.3, 30), ("SM_Prop_Radio_01", -0.95, 0.15, 160), ("SM_Prop_Phone_Desk_01", 0.95, 0.2, 200)]:
        put(scene, key[8:], key, (guard_desk[0] + dx, top_y, guard_desk[2] + dz), 180.0 + yaw, parent=lobby)
    put(scene, "Guard Chair", "SM_Prop_Chair_05", guard_chair(guard_desk), -10.0, parent=lobby)
    cameras = []
    for at, aim in [((24.6, CEILING - 0.02, 0.4), (14.0, 0.0, 9.0)), ((7.9, CEILING - 0.02, 17.0), (14.0, 0.0, 8.0))]:
        cam = put(scene, "Security Camera", "SM_Prop_Security_Camera_02", at, compass(aim[0] - at[0], aim[2] - at[2]),
                  parent=lobby, anchor="top")
        cameras.append((cam, at, aim))
    put(scene, "Plant", "SM_Prop_Plant_05", (17.0, 0, 0.6), 0.0, parent=lobby)
    put(scene, "Plant", "SM_Prop_Plant_05", (8.0, 0, 0.6), 0.0, parent=lobby)
    return lobby, guard_desk, cameras


# ---------------------------------------------------------------------------------------------
# People


def build_people(scene, pit_info, guard_desk):
    people = scene.group("People")
    clips = {}
    # The hero: still typing at 3:47 AM. Hands on the keyboard by IK; the typing is a bone clip.
    seat, facing = pit_info["hero"]
    key_y = top("SM_Prop_Desk_01") + 0.06 - SIT_LIFT

    def typing_pose(left_lift=0.0, right_lift=0.0, head=0.0):
        return seated({"spine_01": ("turn", (1, 0, 0), -8.0), "spine_02": ("turn", (1, 0, 0), -6.0),
                       "head": ("turn", (1, 0, 0), -12.0 + head),
                       "UpperArm_L": ("reach", "L", (0.17, key_y + left_lift, -0.52), (0.6, -0.5, 0.4)),
                       "UpperArm_R": ("reach", "R", (-0.17, key_y + right_lift, -0.52), (-0.6, -0.5, 0.4)),
                       "Hand_L": ("aim", "indexFinger_01_l", (-0.1, -0.35, -1.0)), "Hand_R": ("aim", "indexFinger_01_r", (0.1, -0.35, -1.0))})
    hero = Character(scene, "The Last Developer", "SK_Chr_Developer_Male_01", front(seat, facing, -0.02), facing, typing_pose(), people, lift=SIT_LIFT)
    hero.wear("head", "SM_Chr_Attachment_Headset_01")
    sound(scene, "Typing Sound", "Typing", hero.to_world((0.0, key_y + 0.05, -0.45)), people, volume=0.7, near=0.6, far=7.0)
    typing = scene.clip("Typing", 2.0)
    for bone in ("UpperArm_L", "lowerarm_l", "Hand_L", "UpperArm_R", "lowerarm_r", "Hand_R", "head"):
        keys = []
        for i in range(17):
            t = i * 0.125
            left = 0.035 if i % 2 == 0 else 0.0
            right = 0.0 if i % 2 == 0 else 0.03
            if i % 8 in (5, 6):
                left = right = 0.0  # a pause to read the error
            head = 2.0 * math.sin(i * 0.9)
            keys.append((t, hero.local_rotation(typing_pose(left, right, head), bone), "SmoothStep"))
        keys[-1] = (2.0, keys[0][1], "SmoothStep")
        typing.track(hero.bone(bone), "Transform", "Rotation", keys, label="Developer " + bone)
    clips["typing"] = typing
    # Asleep on the keyboard, folded over the desk.
    seat, facing = pit_info["sleeper"]
    desk_y = top("SM_Prop_Desk_01") - SIT_LIFT

    def sleep_pose(breath=0.0):
        return seated({"spine_01": ("turn", (1, 0, 0), -30.0 - breath), "spine_02": ("turn", (1, 0, 0), -24.0 + breath * 0.5),
                       "spine_03": ("turn", (1, 0, 0), -12.0 + breath * 0.5),
                       "neck_01": ("turn", (0, 0, 1), 25.0), "head": ("turn", (0, 0, 1), 45.0),
                       "UpperArm_L": ("reach", "L", (-0.12, desk_y + 0.08, -0.5), (1.0, 0.2, 0.3)),
                       "UpperArm_R": ("reach", "R", (0.15, desk_y + 0.08, -0.46), (-1.0, 0.2, 0.3)),
                       "Hand_L": ("aim", "indexFinger_01_l", (-1.0, -0.1, 0.1)), "Hand_R": ("aim", "indexFinger_01_r", (1.0, -0.1, 0.2))})
    sleeper = Character(scene, "Asleep On The Keyboard", "SK_Chr_Developer_Female_01", front(seat, facing, -0.04), facing, sleep_pose(), people, lift=SIT_LIFT)
    breathing = scene.clip("Breathing", 4.5)
    for bone in ("spine_01", "spine_02", "spine_03"):
        breathing.track(sleeper.bone(bone), "Transform", "Rotation",
                        [(0.0, sleeper.local_rotation(sleep_pose(0.0), bone), "SmoothStep"),
                         (1.8, sleeper.local_rotation(sleep_pose(2.5), bone), "SmoothStep"),
                         (4.5, sleeper.local_rotation(sleep_pose(0.0), bone), "SmoothStep")], label="Sleeper " + bone)
    clips["breathing"] = breathing
    # The beanbag: lying back, laptop on his stomach, still compiling.
    def lounge_pose(breath=0.0):
        # Upright frame: the body is leaned back 52 degrees about the hips, the legs are not.
        return {"spine_02": ("turn", (1, 0, 0), -14.0 + breath), "head": ("turn", (1, 0, 0), -30.0), "neck_01": ("turn", (0, 1, 0), 20.0),
                "Thigh_L": ("aim", "calf_l", (0.3, 0.25, -1.0)), "calf_l": ("aim", "Foot_L", (0.1, -1.0, -0.35)),
                "Thigh_R": ("aim", "calf_r", (-0.25, 0.05, -1.0)), "calf_r": ("aim", "Foot_R", (-0.05, -0.8, -0.8)),
                "Foot_L": ("aim", "ball_l", (0.0, 0.2, -1.0)), "Foot_R": ("aim", "ball_r", (0.0, 0.0, -1.0)),
                "UpperArm_L": ("reach", "L", (0.1, 1.05, -0.45), (1.0, -0.5, 0.3)),
                "UpperArm_R": ("aim", "lowerarm_r", (-0.7, -0.7, 0.2)), "lowerarm_r": ("aim", "Hand_R", (-0.3, -0.95, 0.1))}
    bag_at = (2.6, 0.0, 10.0)
    loafer = Character(scene, "Compiling In The Beanbag", "SK_Chr_Developer_Male_02", (bag_at[0] - 0.08, 0.0, bag_at[2] + 0.12), 135.0, lounge_pose(),
                       people, lift=-0.53, lean=66.0)
    lap = loafer.joint("Pelvis")
    laptop = loafer.attach("spine_01", "SM_Prop_Laptop_01", (lap[0] + 0.02, lap[1] + 0.1, lap[2] - 0.32), quat(180.0, -8.0),
                           name="Laptop (still compiling)", materials=part_materials("SM_Prop_Laptop_01", screens=[graph("Compiling", {"Brightness": 0.45})]))
    scene.entity("Laptop Glow", [transform(loafer.to_world((lap[0], lap[1] + 0.45, lap[2] - 0.6))), light("Point", (0.4, 1.0, 0.5), 0.35, 1.6)], people)
    snooze = scene.clip("Beanbag Breathing", 5.2)
    snooze.track(loafer.bone("spine_01"), "Transform", "Rotation",
                 [(0.0, loafer.local_rotation(lounge_pose(0.0), "spine_01"), "SmoothStep"),
                  (2.2, loafer.local_rotation(lounge_pose(3.0), "spine_01"), "SmoothStep"),
                  (5.2, loafer.local_rotation(lounge_pose(0.0), "spine_01"), "SmoothStep")], label="Beanbag spine_01")
    # The security guard: leaning right back, mouth open, CCTV on fire in front of him.
    def guard_pose(breath=0.0, nod=0.0):
        # Slumped against the backrest (about 8 degrees back), head lolling back.
        return seated({"spine_01": ("turn", (1, 0, 0), 7.0 + breath), "spine_03": ("turn", (1, 0, 0), 4.0),
                       "neck_01": ("turn", (0, 0, 1), -10.0 + nod * 0.3), "head": ("turn", (1, 0, 0), 34.0 - nod),
                       "UpperArm_L": ("aim", "lowerarm_l", (0.35, -0.9, 0.2)), "lowerarm_l": ("aim", "Hand_L", (-0.5, -0.1, -0.85)),
                       "UpperArm_R": ("aim", "lowerarm_r", (-0.35, -0.9, 0.2)), "lowerarm_r": ("aim", "Hand_R", (0.55, -0.05, -0.85))},
                      foot_forward=0.85, knee_spread=0.3)
    # On the cushion: Chair_05's seat is 0.05 m ahead of its bounds' centre (the backrest is behind).
    guard_seat = front(guard_chair(guard_desk), -10.0, 0.06)
    guard = Character(scene, "Security Guard (Asleep)", "SK_Chr_Security_Male_01", guard_seat, -10.0, guard_pose(), people, lift=SIT_LIFT)
    guard.wear("spine_03", "SM_Chr_Attachment_Identity_01")
    sound(scene, "Snoring", "Snoring", guard.to_world(guard.joint("head")), people, volume=0.8, near=0.6, far=8.0)
    dozing = scene.clip("Guard Dozing", 11.0)
    for bone in ("spine_01", "head", "neck_01"):
        keys = []
        for t, breath, nod in [(0.0, 0, 0), (2.0, 2.5, 0), (4.0, 0, 0), (6.0, 2.5, 0), (7.6, 0, 0), (8.2, 0, 32), (8.5, 0, -4), (9.2, 1.0, 0), (11.0, 0, 0)]:
            keys.append((t, guard.local_rotation(guard_pose(breath, nod), bone), "SmoothStep"))
        dozing.track(guard.bone(bone), "Transform", "Rotation", keys, label="Guard " + bone)
    # The boss, at the window, on the phone to the board: "It's basically done."
    boss_at = (2.1, 0.0, 16.75)
    ear = (-0.1, 1.6, -0.05)

    def boss_pose(turn=0.0):
        return {"spine_02": ("turn", (0, 1, 0), turn), "head": ("turn", (1, 0, 0), 6.0),
                "UpperArm_R": ("reach", "R", (ear[0] - 0.02, ear[1], ear[2] - 0.06), (-0.7, -1.0, 0.2)),
                "Hand_R": ("at", "indexFinger_01_r", (ear[0] + 0.05, ear[1] + 0.15, ear[2] - 0.05)),
                "UpperArm_L": ("aim", "lowerarm_l", (0.15, -1.0, 0.05)), "lowerarm_l": ("aim", "Hand_L", (0.0, -0.4, -1.0))}
    boss = Character(scene, "The Boss (On The Phone)", "SK_Chr_Boss_Male_01", boss_at, 10.0, boss_pose(), people)
    hand = boss.joint("Hand_R")
    boss.attach("Hand_R", "SM_Prop_Cellphone_01", (hand[0] - 0.02, hand[1] + 0.04, hand[2] - 0.03), quat(180.0, -80.0, 90.0), name="Phone")
    pacing = scene.clip("Boss On The Phone", 9.0)
    pacing.track(boss.bone("spine_02"), "Transform", "Rotation",
                 [(0.0, boss.local_rotation(boss_pose(0.0), "spine_02"), "SmoothStep"),
                  (3.5, boss.local_rotation(boss_pose(14.0), "spine_02"), "SmoothStep"),
                  (6.0, boss.local_rotation(boss_pose(-8.0), "spine_02"), "SmoothStep"),
                  (9.0, boss.local_rotation(boss_pose(0.0), "spine_02"), "SmoothStep")], label="Boss spine_02")
    # The cleaner mopping the flood from the server room, earbuds in, unbothered.
    grip_r = (-0.04, 1.05, -0.36)
    floor_point = (0.24, 0.02, -1.12)

    def palm(world, index, side):
        wrist, knuckle = world[index["Hand_" + side]][0], world[index["indexFinger_01_" + side.lower()]][0]
        return scale3(add3(wrist, knuckle), 0.5)

    left_fix = [0.0, 0.0, 0.0]

    def mop_pose(sweep=0.0):
        shift = (sweep * 0.006, 0.0, 0.0)
        right = add3(grip_r, shift)
        left = add3(add3(add3(grip_r, scale3(sub3(floor_point, grip_r), 0.32)), scale3(shift, 0.7)), left_fix)
        return {"spine_01": ("turn", (1, 0, 0), -10.0), "spine_02": ("turn", (0, 1, 0), sweep * 0.5), "head": ("turn", (1, 0, 0), -18.0),
                "UpperArm_R": ("reach", "R", right, (-1.0, -0.6, 0.3)),
                "UpperArm_L": ("reach", "L", left, (1.0, -0.6, 0.3))}
    # The handle runs from the floor through the right palm; pull the left palm onto it (IK targets
    # the wrists, so correct the left target by how far its palm misses the line).
    for _ in range(4):
        _, index, world = solve_pose("SK_Chr_Cleaner_Female_01", mop_pose())
        right_palm, left_palm = palm(world, index, "R"), palm(world, index, "L")
        axis = norm3(sub3(right_palm, floor_point))
        along = sum(a * b for a, b in zip(sub3(left_palm, floor_point), axis))
        miss = sub3(add3(floor_point, scale3(axis, along)), left_palm)
        left_fix = add3(left_fix, miss)
    cleaner_at = (20.6, 0.0, 11.35)
    cleaner = Character(scene, "Cleaner (Mopping)", "SK_Chr_Cleaner_Female_01", cleaner_at, 15.0, mop_pose(), people)
    grip = palm(cleaner.world, cleaner.index, "R")
    lo, hi = bounds("SM_Prop_Mop_02")
    # The mop runs from her right hand down past the left to the floor ahead.
    axis = norm3(sub3(grip, floor_point))
    mop_rot = qarc((0, 1, 0), axis)
    centre = add3(floor_point, scale3(axis, (hi[1] - lo[1]) / 2))
    cleaner.attach("Hand_R", "SM_Prop_Mop_02", centre, mop_rot, name="Mop")
    mopping = scene.clip("Mopping", 2.4)
    for bone in ("spine_02", "UpperArm_R", "lowerarm_r", "UpperArm_L", "lowerarm_l"):
        mopping.track(cleaner.bone(bone), "Transform", "Rotation",
                      [(0.0, cleaner.local_rotation(mop_pose(-12.0), bone), "SmoothStep"),
                       (1.2, cleaner.local_rotation(mop_pose(12.0), bone), "SmoothStep"),
                       (2.4, cleaner.local_rotation(mop_pose(-12.0), bone), "SmoothStep")], label="Cleaner " + bone)
    return people, dict(hero=hero, sleeper=sleeper, loafer=loafer, guard=guard, boss=boss, cleaner=cleaner, laptop=laptop)


# ---------------------------------------------------------------------------------------------
# Little things that move


def build_motion(scene, pit_info, ceiling_lights, candle_light, micro_light, spark_light, balloons, tank_at, fish, cameras):
    life = scene.clip("Office Life", 12.0)
    # The rage-quitter's chair, still turning slowly after the shove.
    chair = pit_info["chair"]
    base = chair["Components"][0]["Rotation"]
    life.track(chair, "Transform", "Rotation", spin_keys(12.0, turns=1.0, steps=16, base=base), label="Spinning Chair")
    # The hero's panel, failing.
    hero_light = ceiling_lights["Hero Panel"]
    sound(scene, "Panel Buzz", "PanelBuzz", (0.0, 0.0, 0.0), hero_light, volume=0.3, near=0.5, far=6.0)
    pattern = [(0.0, 6.0), (2.1, 6.0), (2.15, 0.3), (2.2, 5.0), (2.3, 0.2), (2.45, 6.0), (7.0, 6.0), (7.05, 0.5), (7.4, 0.5),
               (7.45, 6.2), (7.6, 1.0), (7.7, 6.0), (12.0, 6.0)]
    life.track(hero_light, "Light", "Intensity", [(t, v, "Hold") for t, v in pattern], label="Hero Panel")
    corridor = ceiling_lights["Corridor Panel"]
    life.track(corridor, "Light", "Intensity", flicker_keys(12.0, 4.8, 0.7, 1.0, 0.25, seed=12, drop=0.18, interpolation="Hold"), label="Corridor Panel")
    life.track(spark_light, "Light", "Intensity", flicker_keys(12.0, 4.0, 0.0, 1.0, 0.05, seed=3, drop=0.5, interpolation="Hold"))
    life.track(candle_light, "Light", "Intensity", flicker_keys(12.0, 2.2, 0.75, 1.1, 0.1, seed=8))
    life.track(micro_light, "Light", "Intensity", flicker_keys(12.0, 3.0, 0.5, 1.0, 0.15, seed=21))
    # Balloons bobbing on their strings.
    for i, balloon in enumerate(balloons):
        pos = balloon["Components"][0]["Position"]
        rot = balloon["Components"][0]["Rotation"]
        keys_p, keys_r = [], []
        for k in range(7):
            t = k * 2.0
            dy = 0.04 * math.sin(k * 1.7 + i * 2.0)
            keys_p.append((t, [pos[0] + 0.03 * math.sin(k + i), pos[1] + dy, pos[2] + 0.03 * math.cos(k * 1.3 + i)], "SmoothStep"))
            keys_r.append((t, qmul(qaxis((0, 1, 0), 12.0 * math.sin(k * 0.9 + i)), rot), "SmoothStep"))
        keys_p[-1] = (12.0, keys_p[0][1], "SmoothStep")
        keys_r[-1] = (12.0, keys_r[0][1], "SmoothStep")
        life.track(balloon, "Transform", "Position", keys_p, label="Balloon %d" % (i + 1))
        life.track(balloon, "Transform", "Rotation", keys_r, label="Balloon %d" % (i + 1))
    # Fish, on lazy loops inside the tank (the tank runs north-south, 1.2 m long).
    for i, f in enumerate(fish):
        keys_p, keys_r = [], []
        steps = 48
        for k in range(steps + 1):
            t = 12.0 * k / steps
            a = 2 * math.pi * (k / steps) * (1 if i != 1 else -1) + i * 2.1
            p = [tank_at[0] + 0.12 * math.sin(2 * a + i), 0.95 + 0.12 * math.sin(3 * a + i * 1.3) + i * 0.05, tank_at[2] + 0.42 * math.cos(a)]
            a2 = a + 0.01 * (1 if i != 1 else -1)
            p2 = [tank_at[0] + 0.12 * math.sin(2 * a2 + i), 0.95 + 0.12 * math.sin(3 * a2 + i * 1.3) + i * 0.05, tank_at[2] + 0.42 * math.cos(a2)]
            heading = compass(p2[0] - p[0], p2[2] - p[2])
            keys_p.append((t, p, "Linear"))
            keys_r.append((t, quat(heading), "Linear"))
        life.track(f, "Transform", "Position", keys_p, label="Fish %d" % (i + 1))
        life.track(f, "Transform", "Rotation", keys_r, label="Fish %d" % (i + 1))
    # Security cameras panning.
    for i, (cam, at, aim) in enumerate(cameras):
        rot = cam["Components"][0]["Rotation"]
        keys = [(0.0, qmul(qaxis((0, 1, 0), -30.0), rot), "SmoothStep"), (5.0, qmul(qaxis((0, 1, 0), 30.0), rot), "SmoothStep"),
                (6.0, qmul(qaxis((0, 1, 0), 30.0), rot), "SmoothStep"), (11.0, qmul(qaxis((0, 1, 0), -30.0), rot), "SmoothStep"),
                (12.0, qmul(qaxis((0, 1, 0), -30.0), rot), "SmoothStep")]
        life.track(cam, "Transform", "Rotation", keys, label="Security Camera %d" % (i + 1))
    fan = next(e for e in scene.entities if e["Name"] == "Ceiling Fan")
    fan_clip = scene.clip("Ceiling Fan", 2.0)
    fan_clip.track(fan, "Transform", "Rotation", spin_keys(2.0, turns=1.0, steps=8, base=fan["Components"][0]["Rotation"]))
    # Paper planes: resignation letters, folded and thrown, gliding round the pit forever.
    planes = scene.clip("Paper Planes", 14.0)
    quit_seat = pit_info["quit"][0]
    for i in range(3):
        plane = put(scene, "Paper Plane", "SM_Prop_Paper_Plane_01", (quit_seat[0], 1.6, quit_seat[2]), 0.0, anchor="center",
                    materials=[standard(None, (0.85, 0.85, 0.82), 0.8)])
        keys_p, keys_r = [], []
        steps = 84
        cx, cz, rx, rz = 12.6, 11.2 + i * 0.4, 3.6 - i * 0.5, 2.6 - i * 0.3
        for k in range(steps + 1):
            t = 14.0 * k / steps
            a = 2 * math.pi * k / steps * (1 if i % 2 == 0 else -1) + i * 2.0

            def at(a):
                return [cx + rx * math.cos(a), 1.75 + 0.35 * math.sin(2 * a + i) + i * 0.2, cz + rz * math.sin(a)]
            p, p2 = at(a), at(a + 0.02 * (1 if i % 2 == 0 else -1))
            yaw, pitch = look_angles(p, p2)
            bank = -25.0 * (1 if i % 2 == 0 else -1)
            keys_p.append((t, p, "Linear"))
            # The plane model's nose is -Z: point it along the path.
            keys_r.append((t, quat(yaw + 180.0, -pitch, bank), "Linear"))
        planes.track(plane, "Transform", "Position", keys_p, label="Plane %d" % (i + 1))
        planes.track(plane, "Transform", "Rotation", keys_r, label="Plane %d" % (i + 1))
    return life


# ---------------------------------------------------------------------------------------------
# The camera: a looping tour of the story, cut into shots. Each shot is a slow move between two
# framings (position, look-at, FOV, focus distance), written as dense linear keys.

SHOTS = [
    # name, seconds, (from, to) positions, (from, to) look-at targets, fov, focus subject
    ("Through the storm glass", 9.0, ((14.2, 2.0, 19.6), (13.6, 1.7, 18.6)), ((13.2, 1.1, 8.0), (13.6, 1.0, 8.2)), 44.0, None),
    ("The last developer", 8.0, ((12.6, 1.5, 6.6), (12.9, 1.35, 7.0)), ((14.4, 1.05, 9.3), (14.1, 1.0, 9.1)), 46.0, (13.8, 1.1, 8.0)),
    ("Gold master in...", 6.0, ((12.0, 1.45, 9.2), (12.2, 1.6, 9.6)), ((12.5, 2.25, 12.0), (12.5, 2.25, 12.0)), 40.0, (12.5, 2.25, 11.95)),
    ("Asleep on the keyboard", 7.0, ((8.4, 1.25, 7.0), (8.7, 1.15, 7.3)), ((9.4, 0.85, 8.4), (9.4, 0.85, 8.4)), 42.0, (9.35, 0.9, 8.3)),
    ("The rage quit", 8.0, ((9.5, 1.6, 17.15), (9.9, 1.45, 17.1)), ((11.5, 0.35, 15.9), (11.5, 0.45, 15.8)), 52.0, (11.6, 0.3, 16.0)),
    ("Days since last fire: 0", 9.0, ((16.6, 1.6, 10.6), (17.5, 1.5, 11.2)), ((20.5, 1.6, 16.2), (20.3, 1.8, 16.5)), 48.0, (20.4, 1.8, 16.4)),
    ("Somebody has to mop", 7.0, ((21.9, 1.4, 12.25), (21.7, 1.3, 12.3)), ((20.4, 0.9, 11.0), (20.5, 0.9, 11.1)), 50.0, (20.6, 1.1, 11.35)),
    ("Paper jam", 6.0, ((21.5, 0.9, 8.4), (21.8, 1.0, 8.7)), ((24.2, 0.8, 9.8), (24.2, 0.9, 9.8)), 50.0, (23.9, 0.9, 9.7)),
    ("Q4 roadmap", 8.0, ((18.3, 1.8, 6.7), (18.8, 1.7, 6.3)), ((24.7, 1.5, 3.75), (24.7, 1.5, 3.75)), 50.0, (24.7, 1.6, 3.75)),
    ("Security", 7.0, ((13.3, 1.6, 0.35), (13.5, 1.5, 0.4)), ((14.8, 0.95, 2.1), (14.8, 0.95, 2.1)), 50.0, (14.8, 1.0, 2.05)),
    ("The party that never happened", 9.0, ((5.4, 1.5, 5.2), (5.0, 1.3, 4.7)), ((2.8, 1.0, 2.6), (2.6, 0.95, 2.5)), 50.0, (3.7, 1.0, 3.2)),
    ("Still compiling", 7.0, ((5.3, 1.7, 7.6), (5.0, 1.6, 7.9)), ((2.5, 0.7, 10.1), (2.5, 0.7, 10.1)), 48.0, (2.6, 0.8, 10.0)),
    ("It's basically done", 8.0, ((6.6, 1.6, 13.1), (6.2, 1.6, 13.5)), ((2.2, 1.5, 16.6), (2.2, 1.5, 16.6)), 44.0, (2.2, 1.5, 16.6)),
    ("3:47 AM", 9.0, ((24.2, 2.75, 0.8), (23.6, 2.7, 1.6)), ((12.0, 0.6, 11.0), (12.5, 0.6, 11.5)), 60.0, None),
]


def build_camera(scene):
    sky = {"CloudAltitude": 1500.0, "CloudCoverage": 0.92, "CloudDensity": 1.4, "CloudThickness": 2600.0,
           "Latitude": 47.0, "Month": 10, "MoonAscendingNode": 124.68, "MoonBrightness": 0.6, "MoonOrbitInclination": 5.145,
           "MoonPhase": 0.55, "MoonSize": 2.0, "StarBrightness": 0.4, "SunSize": 2.4, "Time": 3.78, "TimeScale": 0.0,
           "Turbidity": 4.0, "WindDirection": 200.0, "WindSpeed": 18.0}
    post = {"Type": "PostProcess", "Tonemapper": "ACES", "ExposureCompensation": 0.6, "AutoExposure": True,
            "AutoExposureMinEV": -3.5, "AutoExposureMaxEV": 1.5, "AutoExposureSpeed": 1.2,
            "Bloom": True, "BloomThreshold": 1.0, "BloomIntensity": 0.16, "BloomRadius": 1.0,
            "AmbientOcclusion": True, "AORadius": 0.45, "AOIntensity": 1.0,
            "FXAA": False, "TemporalAA": True, "TemporalSharpness": 0.35,
            "DepthOfField": True, "DoFFocusDistance": 3.0, "DoFAperture": 2.0, "DoFSensorHeight": 24.0, "DoFMaxBlurRadius": 14.0,
            "Fog": True, "FogColor": [0.2, 0.21, 0.24], "FogDensity": 0.011, "FogHeight": 0.0, "FogHeightFalloff": 0.0,
            "FogStartDistance": 1.0, "FogMaxOpacity": 0.5, "FogSunIntensity": 0.6, "FogAnisotropy": 0.25,
            "VolumetricFog": True, "VolumetricDistance": 30.0, "VolumetricSteps": 48,
            "Saturation": 1.05, "Contrast": 1.12, "Temperature": -0.04, "Tint": 0.0, "Gamma": 1.0, "Lift": 0.0, "Gain": 1.0,
            "VignetteIntensity": 0.35, "VignetteSmoothness": 0.6,
            "Graphs": [GRAPHS + "NightShift.shadergraph"]}
    first = SHOTS[0]
    camera = {"Type": "Camera", "ClearType": "Procedural", "ClearColor": [0.02, 0.025, 0.04], "Far": 900.0, "Near": 0.05,
              "FieldOfView": first[4], "IsCurrent": True, "Projection": "Perspective", "OrthographicSize": 5.0, "ProceduralSky": sky}
    start, target = first[2][0], first[3][0]
    camera_entity = scene.entity("Main Camera", [transform(start, rotation=look(start, target)), camera, post])
    total = sum(shot[1] for shot in SHOTS)
    tour = scene.clip("Camera Tour", total)
    pos_keys, rot_keys, fov_keys, focus_keys = [], [], [], []
    t0 = 0.0
    for name, seconds, (p0, p1), (a0, a1), fov, focus in SHOTS:
        steps = int(seconds * 2)
        for k in range(steps + 1):
            u = k / steps
            e = u * u * (3 - 2 * u) * 0.35 + u * 0.65  # mostly linear, eased at the ends
            p = [a + (b - a) * e for a, b in zip(p0, p1)]
            aim = [a + (b - a) * e for a, b in zip(a0, a1)]
            # Shots cut: each shot's last key holds until the next shot's first frame.
            t = t0 + u * (seconds - 1.0 / FPS)
            mode = "Hold" if k == steps else "Linear"
            pos_keys.append((t, p, mode))
            rot_keys.append((t, look(p, aim), mode))
            fov_keys.append((t, fov - 2.0 * u, mode))
            focus_keys.append((t, length3(sub3(focus, p)) if focus else 40.0, mode))
        t0 += seconds
    tour.track(camera_entity, "Transform", "Position", pos_keys, label="Camera")
    tour.track(camera_entity, "Transform", "Rotation", rot_keys, label="Camera")
    tour.track(camera_entity, "Camera", "FieldOfView", fov_keys, label="Camera")
    tour.track(camera_entity, "PostProcess", "DoFFocusDistance", focus_keys, label="Camera")
    return camera_entity


def texture_metas():
    """The pack's texture sidecars are Unity YAML, which the engine can't read: write JSON ones for the
    textures used here, keeping the originals under .tmp/LaunchNightImport."""
    for texture in (ATLAS, ATLAS_B, ATLAS_C, NET, LaunchNightGraphs.ARCADE):
        sidecar = ROOT / (texture + ".meta")
        if sidecar.exists():
            try:
                json.loads(sidecar.read_text())
                continue
            except json.JSONDecodeError:
                backup = ROOT / ".tmp/LaunchNightImport" / (sidecar.name + ".unity")
                backup.parent.mkdir(parents=True, exist_ok=True)
                if not backup.exists():
                    backup.write_bytes(sidecar.read_bytes())
        sidecar.write_text(json.dumps(dict(FileType=texture.rsplit(".", 1)[1], Format="None",
                                           GUID=hashlib.sha256(texture.encode()).hexdigest()[:16],
                                           MIPs=True, Quality="h", Type="Default"), indent=4) + "\n")


def asset_meta(path):
    meta = ROOT / (path + ".meta")
    if not meta.exists():
        meta.write_text(json.dumps({"FileType": "sequence", "GUID": guid("asset/" + path)}, indent=4) + "\n")
    return json.loads(meta.read_text())["GUID"]


def build(write=True):
    scene = Scene()
    camera = build_camera(scene)
    build_shell(scene)
    ceiling_lights = build_lighting(scene)
    outside, storm = build_outside(scene)
    pit, pit_info = build_pit(scene, ceiling_lights)
    room, alarm, burning = build_server_room(scene)
    build_boss_office(scene)
    kitchen, candle_light, micro_light, balloons = build_kitchen(scene)
    lounge, tank_at, fish = build_lounge(scene)
    build_conference(scene)
    corridor, spark_light = build_corridor(scene)
    lobby, guard_desk, cameras = build_lobby(scene)
    build_people(scene, pit_info, guard_desk)
    build_motion(scene, pit_info, ceiling_lights, candle_light, micro_light, spark_light, balloons, tank_at, fish, cameras)
    # Every clip's player lives on the entity it was created for.
    references = {}
    for clip in scene.clips.values():
        clip.player["Components"].append(clip.component())
    if write:
        texture_metas()
        folder = ROOT / ANIMATIONS
        folder.mkdir(parents=True, exist_ok=True)
        for clip in scene.clips.values():
            (ROOT / clip.path).write_text(json.dumps(clip.asset(), indent=1) + "\n")
            references[asset_meta(clip.path)] = clip.path
    document = {"Version": 2, "Cores": [], "Entities": scene.entities, "AssetReferences": references}
    if write:
        (ROOT / SCENE).write_text(json.dumps(document, indent=1) + "\n")
    return document


def write_flow():
    """Assets/Scenes/LaunchNight.edscript: every graph compiles and previews, then the scene plays."""
    first = SHOTS[0][2][0]
    lines = ["# Compile and preview the Launch Night shader graphs, then play the scene: the tour must move the camera.",
             "# Engine/Tools/Headless.sh .build/Editor_Debug/Havana --scene Assets/Scenes/LaunchNight.lvl --editor-exec Assets/Scenes/LaunchNight.edscript",
             "wait 30"]
    lines += ["assert-exists %s" % name for name in ("Main Camera", "The Last Developer", "Asleep On The Keyboard", "Compiling In The Beanbag",
                                                   "Security Guard (Asleep)", "The Boss (On The Phone)", "Cleaner (Mopping)", "BUILD-01", "Camera Tour")]
    for name in LaunchNightGraphs.GRAPHS:
        path = GRAPHS + name + ".shadergraph"
        lines += ["sg-open " + path, "sg-assert-compiled", "sg-wait-preview", "sg-assert-preview", "sg-close " + path]
    lines += ["wait 10", "play", "wait 120", "assert-playing 1"]
    # The ambience loops start with Play.
    lines += ["assert-audio %s | 1" % name for name in ("Storm Sound", "Room Tone", "Fire Sound", "Fire Alarm", "Typing Sound", "Snoring",
                                                         "Coffee Sound", "Panel Buzz")]
    lines += ["assert-field Main Camera | Transform.Position | != [%s]" % ", ".join("%g" % v for v in first),
              "stop", "assert-playing 0", "assert-audio Storm Sound | 0", "wait 10", ""]
    path = ROOT / "Assets/Scenes/LaunchNight.edscript"
    text = "\n".join(lines)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def write_graphs():
    folder = ROOT / GRAPHS
    folder.mkdir(parents=True, exist_ok=True)
    for name, make in LaunchNightGraphs.GRAPHS.items():
        text = json.dumps(make().document(), indent=4) + "\n"
        path = folder / (name + ".shadergraph")
        if not path.exists() or path.read_text() != text:
            path.write_text(text)


if __name__ == "__main__":
    write_graphs()
    if "--graphs" not in sys.argv:
        document = build()
        write_flow()
        print("wrote", SCENE, len(document["Entities"]), "entities")
