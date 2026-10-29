#!/usr/bin/env python3
"""Rebuild the render texture showcase. Python 3, no packages.

Run from any directory. Overwrites Assets/Scenes/Showcase/RenderTexture.lvl and the two render
texture assets in Assets/Textures/RenderTexture/ (with their metas).

A studio set is filmed by two render texture cameras: a studio camera (full resolution, every
frame) and a security camera (low resolution, every other frame, with its sun shadows, ambient
occlusion and volumetric fog switched off on the camera although its post settings ask for them).
The main camera looks at a wall of monitors showing the feeds through each kind of consumer:
emissive, diffuse (lit by a spot light), and a shader graph (Examples/CameraFeed, scan lines). A big
monitor on the set is in the studio camera's own shot, so it shows black in that feed (a camera
never samples its own target) and the studio feed in the security camera's. A turntable carries
most of the props round, so the feeds visibly update (25 degrees a second: 200 degrees when the
480-frame capture lands, so a stale feed can't match).
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "Assets/Scenes/Showcase/RenderTexture.lvl"
TEXTURES = "Assets/Textures/RenderTexture/"
STUDIO_FEED = TEXTURES + "StudioFeed.rendertexture"
SECURITY_FEED = TEXTURES + "SecurityFeed.rendertexture"
CAMERA_FEED = "Assets/ShaderGraphs/Examples/CameraFeed.shadergraph"

# The built-in primitives map v up the face, images map it down: this flips them upright.
UPRIGHT = dict(Tiling=[1, -1], Offset=[0, 1])


def guid(name):
    return hashlib.sha256(("render-texture-showcase/" + name).encode()).hexdigest()[:16]


def transform(position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    # Euler degrees: pitch (positive looks down), yaw (0 looks along +Z), roll.
    return dict(Type="Transform", Position=list(position), Rotation=list(rotation), Scale=list(scale))


def material(color=(1, 1, 1), roughness=0.6, metallic=0.0, emissive=None, diffuse=None, glow=None):
    result = dict(Type="StandardMaterial", DiffuseColor=list(color), Roughness=roughness, Metallic=metallic)
    textures = {}
    if emissive:
        texture, intensity = emissive
        result.update(EmissiveColor=[1, 1, 1], EmissiveIntensity=intensity)
        textures["Emissive"] = dict(Path=texture)
    if glow:
        glow_color, intensity = glow
        result.update(EmissiveColor=list(glow_color), EmissiveIntensity=intensity)
    if diffuse:
        textures["Diffuse"] = dict(Path=diffuse)
    if textures:
        result["Textures"] = textures
        result.update(UPRIGHT)
    return result


def write_render_texture(path, settings):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(settings, indent=4) + "\n")
    # As the engine writes metas (json dump(4), no trailing newline).
    meta = {"FileType": "rendertexture", "GUID": hashlib.sha256(path.encode()).hexdigest()[:16]}
    Path(str(target) + ".meta").write_text(json.dumps(meta, indent=4))


def build():
    entities = []

    def entity(name, components, parent=None):
        item = dict(GUID=guid(name), Name=name, DestroyOnLoad=True, Components=components)
        if parent:
            item["Parent"] = guid(parent)
        entities.append(item)

    def mesh(name, kind, position, scale, surface, rotation=(0, 0, 0), shadows=True, parent=None, script=None):
        components = [transform(position, rotation, scale),
                      dict(Type="Mesh", MeshType=kind, CastShadows=shadows, Material=surface)]
        if script:
            script_name, fields = script
            components.append(dict(Type="ScriptComponent", ScriptName=script_name, ScriptFields=json.dumps(fields)))
        entity(name, components, parent)

    def light(name, kind, position, rotation, color, intensity, shadows=False, extra=None):
        component = dict(Type="Light", LightType=kind, Color=list(color), Intensity=intensity, CastShadows=shadows)
        component.update(extra or {})
        entity(name, [transform(position, rotation), component])

    # The main camera faces the monitor wall (the studio is behind it).
    entity("Main Camera", [transform((0, 1.75, -4.6), (4, 0, 0)),
           dict(Type="Camera", IsCurrent=True, Projection="Perspective", FieldOfView=50, Near=0.05, Far=60,
                ClearType="Color", ClearColor=[0.02, 0.025, 0.035]),
           dict(Type="PostProcess", Tonemapper="ACES", Bloom=True, BloomIntensity=0.06, AmbientOcclusion=True,
                FXAA=True, VignetteIntensity=0.25)])
    light("Sun", "Directional", (0, 10, 0), (50, 35, 0), (1.0, 0.96, 0.9), 2.5, shadows=True,
          extra=dict(DirectionalSource="Manual"))

    # Monitor wall: a dark panel with four screens, their front (-Z) faces towards the main camera.
    mesh("Monitor Wall", "Cube", (0, 1.6, 0.25), (4.2, 1.9, 0.2), material((0.035, 0.035, 0.04), roughness=0.8))
    bezel = material((0.01, 0.01, 0.012), roughness=0.35)
    graph = dict(Type="ShaderGraphMaterial", Graph=CAMERA_FEED, Params={"Brightness": 1.3}, Textures={"Feed": STUDIO_FEED})
    screens = [
        # name, centre, half size, surface
        ("Studio Monitor", (-1.45, 2.15, 0), (1.55, 0.87), material((0.0, 0.0, 0.0), roughness=0.3, emissive=(STUDIO_FEED, 1.0))),
        ("Print Monitor", (1.75, 2.45, 0), (1.05, 0.59), material((1, 1, 1), roughness=0.75, diffuse=STUDIO_FEED)),
        ("Graph Monitor", (1.75, 1.05, 0), (1.05, 0.59), graph),
        ("Security Monitor", (-1.45, 0.55, 0), (1.1, 0.62), material((0.0, 0.0, 0.0), roughness=0.3, emissive=(SECURITY_FEED, 1.2))),
    ]
    for name, (x, y, z), (hw, hh), surface in screens:
        mesh(name + " Bezel", "Cube", (x, y, z + 0.02), (hw + 0.06, hh + 0.06, 0.05), bezel)
        mesh(name, "Cube", (x, y, z - 0.04), (hw, hh, 0.01), surface, shadows=False)
    # Lights the printed (diffuse) screen, which has no glow of its own.
    light("Print Light", "Spot", (1.75, 3.6, -1.6), (38, 0, 0), (1.0, 0.95, 0.85), 60,
          extra=dict(Range=6, InnerConeAngle=22, OuterConeAngle=30))

    # The studio set, behind the main camera: saturated, asymmetric props so a flipped, mirrored or
    # black feed changes many pixels.
    mesh("Studio Floor", "Plane", (0, 0, -12), (6, 1, 5), material((0.32, 0.33, 0.36), roughness=0.85), shadows=False)
    mesh("Studio Backdrop", "Cube", (0, 3, -16.8), (6, 3, 0.2), material((0.05, 0.42, 0.48), roughness=0.9))
    mesh("Magenta Sign", "Cube", (-3.6, 3.9, -16.5), (1.4, 0.45, 0.1),
         material((0.9, 0.1, 0.7), roughness=0.5, glow=((1.0, 0.15, 0.8), 3.0)), shadows=False)
    # A turntable (a pivot with a Spinner) carries most of the props round.
    entity("Turntable", [transform((0.2, 0, -13.4)),
           dict(Type="ScriptComponent", ScriptName="Spinner", ScriptFields=json.dumps({"DegreesPerSecond": 25.0, "Axis": 1}))])
    mesh("Turntable Disc", "Cylinder", (0, 0.08, 0), (3.0, 0.08, 3.0), material((0.55, 0.5, 0.42), roughness=0.6), parent="Turntable")
    mesh("Red Block", "Cube", (1.85, 0.76, -0.45), (0.65, 0.6, 0.65), material((0.85, 0.08, 0.06), roughness=0.4), parent="Turntable")
    mesh("Yellow Pillar", "Cylinder", (-0.75, 1.36, 0.9), (0.33, 1.2, 0.33), material((0.95, 0.75, 0.05), roughness=0.35), parent="Turntable")
    mesh("Green Ball", "Sphere", (-1.65, 0.9, -1.35), (0.74, 0.74, 0.74), material((0.1, 0.7, 0.2), roughness=0.25), parent="Turntable")
    mesh("Blue Slab", "Cube", (0.3, 0.48, -2.25), (1.35, 0.32, 0.24), material((0.1, 0.25, 0.9), roughness=0.45), parent="Turntable")
    # In the studio camera's own shot: black in the studio feed, the studio feed everywhere else.
    mesh("Set Monitor", "Cube", (-2.7, 1.45, -10.6), (1.2, 0.68, 0.03),
         material((0.0, 0.0, 0.0), roughness=0.3, emissive=(STUDIO_FEED, 1.0)), rotation=(0, 160, 0))
    light("Studio Key", "Spot", (-3.0, 4.5, -8.5), (40, 150, 0), (1.0, 0.9, 0.8), 300, shadows=True,
          extra=dict(Range=14, InnerConeAngle=25, OuterConeAngle=35))

    # Studio camera: films the set from the front, every frame, at the feed's full size.
    entity("Studio Camera", [transform((0, 1.6, -6.8), (6, 180, 0)),
           dict(Type="Camera", IsCurrent=False, Projection="Perspective", FieldOfView=55, Near=0.05, Far=40,
                ClearType="Color", ClearColor=[0.35, 0.45, 0.6], TargetTexture=STUDIO_FEED, UpdateInterval=1),
           dict(Type="PostProcess", Tonemapper="ACES", Bloom=True, BloomIntensity=0.05, AmbientOcclusion=True,
                FXAA=True, VignetteIntensity=0.15)])
    # Security camera: high in a corner, a low-resolution feed every other frame. Its post settings
    # ask for fog with volumetrics and ambient occlusion; the camera's pass switches keep the
    # expensive ones off (analytic fog stays).
    entity("Security Camera", [transform((4.6, 4.2, -9.0), (32, 215, 0)),
           dict(Type="Camera", IsCurrent=False, Projection="Perspective", FieldOfView=75, Near=0.05, Far=40,
                ClearType="Color", ClearColor=[0.1, 0.12, 0.1], TargetTexture=SECURITY_FEED, UpdateInterval=2,
                SunShadows=False, AmbientOcclusion=False, VolumetricFog=False),
           dict(Type="PostProcess", Tonemapper="ACES", Bloom=False, AmbientOcclusion=True, AOIntensity=2.0,
                Fog=True, FogDensity=0.06, FogHeightFalloff=0.05, VolumetricFog=True, VolumetricDistance=30,
                FXAA=False, VignetteIntensity=0.4, Saturation=0.6)])

    write_render_texture(STUDIO_FEED, {"Width": 480, "Height": 270, "Mips": True, "Wrap": "Clamp"})
    write_render_texture(SECURITY_FEED, {"Width": 128, "Height": 72, "Mips": False, "Wrap": "Clamp"})

    SCENE.write_text(json.dumps({"Version": 2, "Cores": [], "Entities": entities}, indent=4) + "\n")
    print("wrote", SCENE.relative_to(ROOT), len(entities), "entities")


if __name__ == "__main__":
    build()
