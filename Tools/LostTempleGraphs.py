"""Shader graphs for the Lost Temple scene, written with a small graph-building DSL.

Imported by BuildLostTemple.py; each function returns a graph document (the .shadergraph JSON).
Every graph is made of ordinary nodes, so it opens and edits normally in Havana's Shader Graph
editor. Custom Function nodes are only used where a pattern reads better as a few lines of code
(the rune ring and the water caustics).
"""

TEX = "Assets/Models/Synty/ExplorerKit/Textures/"
ROCK = TEX + "Generic_Rock.png"
GRASS = TEX + "Generic_Grass.png"
GRASS_NORMALS = TEX + "Generic_Grass_Normals.png"
DIRT = TEX + "Generic_Dirt.png"
ATLAS = TEX + "Alts/Generic_01_A.png"
IVY = TEX + "Generic_Ivy.tga"
LENS_DIRT = TEX + "SyntyLensDirt_01.png"
FLAME = TEX + "FX/Generic_Candle_Flame_01.png"


def vec4(value):
    if isinstance(value, (int, float)):
        return [float(value)] * 4
    value = [float(v) for v in value]
    return value + [0.0] * (4 - len(value))


class Pin:
    def __init__(self, node, name):
        self.node = node
        self.name = name


class Node:
    def __init__(self, graph, node_id):
        self.graph = graph
        self.id = node_id

    def __getitem__(self, pin):
        return Pin(self, pin)


class Graph:
    """Builds a graph document. Inputs are pins/nodes (linked) or numbers/lists (inline defaults)."""

    def __init__(self, target, **settings):
        self.settings = dict(Target=target, **settings)
        self.nodes = [{"Id": 1, "Type": "Output"}]
        self.links = []
        self.props = []
        self.output = Node(self, 1)

    def node(self, node_type, ins=None, settings=None):
        node_id = len(self.nodes) + 1
        entry = {"Id": node_id, "Type": node_type}
        if settings:
            entry["Settings"] = settings
        self.nodes.append(entry)
        self.connect(node_id, entry, ins or {})
        return Node(self, node_id)

    def connect(self, node_id, entry, ins):
        for pin, value in ins.items():
            if isinstance(value, Pin):
                self.links.append([value.node.id, value.name, node_id, pin])
            elif isinstance(value, Node):
                self.links.append([value.id, "Out", node_id, pin])
            else:
                entry.setdefault("Defaults", {})[pin] = vec4(value)

    def outputs(self, **pins):
        self.connect(1, self.nodes[0], {name.replace("_", " "): value for name, value in pins.items()})

    def prop(self, name, value_type, default=0.0, exposed=True, color=False, hdr=False, rng=None, texture=None, fallback="white"):
        prop_id = "p%d" % (len(self.props) + 1)
        prop = {"Id": prop_id, "Name": name, "Type": value_type, "Exposed": exposed}
        if value_type in ("Texture2D", "TextureCube"):
            prop["Texture"] = texture or ""
            prop["DefaultTexture"] = fallback
        else:
            prop["Default"] = vec4(default)
            if value_type != "Float":
                prop["Default"][3] = 1.0
        if color:
            prop["IsColor"] = True
        if hdr:
            prop["HDR"] = True
        if rng:
            prop["Range"] = [float(rng[0]), float(rng[1])]
        self.props.append(prop)
        return self.node("Property", settings={"Property": prop_id})

    # Shorthands for the nodes used most.
    def add(self, a, b): return self.node("Add", {"A": a, "B": b})
    def sub(self, a, b): return self.node("Subtract", {"A": a, "B": b})
    def mul(self, a, b): return self.node("Multiply", {"A": a, "B": b})
    def lerp(self, a, b, t): return self.node("Lerp", {"A": a, "B": b, "T": t})
    def smooth(self, e1, e2, x): return self.node("Smoothstep", {"Edge1": e1, "Edge2": e2, "In": x})
    def swizzle(self, x, mask): return self.node("Swizzle", {"In": x}, {"Mask": mask})
    def split(self, x): return self.node("Split", {"In": x})
    def sat(self, x): return self.node("Saturate", {"In": x})
    def one_minus(self, x): return self.node("OneMinus", {"In": x})
    def max(self, a, b): return self.node("Maximum", {"A": a, "B": b})
    def sine(self, x): return self.node("Sine", {"In": x})
    def position(self, space="World"): return self.node("Position", settings={"Space": space})
    def normal(self, space="World"): return self.node("NormalVector", settings={"Space": space})
    def time(self): return self.node("Time")
    def const(self, value): return self.node("Float", settings={"Value": float(value)})
    def vec3(self, value): return self.node("Vector3", settings={"Value": vec4(value)})
    def color(self, value, hdr=False):
        settings = {"Value": vec4(list(value) + [1.0] if len(value) == 3 else value)}
        if hdr:
            settings["HDR"] = True
        return self.node("Color", settings=settings)
    def combine(self, r=0.0, g=0.0, b=0.0, a=1.0): return self.node("Combine", {"R": r, "G": g, "B": b, "A": a})
    def sample(self, texture, uv=None, kind="Color"):
        ins = {"Texture": texture}
        if uv is not None:
            ins["UV"] = uv
        return self.node("SampleTexture2D", ins, {"Type": kind})
    def custom(self, name, inputs, outputs, code, ins):
        return self.node("CustomFunction", ins, {
            "Name": name,
            "Inputs": [{"Name": n, "Type": t} for n, t in inputs],
            "Outputs": [{"Name": n, "Type": t} for n, t in outputs],
            "Code": code.strip("\n"),
        })

    def document(self):
        self.layout()
        return {"Version": 1, "Settings": self.settings, "Properties": self.props, "Nodes": self.nodes, "Links": self.links}

    def layout(self):
        # Columns by distance from the output node, rows in creation order.
        depth = {1: 0}
        changed = True
        while changed:
            changed = False
            for src, _, dst, _ in self.links:
                if dst in depth and depth.get(src, -1) < depth[dst] + 1:
                    depth[src] = depth[dst] + 1
                    changed = True
        rows = {}
        for entry in self.nodes:
            column = depth.get(entry["Id"], max(depth.values()) + 1)
            row = rows.get(column, 0)
            rows[column] = row + 1
            entry["Position"] = [1200 - 280 * column, row * 190 - 300]


MASONRY_CODE = """
float a = radians(FrameYaw);
float c = cos(a);
float s = sin(a);
vec3 p = vec3(Position.x * c - Position.z * s, Position.y, Position.x * s + Position.z * c);
vec3 n = abs(vec3(Normal.x * c - Normal.z * s, Normal.y, Normal.x * s + Normal.z * c));
vec2 uv = n.y > 0.7 ? p.xz : (n.x > n.z ? p.zy : p.xy);
vec2 size = n.y > 0.7 ? vec2_splat(BlockSize.x * 0.8) : BlockSize;
vec2 q = uv / size;
q.x += mod(floor(q.y), 2.0) * 0.5;
vec2 cell = floor(q);
vec2 f = fract(q);
vec2 edge = min(f, vec2_splat(1.0) - f) * size;
float d = min(edge.x, edge.y);
Mortar = 1.0 - smoothstep(Gap * 0.5, Gap * 0.5 + 0.012, d);
Bevel = smoothstep(Gap * 0.5, Gap * 0.5 + 0.07, d);
Block = fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
"""


def ancient_stone():
    """Carved temple stone: triplanar rock, laid in courses of blocks, moss on top faces and in the joints,
    dark and glossy below the waterline."""
    g = Graph("Lit")
    stone_tex = g.prop("Stone Texture", "Texture2D", texture=ROCK)
    moss_tex = g.prop("Moss Texture", "Texture2D", texture=GRASS)
    tint = g.prop("Stone Tint", "Vec3", [0.78, 0.74, 0.64], color=True)
    moss_color = g.prop("Moss Color", "Vec3", [0.55, 0.7, 0.35], color=True)
    moss_amount = g.prop("Moss Amount", "Float", 0.5, rng=(0, 1))
    tile = g.prop("Tile", "Float", 0.35, rng=(0.05, 4))
    wet_height = g.prop("Wet Height", "Float", -50.0)
    roughness = g.prop("Roughness", "Float", 0.85, rng=(0, 1))
    masonry = g.prop("Masonry", "Float", 0.0, rng=(0, 1))
    block_size = g.prop("Block Size", "Vec2", [1.1, 0.45])
    frame_yaw = g.prop("Frame Yaw", "Float", 0.0, rng=(-180, 180))
    variation = g.prop("Block Variation", "Float", 0.35, rng=(0, 1))

    pos = g.position("World")
    world_normal = g.normal("World")
    stone = g.swizzle(g.node("Triplanar", {"Texture": stone_tex, "Tile": tile, "Blend": 6.0}), "xyz")
    blocks = g.custom("Masonry", [("Position", "Vec3"), ("Normal", "Vec3"), ("BlockSize", "Vec2"), ("Gap", "Float"), ("FrameYaw", "Float")],
                      [("Mortar", "Float"), ("Bevel", "Float"), ("Block", "Float")], MASONRY_CODE,
                      {"Position": pos, "Normal": world_normal, "BlockSize": block_size, "Gap": 0.03, "FrameYaw": frame_yaw})
    mortar = g.mul(blocks["Mortar"], masonry)
    shade = g.lerp(1.0, g.add(g.sub(1.0, g.mul(variation, 0.5)), g.mul(blocks["Block"], variation)), masonry)
    albedo = g.mul(g.mul(stone, tint), g.mul(shade, g.lerp(1.0, 0.35, mortar)))
    height = g.add(g.mul(g.node("Luminance", {"In": stone}), 0.5), g.mul(g.lerp(0.5, blocks["Bevel"], masonry), 0.5))

    moss_rgb = g.swizzle(g.node("Triplanar", {"Texture": moss_tex, "Tile": g.mul(tile, 2.3), "Blend": 4.0}), "xyz")
    moss = g.mul(moss_rgb, moss_color)
    up = g.split(world_normal)["G"]
    patches = g.node("FractalNoise", {"UV": g.swizzle(pos, "xz"), "Scale": 0.6, "Octaves": 4.0})
    coverage = g.add(g.add(g.mul(up, 0.7), g.mul(patches, 0.6)), g.mul(mortar, 0.35))
    edge = g.sub(1.15, moss_amount)
    moss_mask = g.smooth(edge, g.add(edge, 0.2), coverage)

    above_water = g.sub(g.split(pos)["G"], wet_height)
    wet = g.one_minus(g.smooth(0.0, 0.8, above_water))
    color = g.mul(g.lerp(albedo, moss, moss_mask), g.lerp(1.0, 0.45, wet))
    rough = g.lerp(g.lerp(roughness, 0.95, g.max(moss_mask, mortar)), 0.18, wet)
    bumps = g.node("NormalFromHeight", {"In": height, "Strength": 0.6})
    occlusion = g.mul(g.sat(g.node("Remap", {"In": height, "In Min": 0.05, "In Max": 0.5, "Out Min": 0.55, "Out Max": 1.0})),
                      g.lerp(1.0, 0.45, mortar))
    g.outputs(Base_Color=color, Roughness=rough, Normal=bumps, Occlusion=occlusion)
    return g


def jungle_floor():
    """The clearing: dirt and grass mixed by large noise patches, darker and wet around the pool."""
    g = Graph("Lit")
    dirt_tex = g.prop("Dirt Texture", "Texture2D", texture=DIRT)
    grass_tex = g.prop("Grass Texture", "Texture2D", texture=GRASS)
    grass_normals = g.prop("Grass Normals", "Texture2D", texture=GRASS_NORMALS, fallback="normal")
    dirt_tint = g.prop("Dirt Tint", "Vec3", [0.78, 0.66, 0.52], color=True)
    grass_tint = g.prop("Grass Tint", "Vec3", [0.62, 0.74, 0.42], color=True)
    tile = g.prop("Tile", "Float", 0.22, rng=(0.01, 2))
    pool = g.prop("Pool Center", "Vec3", [0, 0, 0])
    pool_radius = g.prop("Pool Radius", "Float", 6.0)
    grass_amount = g.prop("Grass Amount", "Float", 0.5, rng=(0, 1))

    ground = g.swizzle(g.position("World"), "xz")
    uv = g.mul(ground, tile)
    grass_uv = g.node("TilingAndOffset", {"UV": uv, "Tiling": [0.83, 0.83], "Offset": [0.37, 0.11]})
    dirt = g.mul(g.sample(dirt_tex, uv)["RGB"], dirt_tint)
    grass = g.mul(g.sample(grass_tex, grass_uv)["RGB"], grass_tint)
    patches = g.node("FractalNoise", {"UV": ground, "Scale": 0.06, "Octaves": 5.0})
    edge = g.sub(1.05, grass_amount)
    mask = g.smooth(g.sub(edge, 0.08), g.add(edge, 0.06), patches)

    distance = g.node("Distance", {"A": ground, "B": g.swizzle(pool, "xz")})
    wet = g.one_minus(g.smooth(pool_radius, g.add(pool_radius, 4.0), distance))
    color = g.mul(g.lerp(dirt, grass, mask), g.lerp(1.0, 0.42, wet))
    rough = g.lerp(g.lerp(0.97, 0.9, mask), 0.22, wet)
    normal = g.node("NormalStrength", {"In": g.lerp(g.vec3([0, 0, 1]), g.sample(grass_normals, grass_uv, "Normal")["RGB"], mask), "Strength": 0.8})
    g.outputs(Base_Color=color, Roughness=rough, Normal=normal)
    return g


def temple_water():
    """The plunge pool: two drifting noise layers for ripples, fresnel depth colour, foam under the falls."""
    g = Graph("Lit", Surface="Transparent", Blend="Alpha", CastShadows=False)
    deep = g.prop("Deep Color", "Vec3", [0.01, 0.05, 0.06], color=True)
    shallow = g.prop("Shallow Color", "Vec3", [0.05, 0.22, 0.2], color=True)
    foam_center = g.prop("Foam Center", "Vec3", [0, 0, 0])
    foam_radius = g.prop("Foam Radius", "Float", 3.0)
    clarity = g.prop("Clarity", "Float", 0.3, rng=(0, 1))

    ground = g.swizzle(g.position("World"), "xz")
    uv = g.mul(ground, 0.18)
    ripple_a = g.node("GradientNoise", {"UV": g.node("Panner", {"UV": uv, "Speed": [0.035, 0.02]}), "Scale": 7.0})
    ripple_b = g.node("GradientNoise", {"UV": g.node("Panner", {"UV": uv, "Speed": [-0.03, 0.045]}), "Scale": 13.0})
    height = g.add(g.mul(ripple_a, 0.6), g.mul(ripple_b, 0.4))
    normal = g.node("NormalFromHeight", {"In": height, "Strength": 0.14})
    fresnel = g.node("FresnelEffect", {"Power": 4.0})

    churn = g.node("GradientNoise", {"UV": g.node("Panner", {"UV": g.mul(ground, 0.9), "Speed": [0.0, -0.35]}), "Scale": 4.0})
    near_falls = g.one_minus(g.smooth(0.0, foam_radius, g.node("Distance", {"A": ground, "B": g.swizzle(foam_center, "xz")})))
    foam = g.mul(g.smooth(0.35, 0.7, g.add(churn, g.mul(near_falls, 0.45))), near_falls)

    color = g.lerp(g.lerp(shallow, deep, g.mul(fresnel, 0.8)), g.vec3([0.85, 0.9, 0.9]), foam)
    alpha = g.node("Maximum", {"A": g.lerp(g.one_minus(clarity), 0.96, fresnel), "B": foam})
    # The gorge walls hide most of the sky the probe sees, so dim the reflected ambient.
    g.outputs(Base_Color=color, Normal=normal, Roughness=g.lerp(0.04, 0.5, foam), Alpha=alpha, Occlusion=g.lerp(0.4, 1.0, foam))
    return g


def waterfall():
    """Falling water on the waterfall mesh: streaks scrolling down in object space, foam at the base."""
    g = Graph("Lit", Surface="Transparent", Blend="Alpha", CastShadows=False)
    water_color = g.prop("Water Color", "Vec3", [0.22, 0.42, 0.42], color=True)
    foam_color = g.prop("Foam Color", "Vec3", [0.92, 0.95, 0.95], color=True)
    speed = g.prop("Fall Speed", "Float", 0.9, rng=(0, 4))
    base_height = g.prop("Base Height", "Float", -10.0)

    local = g.split(g.position("Object"))
    t = g.time()["Time"]
    across = g.add(g.mul(local["R"], 1.4), g.mul(local["B"], 0.9))
    down = g.add(g.mul(local["G"], 0.16), g.mul(t, speed))
    uv = g.combine(across, down)["RG"]
    streak_a = g.node("GradientNoise", {"UV": uv, "Scale": 3.0})
    streak_b = g.node("GradientNoise", {"UV": g.node("TilingAndOffset", {"UV": uv, "Tiling": [2.3, 1.6], "Offset": [0.4, 0.0]}), "Scale": 3.0})
    streaks = g.add(g.mul(streak_a, 0.65), g.mul(streak_b, 0.35))
    churn = g.one_minus(g.smooth(base_height, g.add(base_height, 2.5), local["G"]))
    foam = g.sat(g.add(g.smooth(0.4, 0.68, streaks), churn))
    color = g.lerp(water_color, foam_color, foam)
    # Thin over the lip, where the sheet leaves the rock.
    lip = g.one_minus(g.smooth(-0.9, 0.05, local["G"]))
    alpha = g.mul(g.lerp(0.45, 0.96, foam), lip)
    normal = g.node("NormalFromHeight", {"In": streaks, "Strength": 0.4})
    g.outputs(Base_Color=color, Normal=normal, Roughness=0.3, Alpha=alpha)
    return g


def idol_gold():
    """The idol: polished gold with veins of light that pulse."""
    g = Graph("Lit")
    gold = g.prop("Gold Color", "Vec3", [1.0, 0.72, 0.3], color=True)
    glow = g.prop("Glow Color", "Vec3", [0.2, 1.0, 0.75], color=True, hdr=True)
    intensity = g.prop("Glow Intensity", "Float", 6.0, rng=(0, 30))
    pulse_speed = g.prop("Pulse Speed", "Float", 1.6, rng=(0, 10))
    vein_scale = g.prop("Vein Scale", "Float", 28.0, rng=(1, 100))

    local = g.split(g.position("Object"))
    uv = g.combine(g.add(local["R"], g.mul(local["B"], 0.7)), local["G"])["RG"]
    noise = g.node("GradientNoise", {"UV": uv, "Scale": vein_scale})
    ridge = g.one_minus(g.node("Absolute", {"In": g.sub(g.mul(noise, 2.0), 1.0)}))
    veins = g.node("Power", {"A": ridge, "B": 12.0})
    pulse = g.add(g.mul(g.sine(g.mul(g.time()["Time"], pulse_speed)), 0.5), 0.5)
    emission = g.mul(g.mul(glow, veins), g.mul(intensity, g.add(0.3, g.mul(pulse, 0.7))))
    wear = g.node("GradientNoise", {"UV": uv, "Scale": 90.0})
    g.outputs(Base_Color=gold, Metallic=1.0, Roughness=g.add(0.12, g.mul(wear, 0.22)), Emission=emission)
    return g


def foliage(cutout=False):
    """Synty foliage that sways in the wind (shadows follow); the sway grows with height above the pivot.
    The cutout variant clips leaf cards (ivy) by the texture's alpha, in their shadows too."""
    settings = dict(OffsetSpace="World")
    if cutout:
        settings.update(AlphaClip=True, RenderFace="Both")
    g = Graph("Lit", **settings)
    atlas = g.prop("Albedo", "Texture2D", texture=IVY if cutout else ATLAS)
    tint = g.prop("Tint", "Vec3", [1, 1, 1], color=True)
    strength = g.prop("Wind Strength", "Float", 0.08, rng=(0, 1))
    speed = g.prop("Wind Speed", "Float", 1.3, rng=(0, 6))
    sway_height = g.prop("Sway Height", "Float", 5.0, rng=(-30, 30))

    world = g.split(g.position("World"))
    t = g.time()["Time"]
    phase = g.add(g.add(g.mul(world["R"], 0.31), g.mul(world["B"], 0.23)), g.mul(t, speed))
    sway = g.add(g.sine(phase), g.mul(g.sine(g.add(g.mul(phase, 2.37), 1.3)), 0.35))
    gust = g.add(g.mul(g.sine(g.add(g.mul(t, 0.37), g.mul(world["R"], 0.05))), 0.5), 0.5)
    amount = g.mul(strength, g.add(0.45, gust))
    # Negative heights measure downwards, for things that hang from their pivot (vines).
    rise = g.sat(g.node("Divide", {"A": g.split(g.position("Object"))["G"], "B": sway_height}))
    mask = g.mul(g.mul(rise, rise), amount)
    flutter = g.mul(g.sine(g.add(g.mul(t, 6.5), g.add(g.mul(world["R"], 3.1), g.mul(world["G"], 4.7)))), 0.12)
    offset = g.combine(g.mul(g.add(sway, flutter), mask), 0.0, g.mul(g.node("Cosine", {"In": g.mul(phase, 0.83)}), g.mul(mask, 0.6)))["RGB"]
    texel = g.sample(atlas)
    albedo = g.mul(texel["RGB"], tint)
    if cutout:
        g.outputs(Position_Offset=offset, Base_Color=albedo, Roughness=0.7, Alpha=texel["A"], Alpha_Clip_Threshold=0.45)
    else:
        g.outputs(Position_Offset=offset, Base_Color=albedo, Roughness=0.72)
    return g


def glow_mushroom():
    """Bioluminescent caps: the atlas colour below, a breathing glow above Cap Height."""
    g = Graph("Lit")
    atlas = g.prop("Albedo", "Texture2D", texture=ATLAS)
    glow = g.prop("Glow Color", "Vec3", [0.25, 0.85, 1.0], color=True, hdr=True)
    intensity = g.prop("Glow Intensity", "Float", 4.0, rng=(0, 20))
    cap_height = g.prop("Cap Height", "Float", 0.22)

    local = g.split(g.position("Object"))
    world = g.split(g.position("World"))
    cap = g.smooth(cap_height, g.add(cap_height, 0.12), local["G"])
    breathe = g.add(g.mul(g.sine(g.add(g.mul(g.time()["Time"], 1.3), g.add(g.mul(world["R"], 2.1), g.mul(world["B"], 1.7)))), 0.5), 0.5)
    albedo = g.sample(atlas)["RGB"]
    color = g.lerp(albedo, g.mul(albedo, glow), g.mul(cap, 0.6))
    emission = g.mul(g.mul(glow, cap), g.mul(intensity, g.add(0.35, g.mul(breathe, 0.65))))
    g.outputs(Base_Color=color, Roughness=0.45, Emission=emission)
    return g


def spirit_beam():
    """Unlit, additive: a column of spirit light over the rune circle, hottest in the core (seen through the
    most glow), drifting bands rising, fading out at the top."""
    g = Graph("Unlit", Surface="Transparent", Blend="Additive", RenderFace="Both", CastShadows=False)
    color = g.prop("Beam Color", "Vec3", [0.25, 1.0, 0.8], color=True, hdr=True)
    intensity = g.prop("Intensity", "Float", 1.6, rng=(0, 20))
    rise = g.prop("Rise Speed", "Float", 0.35, rng=(0, 4))

    local = g.split(g.position("Object"))
    height = g.sat(g.mul(g.add(local["G"], 1.0), 0.5))
    facing = g.node("FresnelEffect", {"Power": 1.5})
    core = g.one_minus(facing)
    bands = g.node("GradientNoise", {"UV": g.combine(g.node("Arctangent2", {"A": local["R"], "B": local["B"]}),
                                                      g.sub(g.mul(local["G"], 1.5), g.mul(g.time()["Time"], rise)))["RG"], "Scale": 3.0})
    fade = g.mul(g.one_minus(height), g.smooth(0.0, 0.08, height))
    glow = g.mul(g.mul(g.mul(core, core), g.add(0.35, bands)), g.mul(fade, intensity))
    g.outputs(Color=g.mul(color, glow), Alpha=g.sat(glow))
    return g


RUNE_CODE = """
vec2 p = UV - vec2_splat(0.5);
float r = length(p) * 2.0;
float a = atan2(p.y, p.x) * 0.15915494 + 0.5;
float ring = 1.0 - smoothstep(0.0, 0.012, abs(r - 0.94));
ring += 1.0 - smoothstep(0.0, 0.008, abs(r - 0.79));
ring += 1.0 - smoothstep(0.0, 0.01, abs(r - 0.43));
ring += (1.0 - smoothstep(0.0, 0.006, abs(r - 0.36))) * 0.6;
float turn = a + Time * Speed;
float cell = floor(turn * 28.0);
float seg = fract(turn * 28.0);
float h = fract(sin(cell * 91.7) * 4375.85);
float h2 = fract(sin(cell * 17.3 + 4.1) * 2953.31);
float band = step(0.815, r) * step(r, 0.915);
float stroke = step(0.22, seg) * step(seg, 0.32 + h * 0.45);
float bar = step(abs(r - (0.83 + h2 * 0.06)), 0.007) * step(0.2, seg) * step(seg, 0.8);
float glyph = band * max(stroke * step(0.3, h), bar);
float spin = a * 6.2831853 - Time * Speed * 2.5;
vec2 q = vec2(cos(spin), sin(spin)) * r;
float star = 0.0;
for (int i = 0; i < 6; i++)
{
    float k = float(i) * 1.0471976;
    vec2 d = vec2(cos(k), sin(k));
    star += 1.0 - smoothstep(0.0, 0.01, abs(dot(q, vec2(-d.y, d.x))));
}
star *= step(r, 0.43) * step(0.12, r);
float core = 1.0 - smoothstep(0.0, 0.1, r);
float pulse = 0.65 + 0.35 * sin(Time * 2.2 - r * 9.0);
Mask = clamp(ring + glyph + star * 0.8 + core, 0.0, 1.0) * step(r, 1.0);
Glow = Mask * pulse;
"""


def rune_circle():
    """A carved rune circle: rings, a turning band of glyphs and a six-pointed star, pulsing outwards."""
    g = Graph("Decal")
    glow = g.prop("Glow Color", "Vec3", [0.25, 1.0, 0.8], color=True, hdr=True)
    intensity = g.prop("Glow Intensity", "Float", 8.0, rng=(0, 40))
    speed = g.prop("Turn Speed", "Float", 0.015, rng=(-0.2, 0.2))
    carve = g.prop("Carving Color", "Vec3", [0.05, 0.05, 0.045], color=True)

    rune = g.custom("RuneRing", [("UV", "Vec2"), ("Time", "Float"), ("Speed", "Float")], [("Mask", "Float"), ("Glow", "Float")],
                    RUNE_CODE, {"UV": g.node("UV"), "Time": g.time()["Time"], "Speed": speed})
    fade = g.node("Decal")["Fade"]
    g.outputs(Base_Color=carve, Alpha=g.mul(rune["Mask"], fade), Roughness=0.6,
              Emission=g.mul(g.mul(glow, rune["Glow"]), intensity))
    return g


CAUSTICS_CODE = """
vec2 p = mod(Position * 6.2831853, vec2_splat(6.2831853)) - vec2_splat(250.0);
vec2 i = p;
float c = 1.0;
float strength = 0.005;
for (int n = 0; n < 4; n++)
{
    float t = Time * (1.0 - (3.5 / float(n + 1)));
    i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
    c += 1.0 / length(vec2(p.x / (sin(i.x + t) / strength), p.y / (cos(i.y + t) / strength)));
}
c /= 4.0;
c = 1.17 - pow(c, 1.4);
Light = pow(abs(c), 8.0);
"""


def caustics():
    """Sunlight focused by the ripples, dancing on the pool bed and the stones at the waterline."""
    g = Graph("Decal")
    color = g.prop("Caustic Color", "Vec3", [1.0, 0.85, 0.6], color=True, hdr=True)
    intensity = g.prop("Intensity", "Float", 2.5, rng=(0, 20))
    scale = g.prop("Scale", "Float", 0.35, rng=(0.01, 4))
    speed = g.prop("Speed", "Float", 0.4, rng=(0, 4))

    ground = g.mul(g.swizzle(g.position("World"), "xz"), scale)
    pattern = g.custom("Caustics", [("Position", "Vec2"), ("Time", "Float")], [("Light", "Float")],
                       CAUSTICS_CODE, {"Position": ground, "Time": g.mul(g.time()["Time"], speed)})
    decal = g.node("Decal")
    # A round pool: fade out towards the edge of the (square) projection box.
    rim = g.one_minus(g.smooth(0.36, 0.5, g.node("Length", {"In": g.swizzle(decal["Box Position"], "xy")})))
    light = g.mul(g.mul(pattern["Light"], decal["Fade"]), rim)
    g.outputs(Base_Color=[0, 0, 0], Alpha=g.sat(g.mul(light, 1.6)), Roughness=0.3,
              Emission=g.mul(g.mul(color, light), intensity))
    return g


def spirit_wisp():
    """Glowing spirit wisps: a hot core inside a swirling, noise-torn halo, tinted by the particle colour."""
    g = Graph("Particle", Surface="Transparent")
    swirl = g.prop("Swirl Speed", "Float", 0.35, rng=(0, 3))
    core_size = g.prop("Core Tightness", "Float", 14.0, rng=(1, 60))

    particle = g.node("Particle")
    quad = particle["Quad UV"]
    r = g.mul(g.node("Length", {"In": g.sub(quad, [0.5, 0.5])}), 2.0)
    core = g.node("Exponential", {"In": g.node("Negate", {"In": g.mul(g.node("Square", {"In": r}), core_size)})})
    polar = g.node("PolarCoordinates", {"UV": quad})
    swirled = g.add(polar, g.combine(g.mul(g.time()["Time"], g.mul(swirl, -0.6)), g.mul(g.time()["Time"], swirl))["RG"])
    halo = g.mul(g.smooth(0.4, 0.85, g.node("GradientNoise", {"UV": swirled, "Scale": 5.0})), g.one_minus(g.smooth(0.15, 1.0, r)))
    tint = g.split(particle["Color"])
    glow = g.add(g.mul(core, 3.0), g.mul(halo, 1.4))
    g.outputs(Color=g.mul(g.swizzle(particle["Color"], "xyz"), glow), Alpha=g.mul(g.sat(g.add(core, g.mul(halo, 0.6))), tint["A"]))
    return g


def flame():
    """Camp-fire flames: the flame texture torn by rising noise, hotter in the core."""
    g = Graph("Particle", Surface="Transparent")
    core_color = g.prop("Core Color", "Vec3", [1.0, 0.86, 0.5], color=True, hdr=True)
    edge_color = g.prop("Edge Color", "Vec3", [1.0, 0.28, 0.04], color=True, hdr=True)
    rise = g.prop("Rise Speed", "Float", 1.8, rng=(0, 6))

    particle = g.node("Particle")
    quad = particle["Quad UV"]
    noise = g.node("GradientNoise", {"UV": g.node("Panner", {"UV": quad, "Speed": g.combine(0.0, g.node("Negate", {"In": rise}))["RG"]}), "Scale": 4.5})
    torn = g.add(quad, g.mul(g.sub(noise, 0.5), [0.16, 0.08]))
    shape = g.sample(g.node("ParticleTexture"), torn)
    heat = g.smooth(0.25, 0.95, g.mul(shape["R"], g.one_minus(g.split(quad)["G"])))
    color = g.mul(g.lerp(edge_color, core_color, heat), g.swizzle(particle["Color"], "xyz"))
    alpha = g.mul(g.mul(shape["A"], g.split(particle["Color"])["A"]), g.node("Remap", {"In": noise, "In Min": 0.0, "In Max": 1.0, "Out Min": 0.55, "Out Max": 1.4}))
    g.outputs(Color=color, Alpha=g.sat(alpha))
    return g


BRIGHT_LIGHT_CODE = """
// Samples the frame on a coarse grid (sgSceneColor is the target's scene-colour lookup): the light
// above Threshold, its average colour and where on screen it sits. Fixed sample positions, so bright
// points never leave ghost copies.
vec3 sum = vec3_splat(0.0);
vec2 centre = vec2_splat(0.0);
float total = 0.0;
for (int y = 0; y < 4; y++)
{
    for (int x = 0; x < 6; x++)
    {
        vec2 uv = vec2((float(x) + 0.5) / 6.0, (float(y) + 0.5) / 4.0);
        vec3 c = sgSceneColor(uv);
        float l = max(dot(c, vec3(0.2126, 0.7152, 0.0722)) - Threshold, 0.0);
        sum += c * l;
        centre += uv * l;
        total += l;
    }
}
Light = sum / (24.0 * max(Threshold, 0.05));
Centre = total > 0.0001 ? centre / total : vec2_splat(0.5);
"""


def lens_dirt():
    """Before tonemapping: light from the frame's brightest region catching on a dirty lens (strongest
    around that region), plus a touch of chromatic fringing towards the edges."""
    g = Graph("PostProcess", Injection="BeforeTonemap")
    dirt_tex = g.prop("Lens Dirt", "Texture2D", texture=LENS_DIRT, fallback="black")
    intensity = g.prop("Dirt Intensity", "Float", 0.35, rng=(0, 4))
    threshold = g.prop("Threshold", "Float", 1.5, rng=(0, 10))
    fringe = g.prop("Fringe", "Float", 0.0025, rng=(0, 0.02))
    focus = g.prop("Glow Focus", "Float", 5.0, rng=(0, 30))

    uv = g.node("ScreenPosition")["UV"]
    shift = g.mul(g.sub(uv, [0.5, 0.5]), fringe)
    red = g.split(g.node("SceneColor", {"UV": g.add(uv, shift)}))["R"]
    blue = g.split(g.node("SceneColor", {"UV": g.sub(uv, shift)}))["B"]
    green = g.split(g.node("SceneColor", {"UV": uv}))["G"]
    scene = g.combine(red, green, blue)["RGB"]

    bright = g.custom("BrightLight", [("Threshold", "Float")], [("Light", "Vec3"), ("Centre", "Vec2")], BRIGHT_LIGHT_CODE,
                      {"Threshold": threshold})
    away = g.mul(g.sub(uv, bright["Centre"]), [1.78, 1.0])
    near = g.node("Exponential", {"In": g.node("Negate", {"In": g.mul(g.node("DotProduct", {"A": away, "B": away}), focus)})})
    dirt = g.sample(dirt_tex, uv)["RGB"]
    glow = g.mul(bright["Light"], g.mul(g.add(near, 0.25), intensity))
    g.outputs(Color=g.add(scene, g.mul(dirt, glow)))
    return g


GRAPHS = {
    "AncientStone": ancient_stone,
    "JungleFloor": jungle_floor,
    "TempleWater": temple_water,
    "Waterfall": waterfall,
    "IdolGold": idol_gold,
    "Foliage": foliage,
    "FoliageCutout": lambda: foliage(cutout=True),
    "GlowMushroom": glow_mushroom,
    "SpiritBeam": spirit_beam,
    "RuneCircle": rune_circle,
    "Caustics": caustics,
    "SpiritWisp": spirit_wisp,
    "Flame": flame,
    "LensDirt": lens_dirt,
}
