#!/usr/bin/env python3
"""Build Chamber 07: relay routing, a weighted cube switch, and a momentum fling.

All dimensions below are metres/full sizes. Engine primitive cubes span [-1, 1].
Run from anywhere; writes Assets/Scenes/Portals.lvl atomically so the editor can reload each pass.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / 'Assets/Scenes/Portals.lvl'
BASELINE = ROOT / 'Assets/Scenes/Tests/PortalPhysics.lvl'
DARK = [0.045, 0.06, 0.075]
METAL = [0.11, 0.14, 0.17]
WHITE = [0.76, 0.79, 0.77]
PANEL = [0.92, 0.94, 0.90]
CYAN = [0.025, 0.65, 0.9]
AMBER = [1.0, 0.36, 0.045]
RED = [0.85, 0.075, 0.04]
entities = []


def guid(name):
    return hashlib.sha256(('chamber07/' + name).encode()).hexdigest()[:16]


def entity(name, position=(0, 0, 0), dimensions=None, rotation=(0, 0, 0), components=(), parent=None):
    result = {'GUID': guid(name), 'Name': name, 'DestroyOnLoad': True,
              'Components': [{'Type': 'Transform', 'Position': list(position), 'Rotation': list(rotation),
                              'Scale': [v * 0.5 for v in dimensions] if dimensions else [1, 1, 1]},
                             *copy.deepcopy(list(components))]}
    if parent: result['Parent'] = parent
    entities.append(result)
    return result


def box(name, position, size, color=DARK, solid=False, glow=0, rotation=(0, 0, 0), parent=None, body=None):
    result = entity(name, position, size, rotation, [{'Type': 'Mesh', 'MeshType': 'Cube', 'CastShadows': glow == 0,
        'Material': {'Type': 'StandardMaterial', 'DiffuseColor': color, 'Roughness': 0.65,
                     'Metallic': 0.1, 'EmissiveColor': color, 'EmissiveIntensity': glow}}], parent)
    # Closed interiors need deliberate diffuse fill: mild material lift preserves readable dark
    # structure while the high-output neutral fixtures provide the actual surface lighting.
    material = result['Components'][1]['Material']
    if glow == 0:
        if sum(color)/3 > .7: material['EmissiveIntensity'] = .12
        elif sum(color)/3 > .2: material['EmissiveIntensity'] = .085
        else:
            material['EmissiveColor'] = [.18,.20,.22]
            material['EmissiveIntensity'] = .045
    if solid: result['Components'].append({'Type': 'BoxCollider', 'Size': [2, 2, 2], 'Friction': 0.6})
    if body: result['Components'].append({'Type': 'Rigidbody', 'BodyType': body, 'Mass': 5 if body == 'Dynamic' else 0,
                                         'ContinuousCollision': True})
    return result


def text(name, value, position, size=0.35, color=WHITE, rotation=(0, 0, 0), parent=None):
    return entity(name, position, rotation=rotation, parent=parent, components=[{'Type': 'TextRenderer',
        'Text': value, 'Font': 'Assets/Fonts/Inter-Regular.ttf', 'Size': size, 'Color': color,
        'Alignment': 'Center', 'Anchor': 'Middle', 'Lit': False}])


def light(name, position, color, power=4, reach=10):
    return entity(name, position, components=[{'Type': 'Light', 'LightType': 'Point', 'Color': color,
        'Intensity': power, 'Range': reach, 'CastShadows': False}])


def save():
    SCENE.parent.mkdir(parents=True, exist_ok=True)
    tmp = SCENE.with_suffix('.lvl.tmp')
    tmp.write_text(json.dumps({'Version': 2, 'Cores': [], 'Entities': entities}, indent=4) + '\n')
    tmp.replace(SCENE)
    print(f'Saved {SCENE.relative_to(ROOT)}: {len(entities)} entities', flush=True)


def preserve_players():
    baseline = json.loads((BASELINE if BASELINE.exists() else SCENE).read_text())
    old = {e['Name']: e for e in baseline['Entities']}
    for name in ('Player', 'Player Camera', 'Portal HUD'):
        e = copy.deepcopy(old[name])
        entities.append(e)
        if name == 'Player':
            t = next(c for c in e['Components'] if c['Type'] == 'Transform')
            t.update(Position=[0, 0.95, -11], Rotation=[0, 0, 0])
        if name == 'Player Camera':
            camera = next(c for c in e['Components'] if c['Type'] == 'Camera')
            camera.update(ClearType='Color', ClearColor=[0.022, 0.031, 0.045], Far=120, Zoom=66)
            post = next(c for c in e['Components'] if c['Type'] == 'PostProcess')
            post.update(ExposureCompensation=0.35, BloomIntensity=0.045, BloomThreshold=1.3,
                        VignetteIntensity=0.13, AmbientOcclusion=True)
    for i, color in enumerate(('Blue', 'Orange')):
        name = color + ' Portal'
        root = copy.deepcopy(old[name])
        next(c for c in root['Components'] if c['Type'] == 'Transform').update(Position=[i * 4, -40, 0], Rotation=[0, 0, 0])
        script = next(c for c in root['Components'] if c['Type'] == 'ScriptComponent')
        fields = json.loads(script['ScriptFields'])
        fields.update(RequirePlacement=True, IsPlaced=False)
        script['ScriptFields'] = json.dumps(fields)
        entities.append(root)
        surface = copy.deepcopy(old[name + ' Surface'])
        entities.append(surface)
        tint = CYAN if i == 0 else AMBER
        for label, pos, dim in [('Top', [0,1.22,.02],[1.64,.035,.045]),
                               ('Bottom',[0,-1.22,.02],[1.64,.035,.045]),
                               ('Left',[-.82,0,.02],[.035,2.4,.045]),
                               ('Right',[.82,0,.02],[.035,2.4,.045])]:
            box(name + ' Frame ' + label, pos, dim, tint, glow=3, parent=root['GUID'])


def architecture():
    # The first power pit spans the chamber. Only the bridge or a portal route can cross it.
    box('Start Platform', [0,-.4,-8], [24,.8,12], DARK, True)
    box('Lab Platform', [0,-.4,12], [24,.8,12], DARK, True)
    box('Fling Entry Floor', [0,-.4,20.5], [24,.8,5], DARK, True)
    box('Shaft Left Floor', [-7.5,-.4,27.5], [9,.8,9], DARK, True)
    box('Shaft Right Floor', [7.5,-.4,27.5], [9,.8,9], DARK, True)
    box('Shaft Rear Floor', [0,-.4,32.5], [6,.8,7], DARK, True)
    box('Power Pit Floor', [0,-6.4,2], [24,.8,8], METAL, True)
    box('Drop Shaft Left Wall', [-3.2,-4.7,26], [.4,9.4,6], DARK, True)
    box('Drop Shaft Right Wall', [3.2,-4.7,26], [.4,9.4,6], DARK, True)
    box('Drop Shaft Rear Wall', [0,-4.7,29.2], [6.4,9.4,.4], DARK, True)
    box('Drop Shaft Front Wall', [0,-4.7,22.8], [6.4,9.4,.4], DARK, True)
    box('Chamber West Wall', [-12.25,5.75,11], [.5,12.5,50], DARK, True)
    box('Chamber East Wall', [12.25,5.75,11], [.5,12.5,50], DARK, True)
    box('Chamber South Wall', [0,5.75,-14.25], [24,12.5,.5], DARK, True)
    box('Chamber North Wall', [0,5.75,36.25], [24,12.5,.5], DARK, True)
    box('Chamber Ceiling', [0,12.25,11], [24,.5,50], DARK, True)
    # Portalable faces sit proud of any support wall; the same host must contain the aperture.
    box('Portal Panel Entry', [-3,2.2,-3], [3.2,4.4,.4], PANEL, True)
    box('Entry Panel Base', [-3,.1,-3], [3.65,.2,.85], METAL, True)
    box('Relay Cell Floor', [-8,-.25,3], [6,.5,8], METAL, True)
    box('Relay Cell Left Wall', [-11.1,2.5,3], [.2,5,8], DARK, True)
    box('Relay Cell Right Wall', [-4.9,2.5,3], [.2,5,8], DARK, True)
    box('Relay Cell Ceiling', [-8,5.05,3], [6.4,.2,8.4], DARK, True)
    box('Portal Panel Relay', [-8,2.2,7], [5.6,4.4,.35], PANEL, True)
    box('Relay Cell Rear Border', [-8,4.65,7], [6.4,.5,.5], METAL, True)
    # A portal beam can pass this grille, but physical balls and the player cannot.
    # Cyan transparent-looking bars are spaced around a subtle full solid collider.
    window = entity('Portal Window Relay Barrier', [-8,2.5,-1], [6,5,.09], components=[
        {'Type':'BoxCollider','Size':[2,2,2]}])
    glass = box('Relay Window Glass', [-8,2.5,-1.02], [5.85,4.8,.02], [.12,.32,.39])
    glass['Components'][1]['CastShadows'] = False
    glass['Components'][1]['Material'].update(Opacity=.12, RenderMode=1, Roughness=.1, Metallic=.0)
    for x in (-10.9,-9.45,-8,-6.55,-5.1):
        box('Relay Window Mullion ' + str(x), [x,2.5,-1.04], [.065,5.1,.1], METAL)
    for y in (.2,2.5,4.8): box('Relay Window Rail ' + str(y), [-8,y,-1.04], [6,.045,.1], CYAN, glow=.6)
    box('Bridge', [0,-3,2], [3.4,.3,8.1], METAL, True, body='Kinematic')
    entity('Checkpoint 1', [0,.9,8])
    box('Cube Gallery', [7.5,1.5,13], [5,3,6], METAL, True)
    box('Portal Panel Gallery', [7.5,5.2,16], [4.8,4.4,.35], PANEL, True)
    box('Portal Panel Lab', [-7.5,2.2,12.5], [.35,4.4,4.8], PANEL, True)
    box('Pressure Plate', [0,.1,13], [2.2,.2,2.2], [0.33,.16,.055], True)
    cube = box('Companion Cube', [7.5,3.55,12.5], [.85,.85,.85], WHITE, True, body='Dynamic')
    # Parent-local dimensions account for the cube's .425 world scale.
    for axis in range(3):
        dim = [1.55,1.55,1.55]; dim[axis]=2.05
        box('Cube Accent ' + str(axis), [0,0,0], dim, METAL, parent=cube['GUID'])
    box('Cube Core', [0,0,-1.035], [.78,.78,.04], CYAN, glow=1.5, parent=cube['GUID'])
    for side in (-1,1):
        box('Gate Wall ' + str(side), [side*6.95,2.3,18], [10.1,4.6,.5], METAL, True)
    box('Gate Lintel', [0,4.8,18], [24,.45,.6], METAL, True)
    box('Gate Left', [-.95,2.25,18], [1.9,4.5,.35], DARK, True, body='Kinematic')
    box('Gate Right', [.95,2.25,18], [1.9,4.5,.35], DARK, True, body='Kinematic')
    hatch = entity('Portal Window Drop Hatch', [0,-.15,26], [3,.3,6], components=[
        {'Type':'BoxCollider','Size':[2,2,2]},
        {'Type':'Rigidbody','BodyType':'Kinematic','Mass':0,'ContinuousCollision':True}])
    for i,x in enumerate((-1.4,-1.12,-.84,-.56,-.28,.28,.56,.84,1.12,1.4)):
        box('Drop Hatch Grate '+str(i), [x/1.5,1.13,0], [.065/1.5,.08/.15,5.85/3], METAL,
            parent=hatch['GUID'])
    for side in (-1,1):
        box('Drop Hatch End Frame '+str(side), [0,1.05,side*.975], [2,.10/.15,.12/3], WHITE,
            parent=hatch['GUID'])
        box('Drop Hatch Side Frame '+str(side), [side*.98,1.05,0], [.10/1.5,.10/.15,2], WHITE,
            parent=hatch['GUID'])
    box('Portal Panel Drop', [0,-9.2,26], [5.6,.4,5.6], PANEL, True)
    box('Portal Panel Fling', [0,3.3,31], [4.8,5,.4], PANEL, True, rotation=(-35,180,0))
    box('Fling Panel Support', [0,2.2,33.5], [5.5,4.4,1.0], DARK, True)
    box('Exit Ledge', [0,5,17.625], [5.5,.4,7.25], METAL, True)
    box('Exit Vestibule Back', [0,7.6,13.7], [5.5,4.8,.4], DARK, True)
    for side in (-1,1):
        box('Exit Vestibule Side '+str(side), [side*2.95,5.85,17.625], [.4,1.3,7.25], METAL, True)
    box('Exit Back Left', [-3.2,7,17.5], [2.8,4,.4], DARK, True)
    box('Exit Back Right', [3.2,7,17.5], [2.8,4,.4], DARK, True)
    box('Exit Door', [0,7,17.65], [3.2,3.6,.25], [0.12,.19,.19], True, body='Kinematic')
    box('Exit Door Header', [0,9,17.65], [6,.45,.5], METAL, True)
    entity('Exit Goal', [0,6.1,15.5])
    entity('Chamber Controller', components=[{'Type':'ScriptComponent','ScriptName':'ChamberController','ScriptFields':'{}'}])
    entity('Chamber HUD', components=[{'Type':'UIDocument','FilePath':'Assets/UI/Portals/Chamber.rml','Visible':True,'SortOrder':11}])


def lighting():
    entity('Chamber Fill', rotation=(55,-25,0), components=[{'Type':'Light','LightType':'Directional',
        'Color':[.95,.97,1.0], 'Intensity':2.4, 'CastShadows':False,'ShadowDistance':65}])
    for i,z in enumerate((-10,-1,9,20,31)):
        light('Ceiling Area ' + str(i), [0,8.0,z], [.95,.97,1], 160, 18)
        box('Ceiling Fixture ' + str(i), [0,11.8,z], [8,.15,.65], WHITE, glow=2.1)
    light('Relay Cell Light', [-8,4.2,3], [.78,.92,1], 90, 10)
    light('Gallery Light', [8,7.5,13], [1,.92,.78], 130, 13)
    light('Drop Shaft Light', [0,-4,26], [1,.65,.28], 65, 12)
    box('Relay Lamp', [-5.15,3.6,-1.12], [.18,.7,.1], AMBER, glow=1.8)
    box('Plate Lamp', [1.32,.22,13], [.12,.22,1.8], AMBER, glow=1.5)
    box('Exit Lamp', [0,9.05,17.35], [2.2,.12,.12], AMBER, glow=1.5)
    # Receiver collider-free socket: a glowing target catches balls along -Z from the back panel.
    entity('Relay Receiver', [-8,1.3,3.8])
    box('Relay Socket Body', [-8,.10,3.5], [3.6,.20,.45], METAL)
    box('Relay Socket Core', [-8,2.42,3.72], [3.3,.10,.12], CYAN, glow=1.4)
    box('Relay Status Face', [-8,.23,3.29], [3.3,.11,.06], CYAN, glow=.5)
    text('Relay Status Label', 'RECEIVER / ROUTE AN ENERGY BALL', [-8,2.79,3.26], .22, CYAN)
    for x in (-9.65,-6.35): box('Relay Socket Clamp ' + str(x), [x,1.3,3.82], [.15,2.2,.15], WHITE)


def details():
    # A restrained, repeated panel system replaces the old outdoor prototype's loose primitives.
    for row,z in enumerate((-12,-9,-6,-3,7.5,10.5,13.5,16.5,19.5,22)):
        for col,x in enumerate((-10.5,-7.5,-4.5,-1.5,1.5,4.5,7.5,10.5)):
            if z > 10 and x > 5: continue  # gallery solid already occupies this footprint
            if z > 17 and abs(x) < 3: continue  # avoid moving gate and raised exit geometry
            shade = [.54,.58,.59] if (row+col)%3 else [.61,.64,.63]
            box(f'Floor Tile {row:02d}-{col:02d}', [x,.012,z], [2.94,.024,2.92], shade)
    for side in (-1,1):
        for i,z in enumerate((-11,-6,-1,4,9,14,19,24,29,34)):
            # Wall relief stays separate from portalable white panels and never adds colliders.
            box(f'Wall Inset {side}-{i}', [side*11.975,4.4,z], [.035,6.8,4.86], [.76,.79,.78])
            box(f'Wall Lower Panel {side}-{i}', [side*11.94,1,z], [.05,1.8,4.82], [.43,.48,.49])
            box(f'Wall Upright {side}-{i}', [side*11.88,5.5,z+2.45], [.16,11,.13], METAL)
        box('Wall Cyan Service Strip '+str(side), [side*11.85,3.1,10.5], [.065,.055,48.6], CYAN, glow=1.25)
        box('Wall Amber Service Strip '+str(side), [side*11.85,.55,10.5], [.065,.04,48.6], AMBER, glow=.5)
    # Continuous inlaid edge bands read as boundaries, not loose orange objects/debris.
    for z in (-2.12,6.12):
        for side in (-1,1):
            box('Pit Edge Band '+str(z)+'-'+str(side), [side*6.95,.006,z], [10.1,.009,.065], AMBER)
            box('Pit Lip '+str(z)+'-'+str(side), [side*6.95,-.06,z], [10.1,.12,.18], METAL)
    for side in (-1,1):
        box('Bridge Guide Rail '+str(side), [side*.965,1.4,0], [.07/1.7,.25/.15,7.9/4.05], CYAN, glow=1.3, parent=guid('Bridge'))
        # No side catwalk can bypass the bridge; the rail ends remain in each safe landing.
        box('Start Safety Rail '+str(side), [side*5.3,.75,-2.35], [5.8,.085,.085], [.37,.43,.45])
        for x in (side*2.4,side*8.2): box('Start Rail Post '+str(x), [x,.38,-2.35], [.07,.76,.07], METAL)
    for i in range(9):
        box('Bridge Deck Slat '+str(i), [0,1.08,-.88+i*.22], [2.9/1.7,.035/.15,.045/4.05], [.31,.37,.4], parent=guid('Bridge'))
    # Cable paths form visual cause-and-effect links between relay, bridge, plate and gate.
    box('Relay Inlaid Conduit', [-3.2,.008,-2.65], [3,.01,.035], CYAN, glow=.25)
    box('Plate Inlaid Conduit', [1.55,.008,15.1], [.035,.01,3.6], CYAN, glow=.25)
    # Joined, flush white arrows use built-in primitives; there are no loose marker blocks.
    for i,z in enumerate((21.1,22.25)):
        box('Fling Floor Arrow Shaft '+str(i), [0,.025,z-.12], [.055,.008,.65], WHITE)
        box('Fling Floor Arrow Left '+str(i), [-.10,.025,z+.19], [.055,.008,.30], WHITE, rotation=(0,45,0))
        box('Fling Floor Arrow Right '+str(i), [.10,.025,z+.19], [.055,.008,.30], WHITE, rotation=(0,-45,0))
    for side in (-1,1):
        box('Drop Hazard Side '+str(side), [side*3.08,.006,26], [.065,.009,5.9], AMBER, glow=.6)
        box('Drop Shaft Ruler '+str(side), [side*2.97,-4.2,26], [.03,7.6,.08], CYAN, glow=1)
        for j in range(8):
            box(f'Drop Depth Tick {side}-{j}', [side*2.96,-.75-j,25.75], [.04,.045,.45], WHITE, glow=.4)
    # Cage rails let the cube remain readable from below without obstructing portal placement.
    for x in (5.1,9.9):
        box('Gallery Edge Rail '+str(x), [x,3.65,11.7], [.055,1.3,3.4], METAL)
    for i,z in enumerate((10.15,11.6,13.05,14.5)):
        box('Gallery Rail Top '+str(i), [10,4.25,z], [.07,.07,1.4], WHITE)
    # Frames identify the intended shooting panels; decoration sits outside the usable faces.
    for name,center,width,height in [('Entry',[-3,2.2,-3.25],3.2,4.4),
                                      ('Relay',[-8,2.2,6.79],5.6,4.4),
                                      ('Gallery',[7.5,5.2,15.79],4.8,4.4)]:
        for side in (-1,1):
            box(name+' Panel Edge '+str(side), [center[0]+side*(width*.5+.035),center[1],center[2]],
                [.07,height+.16,.09], METAL)
        box(name+' Panel Header', [center[0],center[1]+height*.5+.04,center[2]], [width+.14,.08,.1], METAL)
    # Signage: clear stage numbers, concise instructions, and exactly the controls in use.
    box('Arrival Sign Backer', [4.4,3,-3.1], [6.5,3,.15], DARK)
    text('Chamber Title','CHAMBER 07', [4.4,3.75,-3.21], .6, WHITE)
    text('Chamber Subtitle','TRANSFER / WEIGHT / MOMENTUM', [4.4,3.06,-3.21], .19, CYAN)
    text('Chamber Controls','LMB + RMB  PORTALS\nE  LAUNCH BALL    F  CARRY CUBE\nR  RETURN TO CHECKPOINT', [4.4,2.31,-3.21], .23, [.55,.67,.72])
    text('Entry Panel Label','01', [-3,5,-3.26], .85, CYAN)
    text('Entry Panel Prompt','1 / LEFT CLICK: BLUE PORTAL', [-3,4.65,-3.26], .18, WHITE)
    box('Relay Label Backer', [-8,5.65,-1.12], [6.2,1,.12], DARK)
    text('Relay Label','01 / POWER RELAY', [-8,5.85,-1.21], .43, CYAN)
    text('Relay Window Instructions','RIGHT CLICK WHITE WALL THROUGH GLASS', [-8,5.4,-1.21], .16, [.65,.75,.8])
    text('Energy Ball Instructions', '3 / AIM INSIDE BLUE + E TO FIRE AN ENERGY BALL', [0,3.7,-3.3], .22, CYAN)
    text('Relay Receiver Label','2 / RIGHT CLICK: ORANGE PORTAL', [-8,4.45,6.77], .25, METAL)
    text('Bridge Notice','POWER REQUIRED', [0,1.3,6.2], .34, AMBER)
    text('Lab Title','02 / WEIGHTED ACCESS', [0,4.45,17.61], .48, WHITE)
    text('Plate Prompt','CUBE ON SWITCH = OPEN GATE', [0,3.91,17.61], .19, CYAN)
    text('Gallery Number','02', [7.5,8.05,15.74], .8, AMBER)
    text('Gallery Prompt','RETRIEVE THE CUBE', [7.5,7.43,15.74], .25, WHITE)
    text('Cube Pickup Hint','F / CARRY', [7.5,4.55,12.5], .22, CYAN)
    text('Drop Label','03 / MOMENTUM', [-5,3.6,29.9], .52, WHITE)
    text('Drop Steps','1  PORTAL ON THE SHAFT FLOOR\n2  LINK THE ANGLED PANEL\n3  DROP IN / KEEP YOUR SPEED', [-5,2.55,29.9], .24, AMBER)
    box('Drop Hatch Instructions Backer', [3.4,1.5,27.2], [2.5,1.8,.12], DARK, rotation=(0,25,0))
    text('Drop Hatch Instructions','PLACE BOTH PORTALS\nF / RELEASE DROP HATCH', [3.34,1.5,27.08], .23, CYAN, rotation=(0,25,0))
    text('Fling Panel Label','EXIT VECTOR', [0,6.15,32.45], .4, CYAN)
    text('Exit Sign','EXIT', [0,9.47,17.98], .6, CYAN, rotation=(0,180,0))
    text('Exit Vestibule Title','TEST COMPLETE', [0,8.6,13.965], .52, CYAN, rotation=(0,180,0))
    text('Exit Vestibule Subtitle','CHAMBER 07 / TRANSFER VERIFIED', [0,7.94,13.965], .19, WHITE, rotation=(0,180,0))
    light('Exit Vestibule Light', [0,8.8,15.4], [.82,1,.94], 95, 10)
    text('Exit Ledge Mark','LANDING ZONE', [0,5.225,19.5], .27, CYAN, rotation=(90,180,0))
    text('Floor Start Mark','07', [6,.035,-9], 1.3, [.28,.35,.38], rotation=(90,0,0))
    # Ceiling beams, ventilation strips, cable trays and a view-only observation recess.
    for i,z in enumerate((-12,-5,7,16,25,34)):
        box('Ceiling Crossbeam '+str(i), [0,11.55,z], [24,.42,.38], METAL)
    for side in (-1,1):
        box('Ceiling Cable Tray '+str(side), [side*8,11.58,11], [.6,.22,49], METAL)
        for i in range(5):
            box(f'Vent {side}-{i}', [side*11.88,8.8,-8+i*9], [.08,1.3,2.4], DARK)
            for j in range(4):
                box(f'Vent Slat {side}-{i}-{j}', [side*11.81,8.4+j*.26,-8+i*9], [.08,.055,2.2], [.31,.36,.38])
    box('Observation Window Frame', [11.78,6.8,10.3], [.22,3.5,7.8], DARK)
    box('Observation Window Glass', [11.65,6.8,10.3], [.025,3.1,7.4], [.018,.075,.1], glow=.7)
    for z in (7.85,10.3,12.75): box('Observation Window Mullion '+str(z), [11.6,6.8,z], [.04,3.1,.055], METAL)
    # Landing safety strips improve depth judgement from the launch panel.
    for side in (-1,1): box('Exit Landing Strip '+str(side), [side*2.66,5.215,17.625], [.08,.025,7.1], CYAN, glow=1.1)


def main():
    preserve_players()
    architecture()
    lighting()
    save()  # Checkpoint 1: complete, valid blockout before the detail pass.
    details()
    save()  # Checkpoint 2: authored surfaces, puzzle wayfinding and industrial detail.


if __name__ == '__main__': main()
