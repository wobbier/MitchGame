#!/usr/bin/env python3
"""Rebuild the Synty Office Pack split-diopter showcase. Python 3, no packages.

Run from any directory. Overwrites Assets/Scenes/Showcase/SplitDiopter.lvl.
The companion manifest records the engine's imported part paths and four posed arm
nodes per character, including the FBX pivot hierarchy. Original imports stay intact.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICE = "Assets/Models/Synty/OfficePack/"
ATLAS = OFFICE + "Textures/PolygonOffice_Texture_01_A.png"
SCREEN = OFFICE + "Textures/PolygonOffice_Texture_Sceen_01.png"
PARTS = json.loads((ROOT / "Tools/SplitDiopterOfficeParts.json").read_text())
SCENE = ROOT / "Assets/Scenes/Showcase/SplitDiopter.lvl"


def transform(position=(0, 0, 0), yaw=0, pitch=0, scale=1):
    y, p = math.radians(yaw) / 2, math.radians(pitch) / 2
    rotation = [math.cos(y) * math.sin(p), math.sin(y) * math.cos(p),
                -math.sin(y) * math.sin(p), math.cos(y) * math.cos(p)]
    return dict(Type="Transform", Position=list(position), Rotation=rotation,
                Scale=[scale] * 3 if isinstance(scale, (int, float)) else list(scale))


def material(texture=ATLAS, color=(1, 1, 1), emissive=0):
    result = dict(Type="StandardMaterial", DiffuseColor=list(color), Roughness=0.72,
                  Metallic=0, EmissiveColor=[1, 1, 1], EmissiveIntensity=emissive)
    if texture:
        result["Textures"] = {"Diffuse": dict(Path=texture, RenderMode="Opaque")}
    return result


def model(key):
    asset = PARTS[key]
    result = dict(Type="Model", ModelPath=asset["ModelPath"], Compact=True,
                  BakedImportScale=0.01, Parts={})
    for i, part in enumerate(asset["Parts"]):
        surface = material()
        if key == "SM_Prop_Computer_Monitor_01" and i == 1:
            surface = material(SCREEN, emissive=0.35)
        if key == "SM_Bld_Door_01" and "Glass" in part:
            surface = material(None, (0.12, 0.19, 0.19))
            surface.update(Opacity=0.24, RenderMode=1, FaceMode=2)
        result["Parts"][part] = dict(Type="Mesh", MeshType="Model", CastShadows=True, Material=surface)
    if "Nodes" in asset:
        result["Nodes"] = copy.deepcopy(asset["Nodes"])
    return result


def build():
    entities = []

    def entity(name, components):
        entities.append(dict(GUID=hashlib.sha256(("office-diopter/" + name).encode()).hexdigest()[:16],
                             Name=name, DestroyOnLoad=True, Components=components))

    def prop(name, key, position=(0, 0, 0), yaw=0, scale=1):
        entity(name, [transform(position, yaw=yaw, scale=scale), model(key)])

    def box(name, position, scale, color):
        entity(name, [transform(position, scale=scale),
                      dict(Type="Mesh", MeshType="Cube", CastShadows=True, Material=material(None, color))])

    def light(name, kind, position, color, intensity, radius=10, yaw=0, pitch=0, shadows=False):
        entity(name, [transform(position, yaw, pitch), dict(Type="Light", LightType=kind,
               Color=list(color), Intensity=intensity, Range=radius, CastShadows=shadows,
               ShadowDistance=22, ShadowBias=0.5, ShadowNormalBias=1.5)])

    entity("Main Camera", [transform((2.45, 1.60, -2.0), yaw=-28),
           dict(Type="Camera", IsCurrent=True, Projection="Perspective", FieldOfView=28,
                Near=0.05, Far=40, ClearType="Color", ClearColor=[0.075, 0.10, 0.14]),
           dict(Type="PostProcess", DepthOfField=True, DoFFocusDistance=1.83,
                DoFSplitDiopter=True, DoFSplitFocusDistance=8.36, DoFSplitPosition=0.47,
                DoFSplitFeather=0.018, DoFAperture=0.8, DoFSensorHeight=36,
                DoFMaxBlurRadius=28, DoFDebugCoC=False, AutoExposure=False,
                ExposureCompensation=0.2, Bloom=True, BloomIntensity=0.035,
                BloomThreshold=1.4, AmbientOcclusion=True, AORadius=0.3,
                AOIntensity=0.75, TemporalAA=False, FXAA=True, VignetteIntensity=0.16)])

    # Shoot diagonally from the corridor through a normal-width office entrance.
    # The employee is just outside the threshold, close enough for a head/shoulder
    # foreground portrait; the boss is visible beyond his right shoulder.
    # Both rigs face -Z in their original model coordinates.
    prop("Employee - doorway - left focus", "SK_Chr_Business_Male_01", (1.08, 0, -0.50), yaw=-28)
    prop("Boss - office - right focus", "SK_Chr_Boss_Male_01", (-0.80, 0, 5.90), yaw=-20)

    for key, label in (("SM_Bld_Wall_Blank_Door_01", "Doorway wall"),
                       ("SM_Bld_Wall_Trim_Door_01", "Doorway trim"),
                       ("SM_Bld_Wall_Baseboard_Door_01", "Doorway skirting")):
        prop(label, key, (0, 0, 0.3))
    # The pack's opening spans x=0.75..1.75. Keep the matching 1 m door
    # unstretched, hinged on the left jamb and swung inward into the office.
    prop("Open office door", "SM_Bld_Door_01", (0.75, 0, 0.30), yaw=-95)
    prop("Manager nameplate", "SM_Prop_Sign_Manager_01", (2.08, 1.55, 0.105))
    for x in (-5, -2.5, 2.5):
        prop(f"Corridor entrance wall {x}", "SM_Bld_Wall_Blank_01", (x, 0, 0.3))

    for x in (-2.5, 0):
        for z in (2.8, 5.3, 7.8):
            prop(f"Carpet {x} {z}", "SM_Bld_Floor_Carpet_01", (x, -0.004, z))
    for x in (-5, -2.5, 0, 2.5):
        prop(f"Corridor carpet {x}", "SM_Bld_Floor_Carpet_01", (x, -0.004, 0.3))
    for z in (0.3, 2.8, 5.3):
        prop(f"Left wall {z}", "SM_Bld_Wall_Blank_01", (-2.5, 0, z), yaw=-90)
        prop(f"Right wall {z}", "SM_Bld_Wall_Blank_01", (2.5, 0, z + 2.5), yaw=90)
    for x in (-2.5, 0):
        prop(f"Back wall {x}", "SM_Bld_Wall_Blank_01", (x, 0, 7.8))
    box("Ceiling", (0, 3.05, 4), (2.5, 0.05, 4), (0.48, 0.49, 0.46))
    box("Corridor ceiling", (0, 3.05, -0.95), (5, 0.05, 1.25), (0.48, 0.49, 0.46))

    # A dressed executive office gives depth cues and small details to compare.
    prop("Executive desk", "SM_Prop_Desk_01", (-0.90, 0, 4.95), yaw=180)
    prop("Boss chair", "SM_Prop_Chair_05", (-0.80, 0, 6.65), yaw=180)
    prop("Desk monitor", "SM_Prop_Computer_Monitor_01", (-1.43, 0.75, 5.06), yaw=180)
    prop("Desk keyboard", "SM_Prop_Computer_Keyboard_01", (-1.37, 0.75, 5.32), yaw=180)
    prop("Desk telephone", "SM_Prop_Phone_Desk_01", (-0.22, 0.75, 4.95), yaw=180)
    prop("Desk coffee", "SM_Prop_Cup_01", (-0.71, 0.75, 4.72))
    prop("Desk photograph", "SM_Prop_Photo_01", (-0.25, 0.75, 5.25), yaw=180)
    prop("Desk task lamp", "SM_Prop_DeskLamp_05", (-1.75, 0.75, 5.0), yaw=20)
    prop("Bookshelf", "SM_Prop_Shelf_01", (-1.30, 0, 7.38))
    prop("Shelf books", "SM_Prop_Book_Group_02", (-1.30, 1.12, 7.34))
    prop("Office plant", "SM_Prop_Plant_01", (2.0, 0, 7.05), scale=1.6)
    prop("Hall plant", "SM_Prop_Plant_01", (3.6, 0, -0.25), scale=1.25)
    # A window surround and slats on the back wall expose background defocus on
    # the employee's side while leaving the boss's side crisp.
    box("Window recess", (-1.25, 1.75, 7.61), (0.66, 0.70, 0.035), (0.16, 0.27, 0.36))
    prop("Window blinds", "SM_Bld_Wall_Window_Blinds_Open_01", (-2.5, 0, 7.62))

    light("Window daylight", "Directional", (0, 4, 2), (0.78, 0.86, 1), 2.3, yaw=-30, pitch=38, shadows=True)
    light("Hall portrait key", "Point", (2.05, 2.15, -1.8), (1, 0.83, 0.66), 10, 4.5)
    light("Office ceiling fill", "Point", (0.3, 2.65, 4.4), (1, 0.90, 0.74), 22, 7)
    light("Boss face key", "Point", (-0.3, 2.2, 4.4), (1, 0.84, 0.65), 10, 3.5)
    light("Window cool fill", "Point", (-1.25, 2.0, 7.1), (0.50, 0.72, 1), 9, 4)

    references = sorted({m["ModelPath"] for m in PARTS.values()} | {ATLAS, SCREEN})
    for path in references:
        if not (ROOT / path).is_file():
            raise FileNotFoundError(path)
    # The supplied pack's PNG sidecars use Unity YAML. The engine expects JSON;
    # convert only these two textures and preserve the source metadata in .tmp.
    for texture in (ATLAS, SCREEN):
        sidecar = ROOT / (texture + ".meta")
        if sidecar.exists():
            try:
                json.loads(sidecar.read_text())
                continue
            except json.JSONDecodeError:
                backup = ROOT / ".tmp/SplitDiopterImport" / (sidecar.name + ".unity")
                backup.parent.mkdir(parents=True, exist_ok=True)
                if not backup.exists():
                    backup.write_bytes(sidecar.read_bytes())
        sidecar.write_text(json.dumps(dict(FileType="png", Format="None",
                           GUID=hashlib.sha256(texture.encode()).hexdigest()[:16],
                           MIPs=True, Quality="h", Type="Default"), indent=4) + "\n")
    SCENE.write_text(json.dumps(dict(Version=2, Cores=[], Entities=entities), indent=4) + "\n")
    print(f"Wrote {SCENE.relative_to(ROOT)} ({len(entities)} entities)")


if __name__ == "__main__":
    build()
