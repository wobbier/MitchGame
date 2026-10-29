#!/usr/bin/env python3
"""Rebuild the concert lighting study from the arena photo, using local assets.

Run from any directory. Overwrites only ConcertTest.lvl, its generated crowd
assets and the LED wall's render texture. All dimensions are metres; the two
light rigs remain editable in Havana.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import random

from ConcertAssets import add_performer, build_crowd_assets

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Assets/Scenes/Tests/ConcertTest.lvl"
# The LED wall's live feed: a camera crew member in the stands films the singer into it.
SCREEN_FEED = "Assets/Textures/ConcertTest/LedWall.rendertexture"
# Close to the wall's 23 x 12 m shape.
SCREEN_FEED_SIZE = (384, 200)
PANEL_INTENSITY = 10000
PANEL_CONE = (2.0, 5.5)   # inner / outer half-angles: a narrow, soft-edged panel beam


def write_render_texture(path, width, height):
    """A .rendertexture asset and its meta (as the engine writes metas: no trailing newline)."""
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(Width=width, Height=height, Mips=True, Wrap="Clamp"), indent=4) + "\n")
    meta = dict(FileType="rendertexture", GUID=hashlib.sha256(path.encode()).hexdigest()[:16])
    Path(str(target) + ".meta").write_text(json.dumps(meta, indent=4))


def transform(position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    return dict(Type="Transform", Position=list(position), Rotation=list(rotation),
                Scale=[scale] * 3 if isinstance(scale, (int, float)) else list(scale))


def aim(source, target):
    x, y, z = (target[i] - source[i] for i in range(3))
    return [math.degrees(math.atan2(-y, math.hypot(x, z))),
            math.degrees(math.atan2(x, z)), 0]


class Scene:
    def __init__(self):
        self.entities = []

    def entity(self, name, components, parent=None):
        result = dict(GUID=hashlib.sha256(("concert-test/" + name).encode()).hexdigest()[:16],
                      Name=name, DestroyOnLoad=True, Components=components)
        if parent:
            result["Parent"] = parent["GUID"] if isinstance(parent, dict) else parent
        self.entities.append(result)
        return result

    def group(self, name, position=(0, 0, 0), rotation=(0, 0, 0), parent=None):
        return self.entity(name, [transform(position, rotation)], parent)

    def mesh(self, name, position, full_size, color, shape="Cube", emission=0,
             parent=None, rotation=(0, 0, 0), shadows=True, metallic=0, roughness=0.7,
             texture=None):
        # Cube, cylinder and sphere all span [-1,1] on each axis.
        scale = [n * .5 for n in full_size]
        material = dict(Type="StandardMaterial", DiffuseColor=list(color),
                        Roughness=roughness, Metallic=metallic,
                        EmissiveColor=list(color), EmissiveIntensity=emission)
        if texture:
            material["Textures"] = dict(Diffuse=dict(Path=texture), Emissive=dict(Path=texture))
        return self.entity(name, [transform(position, rotation, scale),
            dict(Type="Mesh", MeshType=shape, CastShadows=shadows, Material=material)], parent)

    def rod(self, name, start, end, width, color, parent=None, emission=0):
        center = [(start[i] + end[i]) * .5 for i in range(3)]
        length = math.dist(start, end)
        return self.mesh(name, center, (width, width, length), color, parent=parent,
                         rotation=aim(start, end), emission=emission)


def build():
    scene = Scene()
    rng = random.Random(291026)
    crowd_assets = build_crowd_assets()
    camera_position, camera_target = (27, 16.5, -35), (-1, 9, 4)
    scene.entity("Main Camera", [transform(camera_position, aim(camera_position, camera_target)),
        dict(Type="Camera", IsCurrent=True, ClearType="Color", ClearColor=[.012, .016, .023],
             Projection="Perspective", FieldOfView=47, Near=.1, Far=150),
        dict(Type="PostProcess", AutoExposure=False, ExposureCompensation=-.25,
             Tonemapper="ACES", Bloom=True, BloomIntensity=.07, BloomThreshold=1.2,
             AmbientOcclusion=True, AORadius=.55, AOIntensity=.8,
             Fog=True, FogColor=[.0008, .0011, .0016], FogDensity=.024,
             FogHeight=0, FogHeightFalloff=.012, FogMaxOpacity=1,
             FogStartDistance=0, FogSunIntensity=.55, FogAnisotropy=.45,
             FogLocalAnisotropy=.45, VolumetricFog=True, VolumetricDistance=110,
             VolumetricSteps=64, VolumetricTemporal=True,
             DepthOfField=False, TemporalAA=True, TemporalSharpness=.2, FXAA=True,
             VignetteIntensity=.22, VignetteSmoothness=.7, Saturation=.83)])

    arena = scene.group("Arena - hockey floor and seating bowl")
    dark = (.036, .041, .049)
    steel = (.12, .14, .16)
    scene.mesh("Arena Floor - 34 x 64 m", (0, -.2, 0), (34, .4, 64), (.095, .105, .115),
               parent=arena, roughness=.87)
    scene.mesh("Arena Foundation", (0, -1.1, 0), (66, 1.8, 100), dark, parent=arena)

    # A stepped oval bowl, with radial aisles cut through the spectators below.
    for row in range(10):
        rx, rz, y = 18.5 + row * 1.08, 33 + row * 1.1, row * .86
        for segment in range(48):
            a = (segment + .5) * math.tau / 48
            x, z = rx * math.cos(a), rz * math.sin(a)
            tx, tz = -rx * math.sin(a), rz * math.cos(a)
            length = math.hypot(tx, tz) * math.tau / 48 * 1.035
            yaw = math.degrees(math.atan2(tx, tz))
            scene.mesh(f"Bowl riser {row:02d}-{segment:02d}", (x, y - .38, z),
                       (1.35, .76, length), dark, rotation=(0, yaw, 0), parent=arena)
    # Dim concourse bands and roof hardware read as silhouettes above the beams.
    for y in (11.2, 17.4):
        for segment in range(64):
            a, b = segment * math.tau / 64, (segment + 1) * math.tau / 64
            scene.rod(f"Concourse rail {y}-{segment}", (30*math.cos(a), y, 46*math.sin(a)),
                      (30*math.cos(b), y, 46*math.sin(b)), .13, steel, parent=arena)
    scene.mesh("Arena Roof", (0, 29.5, 0), (68, 1, 102), (.018, .021, .027), parent=arena)
    for z in (-30, -15, 0, 15, 30):
        for y in (26.8, 28):
            scene.rod(f"Roof truss chord {z} {y}", (-30, y, z), (30, y, z), .18, steel, arena)
        for x in range(-30, 30, 3):
            scene.rod(f"Roof truss brace {z} {x}", (x, 26.8, z), (x+3, 28, z), .11, steel, arena)
    for x in (-22, 22):
        scene.rod(f"Longitudinal roof truss {x}", (x, 27.3, -43), (x, 27.3, 43), .22, steel, arena)

    stage = scene.group("Stage - circular satellite platform")
    scene.mesh("Circular stage skirt", (0, .44, 1), (6.6, .88, 6.6), (.035, .04, .047),
               "Cylinder", parent=stage, roughness=.55, metallic=.3)
    scene.mesh("Brushed stage rim", (0, .94, 1), (6.65, .12, 6.65), (.46, .49, .51),
               "Cylinder", parent=stage, metallic=.8, roughness=.28)
    scene.mesh("Stage deck", (0, 1.015, 1), (6.3, .03, 6.3), (.2, .215, .23),
               "Cylinder", parent=stage, metallic=.25, roughness=.6)
    for stripe in range(-5, 6):
        x = stripe * .5
        half_length = math.sqrt(3.06**2-x*x)
        scene.mesh(f"Deck groove {stripe}", (x, 1.034, 1), (.012, .004, half_length*2),
                   (.07, .08, .09), parent=stage, shadows=False)
    for a in range(0, 360, 30):
        angle = math.radians(a)
        scene.mesh(f"Stage edge marker {a}", (3.23*math.cos(angle), .92, 1+3.23*math.sin(angle)),
                   (.10, .025, .10), (.75, .8, .8), emission=.55, parent=stage, shadows=False)
    # A low runway to the blacked-out main stage helps describe the floor plane.
    scene.mesh("Runway", (0, .48, 14.3), (2.4, .96, 20.4), (.04, .045, .055), parent=stage)
    scene.mesh("Rear main stage", (0, .75, 28), (18, 1.5, 7), (.035, .04, .05), parent=stage)
    # The LED wall behind the main stage shows the crowd camera's live close-up of the singer
    # (the photo's close-up). Dark when off; the feed is its emission. The cube's faces map v
    # up the face, so Tiling (1, -1) with Offset (0, 1) shows the image upright.
    write_render_texture(SCREEN_FEED, *SCREEN_FEED_SIZE)
    scene.entity("LED video wall", [transform((0, 7, 32), scale=(11.5, 6, .125)),
        dict(Type="Mesh", MeshType="Cube", CastShadows=False, Material=dict(
             Type="StandardMaterial", DiffuseColor=[.02, .02, .022], Roughness=.4, Metallic=0,
             EmissiveColor=[1, 1, 1], EmissiveIntensity=5.0, Tiling=[1, -1], Offset=[0, 1],
             Textures=dict(Emissive=dict(Path=SCREEN_FEED))))], stage)
    # The screen's own glow into the haze and onto the main stage: a near-hemisphere
    # rectangle light the size of the wall, facing the audience (-Z).
    scene.entity("LED video wall glow", [transform((0, 7, 31.85), (0, 180, 0)),
        dict(Type="Light", LightType="Rectangle", Color=[.9, .93, 1], Intensity=4,
             Range=28, RectangleWidth=23, RectangleHeight=12,
             InnerConeAngle=30, OuterConeAngle=89, CastShadows=False)], stage)
    for x in (-9, 9):
        for i in range(7):
            scene.mesh(f"Line array {x} {i}", (x, 9.2-i*.48, 25.5-i*.07), (1.0, .43, .65),
                       (.025, .03, .038), parent=stage, rotation=(i*2, 0, 0))
    add_performer(scene, "Singer", (0, 1.04, 1), facing=145, parent=stage)

    # The camera crew: an operator on a riser in a stand aisle (aisle 11, second row), filming
    # the singer's lit front with a long lens into the LED wall's feed. The wall stays out of shot.
    crew = scene.group("Camera crew - stand aisle")
    aisle = (11 + .03) * math.tau / 12
    floor_x, floor_z, floor_y = 20.56 * math.cos(aisle), 35.1 * math.sin(aisle), 2 * .86 + .02
    scene.mesh("Camera riser", (floor_x, floor_y + .1, floor_z), (1.1, .2, 1.1), (.03, .034, .04),
               parent=crew)
    operator = copy.deepcopy(crowd_assets["idle_male"])
    for part in operator["Parts"].values():
        part["Material"].update(DiffuseColor=[.05, .05, .055], Roughness=.9, EmissiveColor=[.05, .05, .055],
                                EmissiveIntensity=.006)
    facing = math.degrees(math.atan2(-floor_x, 1 - floor_z)) + 180
    scene.entity("Camera operator", [transform((floor_x + .25, floor_y + .2, floor_z - .2), (0, facing, 0)),
                                     operator], crew)
    lens_position, lens_target = (floor_x - .1, floor_y + 1.75, floor_z + .1), (0, 2.0, 1)
    crowd_camera = scene.entity("Crowd Camera", [transform(lens_position, aim(lens_position, lens_target)),
        dict(Type="Camera", IsCurrent=False, ClearType="Color", ClearColor=[.012, .016, .023],
             Projection="Perspective", FieldOfView=6, Near=.1, Far=90,
             TargetTexture=SCREEN_FEED, UpdateInterval=1,
             SunShadows=False, AmbientOcclusion=False, VolumetricFog=False),
        # The arena's haze without the expensive passes (the camera switches them off).
        dict(Type="PostProcess", AutoExposure=False, ExposureCompensation=1.8,
             Tonemapper="ACES", Bloom=True, BloomIntensity=.05, BloomThreshold=1.2,
             AmbientOcclusion=True, Fog=True, FogColor=[.0008, .0011, .0016], FogDensity=.024,
             FogHeight=0, FogHeightFalloff=.012, FogMaxOpacity=1, FogStartDistance=0,
             FogSunIntensity=.55, FogAnisotropy=.45, FogLocalAnisotropy=.45, VolumetricFog=True,
             VolumetricDistance=110, VolumetricSteps=64, VolumetricTemporal=True,
             DepthOfField=False, TemporalAA=False, FXAA=True, VignetteIntensity=.1, Saturation=.95)], crew)
    scene.mesh("Broadcast camera body", (0, -.05, -.32), (.22, .26, .5), (.02, .02, .024),
               parent=crowd_camera, shadows=False, roughness=.5)
    scene.mesh("Broadcast camera lens", (0, -.05, .02), (.13, .13, .22), (.01, .01, .012), "Cylinder",
               parent=crowd_camera, rotation=(90, 0, 0), shadows=False, roughness=.3)
    for i, x in enumerate((-.85, 1.3)):
        scene.mesh(f"Stage wedge monitor {i}", (x, 1.2, -.9), (.62, .32, .43),
                   (.025, .03, .035), rotation=(-18, 0, 0), parent=stage)

    rigs = scene.group("Lighting - two contrasting throws")
    # Color cameras otherwise inherit the renderer's legacy daylight fallback.
    # An explicit zero-energy directional keeps this enclosed arena unlit.
    scene.entity("Indoor ambient - suppress sky fallback", [transform(),
        dict(Type="Light", LightType="Directional", DirectionalSource="Manual",
             Color=[0, 0, 0], Intensity=0, CastShadows=False)], rigs)
    key_position, key_target = (-22, 25, -12), (0, 2.05, 1)
    key_rotation = aim(key_position, key_target)
    key = scene.group("Followspot Fixture", key_position, key_rotation, rigs)
    scene.mesh("Followspot housing", (0, 0, -.45), (.58, .58, 1.2), steel, parent=key)
    scene.mesh("Followspot lens", (0, 0, .17), (.28, .28, .03), (.95, .91, .82),
               emission=12, parent=key, shadows=False)
    scene.entity("Performer Spotlight", [transform((0, 0, .24)),
        dict(Type="Light", LightType="Spot", Color=[1, .94, .84], Intensity=100000,
             Range=65, InnerConeAngle=1.8, OuterConeAngle=3.0, CastShadows=True,
             ShadowBias=.4, ShadowNormalBias=1.0)], key)

    bank_position, bank_target = (13, 17, 17), (-1.5, .5, -.5)
    bank = scene.group("Box Light Bank", bank_position, aim(bank_position, bank_target), rigs)
    scene.mesh("Bank backing frame", (0, 0, -.26), (3.45, 3.15, .25), (.045, .055, .065), parent=bank)
    wash = scene.group("Crowd Wash", parent=bank)
    for row in range(4):
        for col in range(3):
            center = ((col-1)*1.04, (row-1.5)*.74, 0)
            # Each panel has its own emitter and aim. A gentle outward fan lets the
            # twelve soft beams overlap into one wash across the stage and audience.
            fixture = scene.group(f"Box light fixture {row+1}-{col+1}", center,
                                  (-(row-1.5)*5, (col-1)*6, 0), wash)
            scene.mesh(f"Box light housing {row+1}-{col+1}", (0, 0, 0),
                       (.94, .62, .38), steel, parent=fixture)
            scene.mesh(f"Box light luminous face {row+1}-{col+1}", (0, 0, .205),
                       (.79, .47, .025), (.84, .96, 1), emission=18, parent=fixture, shadows=False)
            # A rectangle light the size of the luminous face: the beam leaves the whole
            # panel and feathers out between the inner and outer cone angles.
            scene.entity(f"Box light beam {row+1}-{col+1}", [transform((0, 0, .225)),
                dict(Type="Light", LightType="Rectangle", Color=[.83, .94, 1],
                     Intensity=PANEL_INTENSITY, Range=62, RectangleWidth=.79, RectangleHeight=.47,
                     InnerConeAngle=PANEL_CONE[0], OuterConeAngle=PANEL_CONE[1],
                     CastShadows=False)], fixture)
    scene.rod("Bank suspension left", (12, 28, 17), (12, 18.5, 17), .06, steel, rigs)
    scene.rod("Bank suspension right", (14, 28, 17), (14, 18.5, 17), .06, steel, rigs)

    audience = scene.group("Audience - floor and tier silhouettes")
    palette = [(.28,.29,.31), (.36,.38,.4), (.5,.46,.42), (.22,.26,.32),
               (.6,.57,.52), (.34,.27,.31), (.63,.65,.64), (.18,.2,.22)]
    count = 0

    def spectator(position, section, index):
        nonlocal count
        pose = "handsup" if rng.random() < .22 else "idle"
        sex = "male" if rng.random() < .5 else "female"
        model = copy.deepcopy(crowd_assets[f"{pose}_{sex}"])
        color = palette[rng.randrange(len(palette))]
        for part in model["Parts"].values():
            part["Material"].update(DiffuseColor=list(color), Roughness=.9,
                                    EmissiveColor=list(color), EmissiveIntensity=.006)
        # Source pawns face -Z. Turn each inward towards the satellite stage.
        direction = math.degrees(math.atan2(-position[0], 1-position[2])) + 180
        scale = rng.uniform(.91, 1.09)
        scene.entity(f"{section} spectator {index:04d}",
                     [transform(position, (0, direction+rng.uniform(-16,16), 0), scale), model], audience)
        count += 1

    for row in range(48):
        z = -27 + row*1.09
        for col in range(28):
            x = -15 + col*1.1
            if (x*x+(z-1)**2 < 4.35**2 or (abs(x)<2 and z>3) or
                    (-21<z<-17) or (7<x<9) or (7.2<x<12.8 and -26<z<-22) or rng.random()<.045):
                continue
            spectator((x+rng.uniform(-.19,.19), 0, z+rng.uniform(-.18,.18)), "Floor", row*28+col)
    for row in range(9):
        rx, rz, y = 18.4+row*1.08, 32.9+row*1.1, row*.86+.02
        slots = 138+row*4
        for col in range(slots):
            a = (col+.25)*math.tau/slots
            # Twelve radial aisles; empty paths and occasional glowing step edges.
            if (a/(math.tau/12)) % 1 < .075 or rng.random()<.025:
                continue
            spectator((rx*math.cos(a), y, rz*math.sin(a)), "Tier", row*200+col)
        for aisle in range(12):
            a = (aisle+.03)*math.tau/12
            scene.mesh(f"Dim aisle step {row}-{aisle}", (rx*math.cos(a), y+.04, rz*math.sin(a)),
                       (.48, .025, .06), (.85,.48,.19), emission=.24, parent=arena, shadows=False,
                       rotation=(0, 90-math.degrees(a), 0))

    # A dim FOH island and a few raised phones establish the observer's position.
    foh = scene.group("Front of house - mix position")
    scene.mesh("Mix riser", (10, .2, -24), (5, .4, 3), (.025,.03,.035), parent=foh)
    scene.mesh("Mix desk", (10, 1.15, -24), (3.8,.35,1.2), (.065,.07,.08), parent=foh)
    for i in range(4):
        scene.mesh(f"Console display {i}", (8.7+i*.85, 1.4, -23.9), (.61,.025,.38),
                   (.17,.32,.37), emission=1.1, parent=foh, rotation=(-12,0,0), shadows=False)
        for fader in range(6):
            scene.mesh(f"Console fader {i}-{fader}", (8.45+i*.85+fader*.09, 1.34, -24.32),
                       (.025,.015,.04), (.6,.6,.52), emission=.3, parent=foh, shadows=False)
    for i in range(34):
        x, z = rng.uniform(-14,14), rng.uniform(-26,23)
        if x*x+(z-1)**2<30 or abs(x)<2:
            continue
        scene.mesh(f"Audience phone {i:02d}", (x, rng.uniform(1.65,2.15), z), (.085,.13,.018),
                   (.55,.64,.7), emission=rng.uniform(.6,1.6), parent=audience,
                   rotation=(rng.uniform(-20,20), rng.uniform(-50,50), 0), shadows=False)

    names = [e["Name"] for e in scene.entities]
    assert len(names) == len(set(names)), "Duplicate entity names"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(dict(Version=2, Cores=[], Entities=scene.entities), indent=2)+"\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(scene.entities)} entities, {count} spectators, "
          "one performer spotlight, twelve rectangle panel lights and the LED wall's crowd camera feed")


if __name__ == "__main__":
    build()
