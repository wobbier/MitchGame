#!/usr/bin/env python3
"""Rebuild the authored Last Tape scene, graphs and original pixel artwork.

Run from any directory with Python 3 (no third-party packages). Export the graphs
with LastTape1999.edscript afterwards; generated .sg sources belong in git too.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
GRAPH = "Assets/ShaderGraphs/LastTape/"
ART = "Assets/Textures/LastTape/"
TOWN = "Assets/Models/Synty/Town/FBX/"


def save(path, data):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4) + "\n")


def guid(name):
    return hashlib.sha256(("last-tape-1999/" + name).encode()).hexdigest()[:16]


def png(path, width, height, pixels):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\0" + bytes(pixels[y * width * 4:(y + 1) * width * 4]) for y in range(height))
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
                      + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))
    save(path + ".meta", dict(FileType="png", Format="None", GUID=guid(path), MIPs=False, Quality="h", Type="Default"))


# Original 5x7 lettering. Also used by the world signs, so the typography belongs
# to the same home-video world as the camera's on-screen display.
FONT = {
    "A": [14,17,17,31,17,17,17], "B": [30,17,17,30,17,17,30],
    "C": [14,17,16,16,16,17,14], "D": [30,17,17,17,17,17,30],
    "E": [31,16,16,30,16,16,31], "F": [31,16,16,30,16,16,16],
    "G": [14,17,16,23,17,17,15], "H": [17,17,17,31,17,17,17],
    "I": [31,4,4,4,4,4,31], "J": [7,2,2,2,18,18,12],
    "K": [17,18,20,24,20,18,17], "L": [16,16,16,16,16,16,31],
    "M": [17,27,21,21,17,17,17], "N": [17,25,25,21,19,19,17],
    "O": [14,17,17,17,17,17,14], "P": [30,17,17,30,16,16,16],
    "Q": [14,17,17,17,21,18,13], "R": [30,17,17,30,20,18,17],
    "S": [15,16,16,14,1,1,30], "T": [31,4,4,4,4,4,4],
    "U": [17,17,17,17,17,17,14], "V": [17,17,17,17,17,10,4],
    "W": [17,17,17,21,21,21,10], "X": [17,17,10,4,10,17,17],
    "Y": [17,17,10,4,4,4,4], "Z": [31,1,2,4,8,16,31],
    "0": [14,17,19,21,25,17,14], "1": [4,12,4,4,4,4,14],
    "2": [14,17,1,2,4,8,31], "3": [30,1,1,14,1,1,30],
    "4": [2,6,10,18,31,2,2], "5": [31,16,16,30,1,1,30],
    "6": [14,16,16,30,17,17,14], "7": [31,1,2,4,8,8,8],
    "8": [14,17,17,14,17,17,14], "9": [14,17,17,15,1,1,14],
    ":": [0,4,4,0,4,4,0], ".": [0,0,0,0,0,4,4],
    "/": [1,1,2,4,8,16,16], "-": [0,0,0,31,0,0,0],
    ">": [16,8,4,2,4,8,16], "!": [4,4,4,4,4,0,4],
    "'": [4,4,8,0,0,0,0], " ": [0]*7,
}


def pixel_text(pixels, width, x, y, text, color, scale=1):
    for index, ch in enumerate(text):
        for row, bits in enumerate(FONT.get(ch, FONT[" "])):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for sy in range(scale):
                        for sx in range(scale):
                            at = ((y + row*scale + sy)*width + x + index*6*scale + col*scale + sx)*4
                            pixels[at:at+4] = color


def artwork():
    pixels = [0,0,0,255] * (96*64)
    for ch in FONT:
        pixel_text(pixels, 96, ord(ch) % 16 * 6, ord(ch) // 16 * 8, ch, [255]*4)
    png(ART + "CameraFont.png", 96, 64, pixels)
    for name, lines, fg, bg in [
        ("LAN99", [("LAN PARTY",4,22,3),("SUMMER '99",20,64,2),("BRING YOUR OWN CRT",26,96,1)], [110,255,221,255], [8,20,29,255]),
        ("DeadEnd", [("DEAD END",16,17,2),("MAPLE COURT",22,45,1)], [244,224,177,255], [25,55,51,255]),
        ("TapeLabel", [("LAST TAPE",13,12,2),("JULY 1999",22,34,1)], [255,216,159,255], [35,27,34,255]),
    ]:
        w,h = (192,128) if name == "LAN99" else (128,64)
        pixels = bg * (w*h)
        for y in (3,h-4):
            for x in range(3,w-3):pixels[(y*w+x)*4:(y*w+x)*4+4] = fg
        for x in (3,w-4):
            for y in range(3,h-3):pixels[(y*w+x)*4:(y*w+x)*4+4] = fg
        for text,x,y,scale in lines:pixel_text(pixels,w,x,y,text,fg,scale)
        png(ART + name + ".png", w, h, pixels)


class Graph:
    def __init__(self, name, target, **settings):
        self.name = name
        self.data = dict(Version=1, Settings=dict(Target=target, **settings), Properties=[], Nodes=[], Links=[])
        self.out = self.node("Output", (1800,0))

    def node(self, kind, pos=(0,0), settings=None, defaults=None):
        n = dict(Id=len(self.data["Nodes"])+1, Type=kind, Position=list(pos))
        if settings:n["Settings"] = settings
        if defaults:n["Defaults"] = defaults
        self.data["Nodes"].append(n)
        return n["Id"]

    def link(self, source, pin, target, input):
        self.data["Links"].append([source,pin,target,input])

    def prop(self, name, value, pos, limits=(0,1), kind="Float"):
        key = "p" + str(len(self.data["Properties"])+1)
        p = dict(Id=key, Name=name, Type=kind, Exposed=True)
        if isinstance(value, str):p.update(Texture=value, DefaultTexture="black")
        else:p.update(Default=[value]*4 if isinstance(value,(int,float)) else value, Range=list(limits))
        self.data["Properties"].append(p)
        return self.node("Property", pos, dict(Property=key))

    def function(self, name, inputs, outputs, code, pos):
        return self.node("CustomFunction", pos, dict(Name=name, Inputs=[dict(Name=n,Type=t) for n,t in inputs],
                         Outputs=[dict(Name=n,Type=t) for n,t in outputs], Code=code.strip()))

    def save(self):
        save(GRAPH + self.name + ".shadergraph", self.data)


def graphs():
    g = Graph("Camcorder1999", "PostProcess", Injection="AfterTonemap")
    uv = g.node("UV",(-1600,-200))
    time = g.node("Time",(-1600,50))
    strength = g.prop("Tape Wear", .72, (-1600,300))
    grain = g.prop("Sensor Grain", .028, (-400,600), (0,.12))
    bleed = g.prop("Chroma Bleed", 1.35, (-1600,500), (0,4))
    frame = g.prop("4:3 Frame", 1, (650,700))
    osd = g.prop("Camera OSD", 1, (650,900))
    vignette = g.prop("Lens Vignette", .32, (-400,800))
    coords = g.function("TapeTransport", [("UV","Vec2"),("Clock","Float"),("Wear","Float"),("Bleed","Float")],
        [("Center","Vec2"),("Red","Vec2"),("Blue","Vec2"),("Soft","Vec2")], r'''
// 480-line capture, mild lens bow and horizontal transport instability.
float frame = floor(Clock * 29.97);
float row = floor(UV.y * 480.0);
float rowNoise = fract(sin(row * 12.9898 + frame * 4.1414) * 43758.5453) - 0.5;
float tracking = smoothstep(0.972, 0.998, UV.y);
float splice = step(0.987, fract(Clock * 0.071));
vec2 p = UV - vec2_splat(0.5);
vec2 warped = UV + p * dot(p,p) * 0.032 * Wear;
warped.x += Wear * (rowNoise * 0.00065 + sin(Clock*1.7) * 0.00018
             + tracking * rowNoise * 0.006 + splice * sin(row*.14) * 0.002);
float aspect = u_viewRect.z / max(u_viewRect.w, 1.0);
vec2 raster = vec2(480.0 * aspect, 480.0);
vec2 lowRes = (floor(warped * raster) + vec2_splat(0.5)) / raster;
Center = mix(UV, lowRes, Wear * 0.78);
Red = Center + vec2(Bleed * Wear / raster.x, 0.0);
Blue = Center - vec2(Bleed * Wear * 0.65 / raster.x, 0.0);
Soft = Center + vec2(3.5 * Wear / raster.x, 0.0);
''', (-1250,-200))
    for a,p in [(uv,"UV"),(time,"Clock"),(strength,"Wear"),(bleed,"Bleed")]:
        g.link(a,"Time" if a==time else "Out",coords,p)
    samples=[]
    for i,pin in enumerate(["Center","Red","Blue","Soft"]):
        n=g.node("SceneColor",(-850,-350+i*210));g.link(coords,pin,n,"UV");samples.append(n)
    signal = g.function("Hi8Signal", [("Center","Vec3"),("Red","Vec3"),("Blue","Vec3"),("Soft","Vec3"),
                        ("UV","Vec2"),("Clock","Float"),("Wear","Float"),("Grain","Float"),("Vignette","Float")],
                        [("Color","Vec3")], r'''
vec3 signal = vec3(Red.r, Center.g, Blue.b);
float luma = dot(signal, vec3(0.299, 0.587, 0.114));
float softLuma = dot(Soft, vec3(0.299, 0.587, 0.114));
vec3 chroma = Soft - vec3_splat(softLuma);
signal = mix(signal, vec3_splat(luma) + chroma * 0.78, Wear * 0.32);
// A consumer CCD: soft highlight knee, lifted blacks and a green/cyan bias.
signal = pow(max(signal, vec3_splat(0.0)), vec3_splat(0.96));
signal = signal * vec3(0.98, 1.01, 1.025) + vec3(0.008, 0.012, 0.014) * Wear;
float frame = floor(Clock * 29.97);
vec2 pixel = floor(UV * vec2(640.0,480.0));
float noise = fract(sin(dot(pixel,vec2(12.9898,78.233)) + frame*3.119) * 43758.5453) - 0.5;
float chromaNoise = fract(sin(dot(pixel,vec2(39.346,11.135)) + frame*1.719) * 47453.5453) - 0.5;
signal += (vec3_splat(noise) + vec3(chromaNoise,0.0,-chromaNoise)*0.25) * Grain * (1.4-luma*.65) * Wear;
float scan = sin(UV.y*480.0*3.14159265 + mod(frame,2.0)*3.14159265);
signal *= 1.0 - (0.014 + scan*0.009) * Wear;
vec2 p = (UV - vec2_splat(0.5)) * vec2(1.12,1.0);
signal *= 1.0 - smoothstep(0.18,0.72,length(p)) * Vignette;
// A narrow head-switching band, kept below the picture and away from faces.
float tracking = smoothstep(0.976,0.999,UV.y);
signal = mix(signal, vec3_splat(0.10+noise*.16), tracking*Wear*.32);
Color = clamp(signal,vec3_splat(0.0),vec3_splat(1.0));
''',(-350,-150))
    for n,p in zip(samples,["Center","Red","Blue","Soft"]):g.link(n,"Out",signal,p)
    for n,out,p in [(uv,"Out","UV"),(time,"Time","Clock"),(strength,"Out","Wear"),(grain,"Out","Grain"),(vignette,"Out","Vignette")]:g.link(n,out,signal,p)
    # One font fetch, regardless of how many characters are visible. The clock
    # rolls at tape time; no UI system, render target or per-character geometry.
    lines=[(38,30,"REC"),(513,30,"SP"),(38,422,"11:58:00 PM"),(38,446,"JUL. 03 1999"),(490,446,"HI8 / 01")]
    textcode=[]
    for i,(x,y,text) in enumerate(lines):
        textcode += [f"vec2 line{i} = (pixel - vec2({float(x)}, {float(y)})) / 2.0;",
                     f"if (line{i}.x >= 0.0 && line{i}.x < {float(len(text)*6)} && line{i}.y >= 0.0 && line{i}.y < 7.0)","{",
                     f"    float index = floor(line{i}.x / 6.0);",f"    local = vec2(mod(floor(line{i}.x),6.0),floor(line{i}.y));","    inkActive = 1.0;"]
        for j,ch in enumerate(text):
            value=f"{float(ord(ch))}"
            if i==2 and j==6:value="48.0 + floor(mod(Clock,60.0)/10.0)"
            if i==2 and j==7:value="48.0 + floor(mod(Clock,10.0))"
            textcode.append(f"    if (index == {float(j)}) glyph = {value};")
        textcode.append("}")
    hud = g.function("CameraDisplay",[("UV","Vec2"),("Clock","Float"),("Frame","Float")],
         [("GlyphUV","Vec2"),("Active","Float"),("FrameMask","Float"),("Dot","Float"),("Battery","Float")],
         r'''
float aspect = u_viewRect.z / max(u_viewRect.w,1.0);
vec2 fit = vec2(max(1.0,aspect/(4.0/3.0)),max(1.0,(4.0/3.0)/aspect));
vec2 frameUV = (UV - vec2_splat(0.5)) * mix(vec2_splat(1.0),fit,Frame) + vec2_splat(0.5);
FrameMask = step(0.0,frameUV.x)*step(frameUV.x,1.0)*step(0.0,frameUV.y)*step(frameUV.y,1.0);
vec2 pixel = floor(frameUV * vec2(640.0,480.0));
float glyph = 32.0;
float inkActive = 0.0;
vec2 local = vec2_splat(0.0);
''' + "\n".join(textcode) + r'''
GlyphUV = (vec2(mod(glyph,16.0)*6.0, floor(glyph/16.0)*8.0) + local + vec2_splat(0.5)) / vec2(96.0,64.0);
Active = inkActive;
Dot = step(length(pixel-vec2(25.0,36.0)),4.0) * step(0.18,fract(Clock*.8));
vec2 b = abs(pixel-vec2(581.0,36.0));
float outer = step(b.x,20.0)*step(b.y,8.0);
float inner = step(b.x,18.0)*step(b.y,6.0);
float fill = step(pixel.x,584.0)*step(b.x,15.0)*step(b.y,4.0);
Battery = max(outer-inner,fill);
Battery = max(Battery,step(abs(pixel.x-604.0),2.0)*step(b.y,3.0));
''',(300,350))
    for n,out,p in [(uv,"Out","UV"),(time,"Time","Clock"),(frame,"Out","Frame")]:g.link(n,out,hud,p)
    atlas=g.node("Texture2DAsset",(300,1100),dict(Texture=ART+"CameraFont.png"))
    font=g.node("SampleTexture2D",(750,350),dict(Type="Data"))
    g.link(atlas,"Out",font,"Texture");g.link(hud,"GlyphUV",font,"UV")
    composite=g.function("RecordToTape",[("Image","Vec3"),("Glyph","Float"),("Active","Float"),("Mask","Float"),("Dot","Float"),("Battery","Float"),("OSD","Float")],[("Color","Vec3")],r'''
float white = max(Glyph*Active,Battery)*OSD;
vec3 image = mix(Image,vec3(0.91,0.96,0.93),white*.9);
image = mix(image,vec3(0.94,0.13,0.08),Dot*OSD);
Color = image * Mask;
''',(1250,0))
    for n,out,p in [(signal,"Color","Image"),(font,"R","Glyph"),(hud,"Active","Active"),(hud,"FrameMask","Mask"),
                    (hud,"Dot","Dot"),(hud,"Battery","Battery"),(osd,"Out","OSD")]:g.link(n,out,composite,p)
    g.link(composite,"Color",g.out,"Color");g.save()

    g=Graph("CRTAfterHours","Unlit",Fog=True,CastShadows=False)
    uv=g.node("UV",(-1000,-100));time=g.node("Time",(-1000,150))
    tint=g.prop("Phosphor",[.12,.8,1.0,1],(-1000,400),kind="Vec3")
    glow=g.prop("Brightness",2.8,(-1000,600),(0,8))
    screen=g.function("NoSignal",[("UV","Vec2"),("Clock","Float"),("Tint","Vec3"),("Gain","Float")],[("Color","Vec3")],r'''
vec2 p = UV - vec2_splat(0.5);
float border = 1.0-smoothstep(0.44,0.5,max(abs(p.x),abs(p.y)));
float lines = .78 + .22*sin(UV.y*190.0*3.14159265);
float roll = 1.0-smoothstep(0.0,0.075,abs(UV.y-fract(Clock*.12)));
float n = fract(sin(dot(floor(UV*vec2(240.0,180.0)),vec2(12.9898,78.233))+floor(Clock*24.0))*43758.5453);
// Abstract terminal windows and cursor, with no extra screen texture.
float window = step(abs(UV.x-.5),.36)*step(abs(UV.y-.42),.28);
float textRows = step(.77,fract(UV.y*22.0))*step(UV.x,.7)*step(.2,UV.x)*step(.19,UV.y)*step(UV.y,.59);
float cursor = step(abs(UV.x-.3),.035)*step(abs(UV.y-.64),.008)*step(.3,fract(Clock));
vec3 display = Tint*(.10 + window*.13 + textRows*.30 + cursor*.7 + roll*.1 + n*.035);
Color = display*lines*border*Gain;
''',(-350,0))
    for n,out,p in [(uv,"Out","UV"),(time,"Time","Clock"),(tint,"Out","Tint"),(glow,"Out","Gain")]:g.link(n,out,screen,p)
    g.link(screen,"Color",g.out,"Color");g.save()

    g=Graph("DampAsphalt","Lit",CastShadows=False)
    pos=g.node("Position",(-1000,-100),dict(Space="World"))
    wet=g.prop("Dampness",.62,(-1000,250))
    asphalt=g.function("SummerRain",[("World","Vec3"),("Wet","Float")],[("Albedo","Vec3"),("Roughness","Float"),("Normal","Vec3")],r'''
vec2 p = World.xz;
float grit = fract(sin(dot(floor(p*160.0),vec2(12.9898,78.233)))*43758.5453);
float wetPatch = sgValueNoise(p*.37,1.0);
float damp = smoothstep(.36,.68,wetPatch)*Wet;
Albedo = mix(vec3(.055,.068,.083),vec3(.022,.033,.044),damp) * (.82+grit*.3);
Roughness = mix(.88,.23,damp);
Normal = normalize(vec3((grit-.5)*.045,(wetPatch-.5)*.045,1.0));
''',(-350,0))
    g.link(pos,"Out",asphalt,"World");g.link(wet,"Out",asphalt,"Wet")
    for p,o in [("Base Color","Albedo"),("Roughness","Roughness"),("Normal","Normal")]:g.link(asphalt,o,g.out,p)
    g.save()

    g=Graph("BlueHourSky","Unlit",CastShadows=False,Fog=False,RenderFace="Both")
    view=g.node("ViewDirection",(-900,-100),dict(Space="World"))
    sky=g.function("LastLightOfSummer",[("View","Vec3")],[("Color","Vec3")],r'''
vec3 direction = -View;
float elevation = clamp(direction.y,0.0,1.0);
vec3 dusk = mix(vec3(.075,.055,.12),vec3(.008,.019,.055),pow(elevation,.45));
vec2 spherical = vec2(atan2(direction.z,direction.x)/6.2831853+.5,asin(direction.y)/3.14159265+.5);
vec2 cell = floor(spherical*vec2(650.0,325.0));
vec2 within = fract(spherical*vec2(650.0,325.0))-vec2_splat(.5);
float seed = fract(sin(dot(cell,vec2(12.9898,78.233)))*43758.5453);
float stars = step(.996,seed)*(1.0-smoothstep(.02,.14,length(within)))*smoothstep(.05,.4,elevation);
vec3 moonDirection = normalize(vec3(.15,.32,.94));
float separation = length(direction-moonDirection);
float moon = 1.0-smoothstep(.017,.018,separation);
float halo = exp(-separation*38.0)*.03;
float haze = sgValueNoise(spherical*vec2(34.0,100.0),1.0)*(1.0-smoothstep(.0,.4,elevation))*.009;
Color = dusk + vec3_splat(stars*.28+halo+haze) + vec3(.62,.71,.79)*moon;
''',(-300,0))
    g.link(view,"Out",sky,"View");g.link(sky,"Color",g.out,"Color");g.save()


def quat(euler):
    x,y,z = [math.radians(v)*.5 for v in euler]
    cx,cy,cz=math.cos(x),math.cos(y),math.cos(z)
    sx,sy,sz=math.sin(x),math.sin(y),math.sin(z)
    return [sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz]


def material(color, rough=.7, emission=None, intensity=1, texture=None):
    m=dict(Type="StandardMaterial", DiffuseColor=color, Roughness=rough, Metallic=0.0,
           EmissiveColor=emission or [0,0,0], EmissiveIntensity=intensity)
    if texture:m["Textures"]=dict(Diffuse=dict(Path=texture,RenderMode="Opaque"))
    return m


def scene():
    entities=[]
    parts = json.loads((ROOT / "Tools/LastTapeSyntyParts.json").read_text())
    def entity(name, pos=(0,0,0), scale=(1,1,1), rotation=(0,0,0), components=()):
        e=dict(Name=name, GUID=guid(name), DestroyOnLoad=True, Components=[dict(Type="Transform",Position=list(pos),
            Scale=list(scale), Rotation=quat(rotation)), *components])
        entities.append(e)
        return e
    def cube(name,pos,scale,color,rotation=(0,0,0),rough=.75,emission=None,intensity=1):
        return entity(name,pos,scale,rotation,[dict(Type="Mesh",MeshType="Cube",CastShadows=emission is None,
                      Material=material(color,rough,emission,intensity))])
    def model(name,asset,pos,angle=0,scale=1):
        assert (ROOT/TOWN/(asset+".fbx")).exists(),asset
        # These FBXs reference the publisher's old PSD paths. Explicit scene
        # overrides use the supplied PNG, without changing the source imports.
        mat = material([1,1,1],.78,texture="Assets/Models/Synty/Town/Textures/PolygonTown_01_A.png")
        overrides = {key: dict(Type="Mesh",MeshType="Model",CastShadows=True,Material=mat) for key in parts[asset]}
        return entity(name,pos,(scale,)*3,(0,angle,0),[dict(Type="Model", ModelPath=TOWN+asset+".fbx", Compact=True,Parts=overrides)])
    def light(name,pos,color,intensity,range,kind="Point",rot=(0,0,0),shadows=False,**extra):
        return entity(name,pos,rotation=rot,components=[dict(Type="Light",LightType=kind,DirectionalSource="Transform",Color=color,
               Intensity=intensity,Range=range,CastShadows=shadows,ShadowDistance=38,ShadowBias=.45,ShadowNormalBias=1.4,**extra)])
    def plane(name,pos,size,mat,rot=(0,0,0)):
        return entity(name,pos,size,rot,[dict(Type="Mesh",MeshType="Plane",Material=mat,CastShadows=False)])
    def sign(name,pos,size,art,brightness=.3):
        mat=material([1,1,1],.8,[.45,.9,.8],brightness,ART+art+".png")
        mat["Tiling"]=[1,-1]
        # The atlas is also the emissive mask, preserving dark lettering backgrounds.
        mat["Textures"]["Emissive"]=dict(Path=ART+art+".png",RenderMode="Opaque")
        return plane(name,pos,size,mat,(-90,0,0))

    camera=entity("Camcorder - July 1999",(-7.0,2.2,-7.8),rotation=(3.0,17.6,0),components=[
        dict(Type="Camera",IsCurrent=True,Projection="Perspective",FieldOfView=54,Zoom=54,Near=.08,Far=140,
             ClearType="Color",ClearColor=[.035,.055,.1],ProceduralSky=dict(Time=19.8,TimeScale=0,Month=7,Latitude=43,
             CloudCoverage=.32,CloudDensity=.65,Turbidity=2.4,SunSize=1.5,MoonBrightness=.4,StarBrightness=.35)),
        dict(Type="PostProcess",Tonemapper="ACES",Bloom=True,BloomThreshold=1.1,BloomIntensity=.07,BloomRadius=.7,
             AmbientOcclusion=True,AORadius=.45,AOIntensity=.85,FXAA=True,TemporalAA=False,
             AutoExposure=False,ExposureCompensation=1.0,Contrast=1.04,Saturation=.86,Temperature=-.025,Tint=-.015,
             Fog=True,FogColor=[.075,.12,.18],FogDensity=.013,FogHeight=.3,FogHeightFalloff=.19,FogStartDistance=9,
             FogMaxOpacity=.62,VolumetricFog=False,VignetteIntensity=0,Graphs=[GRAPH+"Camcorder1999.shadergraph"]),
        dict(Type="ScriptComponent",ScriptName="LastTapeCamera",ScriptFields=json.dumps(dict(Sway=.12))),
        dict(Type="Light",LightType="Spot",Color=[.83,.9,1],Intensity=95,Range=28,InnerConeAngle=26,OuterConeAngle=43,CastShadows=False)])
    entity("Hand-painted blue hour sky",(0,0,10),(100,100,100),components=[dict(Type="Mesh",MeshType="Sphere",CastShadows=False,
           Material=dict(Type="ShaderGraphMaterial",Graph=GRAPH+"BlueHourSky.shadergraph",Params={},Textures={}))])
    light("Blue hour - soft moon key",(0,14,-5),[.48,.64,.95],2.8,100,"Directional",(38,-35,0),True)
    light("Sky bounce over court",(0,14,4),[.42,.55,.85],.75,100,"Directional",(68,145,0))

    plane("Entire court - damp asphalt",(0,-.045,4),(22,1,26),dict(Type="ShaderGraphMaterial",Graph=GRAPH+"DampAsphalt.shadergraph",Params={},Textures={}))
    # Foreground street markings lead into the lit garage.
    for i in range(6):
        cube(f"Faded center stripe {i}",(2.5,.006,-16+i*5),(.055,.006,.8),[.52,.42,.25])
    for side in [-1,1]:
        x=side*9.5
        cube(f"Grass verge {side}",(x,-.09,9),(3.2,.15,17),[.075,.16,.105])
        cube(f"Sidewalk {side}",(side*6.6,-.035,4),(.85,.10,22),[.32,.34,.32])
        for i in range(17):
            cube(f"Curb {side} {i}",(side*5.7,.015,-16+i*2.5),(.12,.12,1.22),[.38,.39,.36])
    plane("Party driveway",(-3,.025,8),(3.05,1,5),material([.25,.27,.27],.8))

    # Houses are individual Synty presets, not the expensive complete demo town.
    model("Maple Court 02 - pale blue house","SM_Bld_House_Preset_02",(9.8,.1,13),180)
    model("Maple Court 03 - neighbour","SM_Bld_House_Preset_01",(-12,.1,18),90)
    model("Maple Court 04 - end of street","SM_Bld_House_Preset_02",(1.5,.1,28),180)
    model("Maple Court 05 - distant roof","SM_Bld_House_Preset_01",(13,.1,32),180)
    # Open-front garage: low-cost architectural shell gives the hero props room
    # and keeps their exact layout independent of the closed prefab interiors.
    shell=[.29,.32,.33]
    cube("Garage slab",(-3,.12,10),(3.25,.12,3.5),[.3,.31,.3])
    cube("Garage left wall",(-6.2,1.75,10),(.12,1.55,3.5),shell)
    cube("Garage right wall",(.2,1.75,10),(.12,1.55,3.5),shell)
    cube("Garage back wall",(-3,1.75,13.4),(3.1,1.55,.12),[.20,.27,.28])
    cube("Garage fascia",(-3,3.15,6.5),(3.3,.32,.16),[.54,.46,.35])
    cube("Garage roof",(-3,3.52,10),(3.5,.12,3.8),[.14,.19,.23])
    cube("Raised roller door",(-3,3.15,7.8),(2.9,.06,1.0),[.33,.39,.4])
    sign("Garage sign - LAN PARTY summer 99",(-3,3.16,6.31),(1.2,1,.32),"LAN99",1.4)
    light("Garage tungsten practical",(-3,2.95,9.5),[1,.62,.3],9.0,8,"Rectangle",(90,0,0),RectangleWidth=4.5,RectangleHeight=3)
    light("Garage warm bounce onto consoles",(-3.5,2.1,7.6),[1,.69,.4],13,6)
    light("Driveway sodium pool",(-5.6,3.8,3.5),[1,.61,.24],65,12,"Spot",(65,12,0),True,InnerConeAngle=34,OuterConeAngle=62)
    light("CRT bounce into driveway",(-2.0,1.25,7.3),[.1,.68,1],5.5,7)
    light("Neighbour porch pool",(7.3,2.4,8),[1,.66,.33],6,7)

    # Two desktop rigs, a floor television and plenty of abandoned snacks.
    for i,x in enumerate([-4.7,-2.25]):
        model(f"LAN desk {i}","SM_Prop_Desk_01",(x,.25,11.5),180)
        model(f"Beige CRT monitor {i}","SM_Prop_Computer_Screen_01",(x,1.13,11.55))
        model(f"Keyboard {i}","SM_Prop_Computer_Keyboard_01",(x,1.13,11.12),180)
        model(f"Mouse {i}","SM_Prop_Computer_Mouse_01",(x+.55,1.13,11.15),180)
        model(f"Desk chair {i}","SM_Prop_DeskChair_01",(x,.25,10.25),0)
        screen=plane(f"Animated phosphor display {i}",(x,1.47,11.41),(.255,1,.18),
            dict(Type="ShaderGraphMaterial",Graph=GRAPH+"CRTAfterHours.shadergraph",Params={"Phosphor":[.08,.7,1,1] if i==0 else [.42,1,.37,1]},Textures={}),(-90,0,0))
        model(f"Desk soda {i}","SM_Item_Drink_01",(x+.75,1.13,11.35),25)
    model("Living room couch dragged outside","SM_Prop_Couch_01",(-4,.23,8.7),-10)
    model("Console coffee table","SM_Prop_CoffeeTable_01",(-3.3,.25,7.1))
    model("PS1 era console","SM_Prop_Game_Console_01",(-3.5,.71,7.1),15)
    model("Controller abandoned on table","SM_Prop_Game_Controller_01",(-2.85,.71,6.9),-25)
    model("Pizza at midnight","SM_Item_Pizza_Box_01",(-4.7,.25,9.1),20,.7)
    model("Driveway television","SM_Prop_Television_Old_01",(-.6,.25,7.7),0,1.25)
    plane("Driveway TV phosphor",(-.6,.67,7.55),(.36,1,.235),dict(Type="ShaderGraphMaterial",Graph=GRAPH+"CRTAfterHours.shadergraph",Params={},Textures={}),(-90,0,0))
    model("Stereo on the garage floor","SM_Prop_Stereo_01",(-5.5,.25,12),180)
    for x in [-5.75,-.45]:model(f"Big speaker {x}","SM_Prop_Stereo_Speaker_Large_01",(x,.25,11.2),180)
    model("Spare folding chair","SM_Prop_Deckchair_01",(-5.8,.03,5.9),25)
    model("Drink beside folding chair","SM_Item_Drink_02",(-5,.03,5),20)
    model("Pizza box on driveway","SM_Item_Pizza_Box_01",(-1.2,.03,5.8),-15)
    model("Summer convertible","SM_Veh_Convertable_01",(3.6,.04,3.2),-20)
    model("Pickup in the background","SM_Veh_Pickup_01",(5.1,.04,23),-12)
    model("Soccer ball forgotten in the gutter","SM_Item_Ball_Soccer_01",(-5.3,.03,1.5),0,.9)
    model("Driveway trash can","SM_Prop_RubbishBin_01",(.7,.03,12.5),-15)
    model("Garbage bag","SM_Prop_TrashBag_01",(.5,.03,11.8),20)
    for i in range(3):
        cube(f"Home video cassette {i}",(-4.7+i*.08,.065+i*.08,4.6),(.25,.04,.16),[.035,.04,.045])
    plane("Handwritten tape label",(-4.54,.308,4.6),(.23,1,.14),material([1,1,1],.9,texture=ART+"TapeLabel.png"))
    model("Coiled garden hose","SM_Prop_HoseReel_01",(6.9,.13,12),90)
    model("Porch deckchair","SM_Prop_Deckchair_03",(6.8,.15,15),-50)
    model("Garden table","SM_Prop_Outdoor_Table_01",(6.5,.15,16),35)

    # Oversized sodium lamps are silhouettes against the blue-hour treeline.
    for i,(x,z) in enumerate([(-5.7,3),(5.8,16),(-5.7,26)]):
        model(f"Streetlamp {i}","SM_Prop_Streetlamp_02",(x,.14,z),0,1.25)
        entity(f"Streetlamp glowing bulb {i}",(x,3.85,z),(.1,.15,.1),components=[dict(Type="Mesh",MeshType="Sphere",CastShadows=False,
               Material=material([1,.69,.35],.6,[1,.56,.18],6))])
        if i>0:light(f"Sodium lamp pool {i}",(x,3.7,z),[1,.64,.29],8,9)
    sign("Maple Court dead end",(5.6,2.35,19),(1,1,.5),"DeadEnd",.15)
    cube("Dead end sign post",(5.6,1.2,19),(.04,1.2,.04),[.24,.28,.27])

    for i in range(12):
        x=-6.15+i*.59;z=6.05;y=3.75-.5*math.sin(i/11*math.pi)
        color=[[1,.29,.09],[.18,.8,1],[1,.74,.21],[.9,.18,.43]][i%4]
        cube(f"Party cable {i}",(x,y+.07,z),(.3,.012,.012),[.045,.055,.06],rotation=(0,0,-8 if i<6 else 8))
        entity(f"Party bulb {i}",(x,y,z),(.055,.08,.055),components=[dict(Type="Mesh",MeshType="Sphere",CastShadows=False,
                      Material=material(color,.7,color,4))])
    light("Party string warm spill",(-4.8,3,6),[1,.4,.18],1.5,5)
    light("Party string cyan spill",(-.7,3,6),[.2,.66,1],1.7,5)

    # Repeated meshes and identical material state are automatically instanced.
    for side in [-1,1]:
        for i in range(7):
            model(f"Picket fence {side} {i}","SM_Env_Fence_White_Straight_01",(side*8.0,.15,-3+i*2.5),90)
        for i in range(7):
            x=side*(10.5+(i%2)*3);z=-1+i*6
            if side==-1 and 6<z<18:continue
            model(f"Court tree {side} {i}","SM_Env_Tree_01" if i%2==0 else "SM_Env_Tree_03",(x,.1,z),i*57,1.25+(i%3)*.17)
        for i in range(8):
            model(f"Hedge {side} {i}","SM_Env_Bush_01",(side*8.9,.12,-3+i*4.3),i*35,1.2)
    for i in range(9):
        model(f"Backdrop tree {i}","SM_Env_Tree_Large_01",(-20+i*5,.1,38+(i%3)*3),i*37,1.3)
    save("Assets/Scenes/LastTape1999.lvl", dict(Version=2,Cores=[],Entities=entities))
    print(f"LastTape1999: {len(entities)} authored entities, 4 shader graphs")


if __name__ == "__main__":
    artwork()
    graphs()
    scene()
