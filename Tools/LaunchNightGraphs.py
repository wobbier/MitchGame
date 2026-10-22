"""Shader graphs for the Launch Night office scene (see Assets/Scenes/LaunchNight.md).

Imported by BuildLaunchNight.py; each entry of GRAPHS returns a graph document. Built with the
graph DSL from LostTempleGraphs.py. Screens and signs print their text with PixelFont, a 5x7 font
compiled into Custom Function code, so the words are part of the graph and need no textures.

Text graphs read UV with v = 0 at the top. Every screen graph has a `UV Rect` (the part of the
mesh's UVs that is the screen) and `Flip` (mirror u/v), so one graph fits any monitor model.
"""
from LostTempleGraphs import Graph
import PixelFont

OFFICE = "Assets/Models/Synty/OfficePack/Textures/"
ATLAS = OFFICE + "PolygonOffice_Texture_01_A.png"
ARCADE = OFFICE + "PolygonOffice_Texture_Sceen_Arcade_01.png"


def screen_uv(g):
    """The mesh UV remapped to the screen: UV Rect (u0, v0, u1, v1) to 0..1, then mirrored by Flip."""
    rect = g.prop("UV Rect", "Vec4", [0.0, 0.0, 1.0, 1.0])
    flip = g.prop("Flip", "Vec2", [0.0, 0.0], rng=(0, 1))
    lo = g.swizzle(rect, "xy")
    hi = g.swizzle(rect, "zw")
    uv = g.node("Divide", {"A": g.sub(g.node("UV"), lo), "B": g.sub(hi, lo)})
    return g.lerp(uv, g.sub([1.0, 1.0], uv), flip)


def inside(g, uv):
    """1 inside the 0..1 screen square, 0 outside (bezels keep their dark material)."""
    s = g.split(uv)
    return g.mul(g.mul(g.node("Step", {"A": 0.0, "B": s["R"]}), g.node("Step", {"A": s["R"], "B": 1.0})),
                 g.mul(g.node("Step", {"A": 0.0, "B": s["G"]}), g.node("Step", {"A": s["G"], "B": 1.0})))


def screen_finish(g, uv, emission, brightness):
    """CRT-ish scanlines and a darker rim, times the screen's brightness, as the Lit outputs."""
    rows = g.split(uv)["G"]
    scan = g.add(0.88, g.mul(g.sine(g.mul(rows, 900.0)), 0.12))
    rim = g.node("Remap", {"In": g.node("Length", {"In": g.sub(uv, [0.5, 0.5])}), "In Min": 0.35, "In Max": 0.75,
                           "Out Min": 1.0, "Out Max": 0.55})
    glow = g.mul(g.mul(emission, g.mul(scan, g.sat(rim))), g.mul(brightness, inside(g, uv)))
    # Occlusion keeps the night sky's image-based reflection off the glass (there are no indoor probes).
    g.outputs(Base_Color=[0.01, 0.01, 0.012], Roughness=0.3, Metallic=0.0, Emission=glow, Occlusion=0.12)


def text_screen(g, lines, inputs=(("UV", "Vec2"),), ins=None, aspect=1.0, dots=False, name="Text"):
    """A Custom Function printing lines (see PixelFont.text_function); returns the node (Mask1..3)."""
    code = PixelFont.text_function(lines, aspect=aspect, uv="UV", dots=dots)
    return g.custom(name, list(inputs), [("Mask1", "Float"), ("Mask2", "Float"), ("Mask3", "Float")], code, ins)


def layered(g, masks, colors):
    """Sum of mask * colour for the text layers."""
    total = None
    for mask, color in zip(masks, colors):
        term = g.mul(mask, g.color(color, hdr=True))
        total = term if total is None else g.add(total, term)
    return total


# ---------------------------------------------------------------------------------------------
# Screens

CODE_LINES = """
float rows = 26.0;
float yy = UV.y * rows + Time * Speed;
float row = floor(yy);
float fy = fract(yy);
float h = fract(sin(row * 12.9898 + Seed * 78.233) * 43758.5453);
float h2 = fract(sin(row * 39.346 + Seed * 11.135) * 24634.6345);
float cols = 70.0;
float indent = floor(h2 * 4.0) * 2.0;
float gutter = UV.x * cols;
float cx = gutter - 4.0 - indent;
float c = floor(cx);
float fx = fract(cx);
float len = floor(6.0 + h * 44.0);
float hc = fract(sin((c + row * 97.0) * 7.31 + Seed) * 9137.17);
float word = floor((c + floor(h * 7.0)) / 5.0);
float hw = fract(sin((word + row * 31.0) * 3.17 + Seed * 1.7) * 5131.7);
float blank = step(h, 0.1);
float ink = step(0.0, c) * step(c, len) * step(0.15, hc) * (1.0 - blank);
float glyph = step(0.2, fy) * step(fy, 0.76) * step(0.12, fx) * step(fx, 0.88);
vec3 col = vec3(0.82, 0.85, 0.9);
if (hw < 0.2) col = vec3(0.78, 0.45, 0.98);
else if (hw < 0.34) col = vec3(1.0, 0.62, 0.3);
else if (hw < 0.52) col = vec3(0.36, 0.68, 1.0);
if (h2 > 0.86) col = vec3(0.4, 0.75, 0.38);
float numbers = step(gutter, 2.6) * step(0.4, fract(sin(row * 3.3) * 91.7)) * glyph;
float cursor = step(abs(UV.y - 0.93), 0.016) * step(abs(UV.x - (0.06 + fract(Time * 0.37 + Seed) * 0.5)), 0.008) * step(0.5, fract(Time * 1.6));
Color = col * ink * glyph + vec3(0.25, 0.27, 0.32) * numbers + vec3(0.9, 0.9, 0.9) * cursor;
"""


def code_screen():
    """An IDE scrolling code: syntax-coloured token runs, line numbers and a blinking cursor."""
    g = Graph("Lit")
    speed = g.prop("Scroll Speed", "Float", 0.6, rng=(0, 10))
    seed = g.prop("Seed", "Float", 0.0)
    brightness = g.prop("Brightness", "Float", 2.2, rng=(0, 20))
    background = g.prop("Background", "Vec3", [0.025, 0.03, 0.045], color=True)
    uv = screen_uv(g)
    code = g.custom("CodeLines", [("UV", "Vec2"), ("Time", "Float"), ("Speed", "Float"), ("Seed", "Float")], [("Color", "Vec3")],
                    CODE_LINES, {"UV": uv, "Time": g.time()["Time"], "Speed": speed, "Seed": seed})
    screen_finish(g, uv, g.add(code["Color"], background), brightness)
    return g


def countdown_board():
    """The gold-master countdown: red LED matrix digits ticking down from Start Seconds."""
    g = Graph("Lit")
    start = g.prop("Start Seconds", "Float", 767.0)
    brightness = g.prop("Brightness", "Float", 6.0, rng=(0, 40))
    uv = screen_uv(g)
    remaining = "max(Start - Time, 0.0)"
    digits = [("digit", "%s / 36000.0" % remaining), ("digit", "mod(%s / 3600.0, 10.0)" % remaining), ":",
              ("digit", "mod(%s, 3600.0) / 600.0" % remaining), ("digit", "mod(mod(%s, 3600.0) / 60.0, 10.0)" % remaining), ":",
              ("digit", "mod(%s, 60.0) / 10.0" % remaining), ("digit", "mod(%s, 10.0)" % remaining)]
    aspect = 1.52
    label = "GOLD MASTER IN"
    lines = [(label, 0.5 - PixelFont.width(label, 0.1, aspect) / 2, 0.13, 0.1, 1),
             (digits, 0.5 - PixelFont.width("00:00:00", 0.19, aspect) / 2, 0.36, 0.19, 2),
             ("PROJECT MOONSHOT V1.0", 0.5 - PixelFont.width("PROJECT MOONSHOT V1.0", 0.07, aspect) / 2, 0.8, 0.07, 3)]
    text = text_screen(g, lines, [("UV", "Vec2"), ("Time", "Float"), ("Start", "Float")],
                       {"UV": uv, "Time": g.time()["Time"], "Start": start}, aspect=aspect, dots=True, name="Countdown")
    urgent = g.add(0.75, g.mul(g.node("Step", {"A": 0.5, "B": g.node("Fraction", {"In": g.time()["Time"]})}), 0.25))
    color = layered(g, [text["Mask1"], g.mul(text["Mask2"], urgent), text["Mask3"]],
                    [(1.0, 0.85, 0.7), (1.0, 0.08, 0.03), (1.0, 0.45, 0.1)])
    screen_finish(g, uv, g.add(color, g.color((0.012, 0.0015, 0.001))), brightness)
    return g


def build_status():
    """The CI dashboard on the hanging TV: build 4471 failed, and the build server is on fire."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 3.0, rng=(0, 40))
    uv = screen_uv(g)
    a = 1.52
    lines = [("MOONSHOT CI", 0.05, 0.06, 0.06, 1),
             ("BUILD #4471", 0.05, 0.16, 0.1, 1),
             ("FAILED", 0.05, 0.31, 0.2, 2),
             ("COMPILE", 0.05, 0.58, 0.06, 1), ("OK", 0.42, 0.58, 0.06, 3),
             ("COOK ASSETS", 0.05, 0.66, 0.06, 1), ("OK", 0.42, 0.66, 0.06, 3),
             ("UNIT TESTS", 0.05, 0.74, 0.06, 1), ("847 FAIL", 0.42, 0.74, 0.06, 2),
             ("BUILD AGENT", 0.05, 0.82, 0.06, 1), ("ON FIRE", 0.42, 0.82, 0.06, 2),
             ("LAST GREEN: 3 DAYS AGO", 0.05, 0.92, 0.045, 1),
             ("DAYS SINCE", 0.66, 0.2, 0.05, 1), ("LAST FIRE", 0.66, 0.27, 0.05, 1)]
    text = text_screen(g, lines, aspect=a, ins={"UV": uv}, name="BuildStatus")
    zero = text_screen(g, [("0", 0.73, 0.38, 0.32, 1)], aspect=a, ins={"UV": uv}, name="DaysSince")
    t = g.time()["Time"]
    flash = g.add(0.35, g.mul(g.node("Step", {"A": 0.45, "B": g.node("Fraction", {"In": g.mul(t, 0.9)})}), 0.65))
    # The status bars beside each step.
    s = g.split(uv)
    bar = g.mul(g.mul(g.node("Step", {"A": 0.62, "B": s["R"]}), g.node("Step", {"A": s["R"], "B": 0.95})),
                g.node("Step", {"A": 0.57, "B": s["G"]}))
    bar = g.mul(bar, g.node("Step", {"A": s["G"], "B": 0.88}))
    rows = g.node("Fraction", {"In": g.mul(g.sub(s["G"], 0.57), 12.5)})
    bar = g.mul(bar, g.node("Step", {"A": rows, "B": 0.7}))
    red_rows = g.node("Step", {"A": 0.72, "B": s["G"]})
    bar_color = g.lerp(g.color((0.1, 0.9, 0.3)), g.mul(g.color((1.0, 0.1, 0.05)), flash), red_rows)
    color = g.add(layered(g, [text["Mask1"], g.mul(text["Mask2"], flash), text["Mask3"]],
                          [(0.9, 0.92, 0.95), (1.0, 0.1, 0.04), (0.15, 1.0, 0.35)]),
                  g.add(g.mul(zero["Mask1"], g.color((1.0, 0.75, 0.1), hdr=True)), g.mul(bar, bar_color)))
    background = g.lerp(g.color((0.03, 0.035, 0.05)), g.color((0.12, 0.01, 0.01)), g.mul(flash, 0.5))
    screen_finish(g, uv, g.add(color, background), brightness)
    return g


def blue_screen():
    """The rage-quit monitor, face down on the carpet: a crash screen for the build."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 2.0, rng=(0, 20))
    uv = screen_uv(g)
    a = 1.6
    lines = [(":(", 0.08, 0.1, 0.26, 1),
             ("YOUR BUILD RAN INTO A PROBLEM AND", 0.08, 0.46, 0.05, 1),
             ("NEEDS TO RESTART. WE'RE JUST", 0.08, 0.53, 0.05, 1),
             ("COLLECTING SOME ERROR INFO.", 0.08, 0.6, 0.05, 1),
             ("4% COMPLETE", 0.08, 0.7, 0.05, 1),
             ("STOP CODE: SHIP_IT_ANYWAY", 0.08, 0.84, 0.04, 1)]
    text = text_screen(g, lines, aspect=a, ins={"UV": uv}, name="Crash")
    color = g.add(g.mul(text["Mask1"], g.color((1, 1, 1))), g.color((0.0, 0.22, 0.62)))
    screen_finish(g, uv, color, brightness)
    return g


def screensaver():
    """The sleeping developer's monitor: ZZZ bouncing round the screen, changing colour at each wall."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 2.5, rng=(0, 20))
    uv = screen_uv(g)
    a = 1.6
    code = """
float w = 0.33;
float hgt = 0.16;
float tx = Time * 0.083;
float ty = Time * 0.061;
vec2 o = vec2(abs(fract(tx) * 2.0 - 1.0) * (1.0 - w), abs(fract(ty) * 2.0 - 1.0) * (1.0 - hgt));
Local = UV - o;
float bounces = floor(tx * 2.0) + floor(ty * 2.0);
Tint = vec3_splat(0.5) + 0.5 * cos(6.2831853 * (bounces * 0.27 + vec3(0.0, 0.33, 0.67)));
"""
    bounce = g.custom("Bounce", [("UV", "Vec2"), ("Time", "Float")], [("Local", "Vec2"), ("Tint", "Vec3")], code,
                      {"UV": uv, "Time": g.time()["Time"]})
    text = text_screen(g, [("ZZZ...", 0.0, 0.0, 0.16, 1)], aspect=a, ins={"UV": bounce["Local"]}, name="Sleepy")
    screen_finish(g, uv, g.mul(text["Mask1"], g.mul(bounce["Tint"], 1.4)), brightness)
    return g


def compiling():
    """The beanbag laptop: shaders compiling since midnight, stuck at 99%."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 2.0, rng=(0, 20))
    uv = screen_uv(g)
    a = 1.6
    lines = [("> BUILD.SH --SHIP", 0.06, 0.1, 0.06, 1),
             ("COMPILING SHADERS", 0.06, 0.24, 0.07, 1),
             ("47391 / 47392", 0.06, 0.36, 0.07, 1),
             ("[", 0.06, 0.52, 0.08, 1), ("]", 0.85, 0.52, 0.08, 1), ("99%", 0.06, 0.66, 0.08, 1),
             ("ETA: 3 MINUTES", 0.06, 0.82, 0.06, 3)]
    text = text_screen(g, lines, aspect=a, ins={"UV": uv}, name="Compile")
    s = g.split(uv)
    t = g.time()["Time"]
    fill = g.add(0.84, g.mul(g.sine(g.mul(t, 0.31)), 0.003))
    bar = g.mul(g.mul(g.node("Step", {"A": 0.1, "B": s["R"]}), g.node("Step", {"A": s["R"], "B": fill})),
                g.mul(g.node("Step", {"A": 0.535, "B": s["G"]}), g.node("Step", {"A": s["G"], "B": 0.585})))
    blink = g.node("Step", {"A": 0.5, "B": g.node("Fraction", {"In": g.mul(t, 1.3)})})
    color = g.add(layered(g, [g.add(text["Mask1"], bar), g.mul(text["Mask3"], blink)], [(0.25, 1.0, 0.4), (0.8, 1.0, 0.85)]),
                  g.color((0.0, 0.02, 0.0)))
    screen_finish(g, uv, color, brightness)
    return g


CCTV_CODE = """
float t = Time;
float roll = fract(UV.y * 0.9 - t * 0.17);
float band = smoothstep(0.0, 0.05, roll) * (1.0 - smoothstep(0.05, 0.12, roll));
float n = fract(sin(dot(floor(UV * vec2(320.0, 240.0)) + floor(t * 24.0) * 1.37, vec2(12.9898, 78.233))) * 43758.5453);
float shade = 0.025 + 0.11 * smoothstep(1.0, 0.25, UV.y) + 0.04 * step(0.62, UV.y);
vec2 c = (UV - Hot) * vec2(1.6, 1.0);
float flicker = 0.75 + 0.25 * sin(t * 13.0) * sin(t * 7.3);
float flame = (exp(-dot(c, c) * 22.0) * 1.6 + exp(-dot(c, c) * 4.0) * 0.35) * flicker;
float rack = step(0.5, fract(UV.x * 9.0)) * step(0.3, UV.y) * step(UV.y, 0.8);
float leds = rack * step(0.82, fract(sin(dot(floor(UV * vec2(36.0, 40.0)), vec2(7.13, 3.71))) * 917.13)) * 0.22;
Gray = shade * (1.0 - rack * 0.6) + leds + n * 0.05 + band * 0.07;
Fire = flame * FireAmount;
Backing = FireAmount * step(0.19, UV.x) * step(UV.x, 0.81) * step(0.69, UV.y) * step(UV.y, 0.84);
"""


def cctv(camera, fire):
    """A security monitor: grainy feed with a rolling bar, the camera name, REC, a clock and an alarm."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 1.8, rng=(0, 20))
    uv = screen_uv(g)
    t = g.time()["Time"]
    feed = g.custom("Feed", [("UV", "Vec2"), ("Time", "Float"), ("Hot", "Vec2"), ("FireAmount", "Float")],
                    [("Gray", "Float"), ("Fire", "Float"), ("Backing", "Float")], CCTV_CODE,
                    {"UV": uv, "Time": t, "Hot": [0.62, 0.5], "FireAmount": 1.0 if fire else 0.0})
    a = 1.33
    clock = "(13632.0 + Time)"  # 03:47:12 when the scene starts
    stamp = [("digit", "mod(%s / 36000.0, 10.0)" % clock), ("digit", "mod(%s / 3600.0, 10.0)" % clock), ":",
             ("digit", "mod(%s, 3600.0) / 600.0" % clock), ("digit", "mod(mod(%s, 3600.0) / 60.0, 10.0)" % clock), ":",
             ("digit", "mod(%s, 60.0) / 10.0" % clock), ("digit", "mod(%s, 10.0)" % clock)]
    lines = [(camera, 0.05, 0.06, 0.06, 1), (stamp, 0.62, 0.06, 0.06, 1), ("REC", 0.12, 0.88, 0.06, 2)]
    if fire:
        lines.append(("! MOTION !", 0.5 - PixelFont.width("! MOTION !", 0.1, a) / 2, 0.72, 0.1, 3))
    text = text_screen(g, lines, [("UV", "Vec2"), ("Time", "Float")], {"UV": uv, "Time": t}, aspect=a, name="Overlay")
    blink = g.node("Step", {"A": 0.5, "B": g.node("Fraction", {"In": g.mul(t, 1.1)})})
    dot = g.mul(g.one_minus(g.smooth(0.012, 0.022, g.node("Length", {"In": g.mul(g.sub(uv, [0.075, 0.91]), [a, 1.0])}))), blink)
    gray = g.mul(g.combine(feed["Gray"], feed["Gray"], feed["Gray"])["RGB"], [0.8, 0.95, 0.85])
    fire_color = g.mul(feed["Fire"], g.color((2.4, 1.1, 0.3), hdr=True))
    # The feed goes dark behind the alarm text so it reads.
    picture = g.mul(g.add(gray, fire_color), g.one_minus(g.mul(feed["Backing"], 0.85)))
    color = g.add(picture, layered(g, [text["Mask1"], g.add(text["Mask2"], dot), g.mul(text["Mask3"], blink)],
                                                   [(0.9, 0.95, 0.9), (1.6, 0.12, 0.06), (2.6, 0.2, 0.1)]))
    screen_finish(g, uv, color, brightness)
    return g


SLIDE_CHART = """
vec2 p = (UV - vec2(0.52, 0.86)) / vec2(0.42, -0.5);
float axis = (step(abs(p.x), 0.006) + step(abs(p.y), 0.012)) * step(-0.02, p.x) * step(p.x, 1.0) * step(-0.02, p.y) * step(p.y, 1.0);
float curve = 0.06 + 0.02 * sin(p.x * 30.0) + pow(max(p.x - 0.55, 0.0) * 2.2, 3.0);
float stroke = 1.0 - smoothstep(0.012, 0.03, abs(p.y - curve));
stroke *= step(0.0, p.x) * step(p.x, 0.98);
float here = 1.0 - smoothstep(0.018, 0.03, length((p - vec2(0.2, 0.08)) * vec2(1.0, 0.8)));
float arrow = step(abs(p.x - 0.2), 0.008) * step(0.12, p.y) * step(p.y, 0.32);
Axes = clamp(axis, 0.0, 1.0);
Curve = stroke;
Here = max(here, arrow);
"""


def roadmap_slide():
    """The conference projector's slide: Q4's three-step plan and a hockey-stick chart."""
    g = Graph("Lit")
    brightness = g.prop("Brightness", "Float", 1.6, rng=(0, 20))
    uv = screen_uv(g)
    a = 1.04
    lines = [("Q4 ROADMAP", 0.07, 0.08, 0.09, 1),
             ("1. SHIP MOONSHOT", 0.07, 0.3, 0.045, 1),
             ("2. ???", 0.07, 0.4, 0.045, 1),
             ("3. PROFIT", 0.07, 0.5, 0.045, 1),
             ("4. SLEEP", 0.07, 0.6, 0.045, 3),
             ("WE ARE HERE", 0.53, 0.5, 0.03, 2),
             ("CONFIDENTIAL - DO NOT SHOW TEAM", 0.07, 0.93, 0.025, 1)]
    text = text_screen(g, lines, aspect=a, ins={"UV": uv}, name="Slide")
    chart = g.custom("Chart", [("UV", "Vec2")], [("Axes", "Float"), ("Curve", "Float"), ("Here", "Float")], SLIDE_CHART, {"UV": uv})
    s = g.split(uv)
    header = g.mul(g.node("Step", {"A": s["G"], "B": 0.21}), g.node("Step", {"A": 0.2, "B": s["G"]}))
    paper = g.color((0.92, 0.93, 0.95))
    ink = g.add(g.mul(g.add(text["Mask1"], chart["Axes"]), g.color((0.1, 0.16, 0.36))),
                g.mul(g.max(text["Mask2"], g.add(chart["Curve"], chart["Here"])), g.color((0.9, 0.12, 0.1))))
    ink = g.add(ink, g.mul(text["Mask3"], g.color((0.55, 0.55, 0.6))))
    coverage = g.sat(g.add(g.add(text["Mask1"], text["Mask2"]), g.add(g.add(text["Mask3"], chart["Axes"]), g.add(chart["Curve"], chart["Here"]))))
    color = g.add(g.mul(g.lerp(paper, g.color((0.1, 0.25, 0.6)), g.mul(header, 0.0)), g.one_minus(coverage)), ink)
    color = g.add(color, g.mul(header, g.color((0.0, 0.25, 0.65))))
    screen_finish(g, uv, color, brightness)
    return g


def arcade_screen():
    """The lounge arcade cabinet in attract mode: the Synty arcade screen, scrolling, with scanlines."""
    g = Graph("Lit")
    tex = g.prop("Screen", "Texture2D", texture=ARCADE)
    brightness = g.prop("Brightness", "Float", 2.5, rng=(0, 20))
    uv = g.node("UV")
    shake = g.node("Panner", {"UV": uv, "Speed": [0.0, 0.03]})
    image = g.sample(tex, shake)["RGB"]
    flicker = g.add(0.9, g.mul(g.sine(g.mul(g.time()["Time"], 37.0)), 0.06))
    scan = g.add(0.8, g.mul(g.sine(g.mul(g.split(uv)["G"], 1400.0)), 0.2))
    g.outputs(Base_Color=[0.02, 0.02, 0.02], Roughness=0.1, Emission=g.mul(g.mul(image, g.mul(scan, flicker)), brightness))
    return g


# ---------------------------------------------------------------------------------------------
# Surfaces

SERVER_LEDS = """
vec2 grid = vec2(6.0, 44.0);
vec2 gp = UV * grid;
vec2 cell = floor(gp);
vec2 fp = fract(gp) - vec2_splat(0.5);
float h = fract(sin(dot(cell + vec2_splat(Seed * 17.0), vec2(12.9898, 78.233))) * 43758.5453);
float h2 = fract(h * 91.7);
float rate = 0.4 + h2 * 7.0;
float on = step(0.4, fract(Time * rate + h * 7.0));
float led = 1.0 - smoothstep(0.16, 0.3, length(fp * vec2(1.0, 0.5)));
vec3 col = h < 0.55 ? vec3(0.1, 1.0, 0.3) : (h < 0.82 ? vec3(1.0, 0.55, 0.08) : vec3(0.2, 0.5, 1.0));
float present = step(0.3, fract(h * 13.1)) * step(0.06, UV.y) * step(UV.y, 0.94);
float strobe = step(0.5, fract(Time * 2.2 + h * 0.15));
col = mix(col, vec3(1.0, 0.04, 0.02), Alarm);
on = mix(on, strobe, Alarm * step(0.25, h2));
Color = col * led * on * present;
"""


def server_leds():
    """The front of a rack: rows of blinking status LEDs; Alarm turns them red and strobing."""
    g = Graph("Lit")
    seed = g.prop("Seed", "Float", 0.0)
    alarm = g.prop("Alarm", "Float", 0.0, rng=(0, 1))
    intensity = g.prop("Intensity", "Float", 6.0, rng=(0, 40))
    leds = g.custom("Leds", [("UV", "Vec2"), ("Time", "Float"), ("Seed", "Float"), ("Alarm", "Float")], [("Color", "Vec3")],
                    SERVER_LEDS, {"UV": g.node("UV"), "Time": g.time()["Time"], "Seed": seed, "Alarm": alarm})
    slots = g.mul(g.add(0.6, g.mul(g.node("Step", {"A": 0.5, "B": g.node("Fraction", {"In": g.mul(g.split(g.node("UV"))["G"], 44.0)})}), 0.4)), [0.04, 0.045, 0.05])
    g.outputs(Base_Color=slots, Metallic=0.6, Roughness=0.35, Emission=g.mul(leds["Color"], intensity))
    return g


RAIN_CODE = """
vec2 p = P * Scale;
float h = 0.0;
{
    vec2 uv = p * 22.0;
    vec2 id = floor(uv);
    vec2 fp = fract(uv) - vec2_splat(0.5);
    float n = fract(sin(dot(id, vec2(12.9898, 78.233))) * 43758.5453);
    vec2 o = vec2(fract(n * 13.1), fract(n * 71.7)) - vec2_splat(0.5);
    float r = 0.1 + 0.16 * fract(n * 7.3);
    float life = fract(Time * (0.05 + 0.1 * fract(n * 3.7)) + n);
    float d = length(fp - o * 0.5);
    h = max(h, (1.0 - smoothstep(r * 0.4, r, d)) * step(0.72, n) * smoothstep(1.0, 0.7, life));
}
{
    float cw = 0.16;
    float colx = floor(p.x / cw);
    float n = fract(sin(colx * 78.233 + 1.3) * 43758.5453);
    float x = (fract(p.x / cw) - 0.5) * cw + sin(p.y * 6.0 + n * 6.28) * 0.012;
    float s = p.y / 0.9 + Time * (0.18 + 0.3 * n) + n * 7.0;
    float cycle = floor(s);
    float dy = (fract(s) - 0.5) * 0.9;
    float m = fract(sin((cycle + colx * 13.0) * 12.9898) * 43758.5453);
    float head = 1.0 - smoothstep(0.008, 0.016, length(vec2(x, dy * 0.75)));
    float trailMask = step(0.0, dy) * (1.0 - smoothstep(0.0, 0.32, dy));
    float trail = (1.0 - smoothstep(0.002, 0.005, abs(x))) * trailMask;
    float bead = fract(dy * 26.0);
    float beads = (1.0 - smoothstep(0.003, 0.007, length(vec2(x, (bead - 0.5) / 26.0)))) * trailMask * step(0.45, fract(sin(floor(dy * 26.0) + m * 40.0) * 917.3));
    h = max(h, (head + max(trail * 0.35, beads * 0.8)) * step(0.3, m));
}
Height = h;
"""


def rain_glass():
    """Storm glass: beaded drops that come and go and drops running down with broken trails."""
    g = Graph("Lit", Surface="Transparent", Blend="Alpha", CastShadows=False, RenderFace="Both")
    tint = g.prop("Tint", "Vec3", [0.05, 0.07, 0.09], color=True)
    scale = g.prop("Scale", "Float", 1.0, rng=(0.1, 4))
    opacity = g.prop("Opacity", "Float", 0.1, rng=(0, 1))
    world = g.position("World")
    plane = g.combine(g.add(g.split(world)["R"], g.split(world)["B"]), g.split(world)["G"])["RG"]
    rain = g.custom("RainDrops", [("P", "Vec2"), ("Time", "Float"), ("Scale", "Float")], [("Height", "Float")], RAIN_CODE,
                    {"P": plane, "Time": g.time()["Time"], "Scale": scale})
    glint = g.prop("Drop Glint", "Vec3", [0.1, 0.11, 0.14], color=True, hdr=True)
    normal = g.node("NormalFromHeight", {"In": rain["Height"], "Strength": 0.8})
    # Drops refract the city behind them: approximate with a faint glow rather than darker glass.
    g.outputs(Base_Color=tint, Roughness=0.05, Metallic=0.0, Normal=normal, Emission=g.mul(glint, rain["Height"]),
              Alpha=g.sat(g.add(opacity, g.mul(rain["Height"], 0.12))))
    return g


CITY_CODE = """
vec3 an = abs(N);
vec2 uv = an.x > an.z ? P.zy : P.xy;
vec2 gp = uv / vec2(3.1, 3.5);
vec2 id = floor(gp);
vec2 fp = fract(gp);
float win = step(0.16, fp.x) * step(fp.x, 0.84) * step(0.22, fp.y) * step(fp.y, 0.84);
float n = fract(sin(dot(id + floor(P.xz * 0.05) * 13.0, vec2(12.9898, 78.233)) + floor(an.x * 1.5) * 3.1) * 43758.5453);
float lit = step(0.64, n);
float tv = step(0.64, n) * step(n, 0.67) * (0.5 + 0.5 * sin(Time * (3.0 + n * 9.0) + n * 40.0));
vec3 warm = vec3(1.0, 0.72, 0.42);
vec3 cool = vec3(0.6, 0.78, 1.0);
vec3 col = fract(n * 31.7) < 0.7 ? warm : cool;
col = mix(col, vec3(0.3, 0.5, 1.0), step(0.0001, tv));
float side = step(an.y, 0.5);
Emit = col * win * lit * side * (0.4 + 0.6 * fract(n * 17.3)) * (1.0 - 0.6 * tv);
Window = win * side;
"""


def city_windows():
    """Distant towers: a grid of windows on every wall, a third of them lit warm or cool, a few TVs."""
    g = Graph("Lit")
    facade = g.prop("Facade", "Vec3", [0.06, 0.065, 0.075], color=True)
    intensity = g.prop("Intensity", "Float", 4.0, rng=(0, 40))
    city = g.custom("City", [("P", "Vec3"), ("N", "Vec3"), ("Time", "Float")], [("Emit", "Vec3"), ("Window", "Float")], CITY_CODE,
                    {"P": g.position("World"), "N": g.normal("World"), "Time": g.time()["Time"]})
    g.outputs(Base_Color=g.lerp(facade, [0.02, 0.025, 0.035], city["Window"]), Roughness=g.lerp(0.8, 0.15, city["Window"]),
              Metallic=g.mul(city["Window"], 0.4), Emission=g.mul(city["Emit"], intensity))
    return g


def blink_light():
    """A small indicator (aircraft warning, smoke detector, REC): on for Duty of each 1/Rate seconds."""
    g = Graph("Lit")
    color = g.prop("Color", "Vec3", [1.0, 0.05, 0.02], color=True, hdr=True)
    intensity = g.prop("Intensity", "Float", 20.0, rng=(0, 200))
    rate = g.prop("Rate", "Float", 1.0, rng=(0, 10))
    duty = g.prop("Duty", "Float", 0.15, rng=(0, 1))
    phase = g.prop("Phase", "Float", 0.0, rng=(0, 1))
    cycle = g.node("Fraction", {"In": g.add(g.mul(g.time()["Time"], rate), phase)})
    on = g.node("Step", {"A": cycle, "B": duty})
    g.outputs(Base_Color=[0.05, 0.02, 0.02], Roughness=0.3, Emission=g.mul(g.mul(color, intensity), on))
    return g


NEON_CODE = """
float t = Time * Rate;
float k = floor(t);
float n = fract(sin(k * 12.9898 + Seed) * 43758.5453);
float drop = step(0.9, n) * step(fract(t), 0.35);
Buzz = (1.0 - drop * 0.85) * (0.94 + 0.06 * sin(Time * 120.0));
"""


def neon():
    """Neon tube on the atlas: the bright, saturated parts glow and buzz, dropping out now and then."""
    g = Graph("Lit")
    atlas = g.prop("Albedo", "Texture2D", texture=ATLAS)
    color = g.prop("Neon Color", "Vec3", [0.3, 1.0, 0.35], color=True, hdr=True)
    intensity = g.prop("Intensity", "Float", 8.0, rng=(0, 60))
    rate = g.prop("Flicker Rate", "Float", 3.0, rng=(0, 20))
    seed = g.prop("Seed", "Float", 0.0)
    texel = g.sample(atlas)["RGB"]
    rgb = g.split(texel)
    saturation = g.sub(g.max(g.max(rgb["R"], rgb["G"]), rgb["B"]), g.node("Minimum", {"A": g.node("Minimum", {"A": rgb["R"], "B": rgb["G"]}), "B": rgb["B"]}))
    tube = g.smooth(0.25, 0.45, saturation)
    buzz = g.custom("Buzz", [("Time", "Float"), ("Rate", "Float"), ("Seed", "Float")], [("Buzz", "Float")], NEON_CODE,
                    {"Time": g.time()["Time"], "Rate": rate, "Seed": seed})
    g.outputs(Base_Color=texel, Roughness=0.35, Emission=g.mul(g.mul(color, g.mul(tube, buzz["Buzz"])), intensity))
    return g


def fish_tank_water():
    """The water in the fish tank: teal, a little murky, light rippling across it."""
    g = Graph("Lit", Surface="Transparent", Blend="Alpha", CastShadows=False)
    deep = g.prop("Water Color", "Vec3", [0.02, 0.22, 0.25], color=True)
    glow = g.prop("Glow", "Float", 0.6, rng=(0, 10))
    world = g.position("World")
    uv = g.add(g.swizzle(world, "xy"), g.swizzle(world, "zz"))
    ripple = g.node("GradientNoise", {"UV": g.node("Panner", {"UV": g.mul(uv, 3.0), "Speed": [0.08, -0.12]}), "Scale": 6.0})
    light = g.mul(g.node("Power", {"A": ripple, "B": 3.0}), glow)
    fresnel = g.node("FresnelEffect", {"Power": 3.0})
    g.outputs(Base_Color=deep, Roughness=0.05, Emission=g.mul(g.color((0.25, 0.85, 0.9)), light),
              Alpha=g.lerp(0.38, 0.8, fresnel))
    return g


FLOOD_CODE = """
float h = 0.0;
vec2 g = World * 1.6;
for (int i = 0; i < 2; i++)
{
    vec2 id = floor(g + vec2_splat(float(i) * 0.5));
    vec2 fp = fract(g + vec2_splat(float(i) * 0.5)) - vec2_splat(0.5);
    float n = fract(sin(dot(id, vec2(12.9898, 78.233)) + float(i) * 7.1) * 43758.5453);
    float life = fract(Time * 0.9 + n);
    vec2 o = vec2(fract(n * 13.1), fract(n * 71.7)) * 0.5 - vec2_splat(0.25);
    float d = length(fp - o);
    float ring = sin((d - life * 0.45) * 70.0) * (1.0 - smoothstep(0.0, 0.06, abs(d - life * 0.45)));
    h += ring * (1.0 - life) * step(0.25, n);
}
Ripple = h * 0.5 + 0.5;
"""


def flood_water():
    """A decal of standing water, ragged at the edge, rippled by drips (Ripples > 0 under the sprinklers)."""
    g = Graph("Decal")
    color = g.prop("Water Color", "Vec3", [0.015, 0.016, 0.018], color=True)
    ripples = g.prop("Ripples", "Float", 1.0, rng=(0, 1))
    edge = g.prop("Edge Noise", "Float", 0.35, rng=(0, 1))
    decal = g.node("Decal")
    box = g.mul(g.swizzle(decal["Box Position"], "xy"), 2.0)
    world = g.swizzle(g.position("World"), "xz")
    rough_edge = g.mul(g.sub(g.node("FractalNoise", {"UV": world, "Scale": 0.9, "Octaves": 4.0}), 0.5), edge)
    r = g.add(g.node("Length", {"In": box}), rough_edge)
    coverage = g.one_minus(g.smooth(0.72, 0.9, r))
    wave = g.custom("Drips", [("World", "Vec2"), ("Time", "Float")], [("Ripple", "Float")], FLOOD_CODE,
                    {"World": world, "Time": g.time()["Time"]})
    normal = g.node("NormalFromHeight", {"In": g.mul(wave["Ripple"], ripples), "Strength": 0.25})
    g.outputs(Base_Color=color, Alpha=g.mul(g.mul(coverage, decal["Fade"]), 0.92), Roughness=0.03, Metallic=0.0, Normal=normal)
    return g


WHITEBOARD_CODE = """
vec2 p = UV + vec2(sin(UV.y * 40.0) * 0.002, sin(UV.x * 37.0) * 0.002);
float tally = 0.0;
for (int i = 0; i < 47; i++)
{
    float fi = float(i);
    float group = floor(fi / 5.0);
    float k = mod(fi, 5.0);
    vec2 o = vec2(0.06 + mod(group, 5.0) * 0.105 + k * 0.016, 0.55 + floor(group / 5.0) * 0.14);
    float wob = sin(fi * 7.1) * 0.004;
    if (k < 3.5)
    {
        float stroke = step(abs(p.x - o.x - (p.y - o.y) * 0.08 - wob), 0.0035) * step(o.y, p.y) * step(p.y, o.y + 0.1);
        tally = max(tally, stroke);
    }
    else
    {
        vec2 a = vec2(o.x - 0.07, o.y + 0.08);
        vec2 b = vec2(o.x + 0.005, o.y + 0.02);
        vec2 pa = p - a;
        vec2 ba = b - a;
        float t = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
        tally = max(tally, step(length(pa - ba * t), 0.0035));
    }
}
Tally = tally;
"""


def whiteboard():
    """Marker on the war-room whiteboard: the crunch tally, the bug count and a prophetic warning."""
    g = Graph("Decal")
    uv = g.node("UV")
    lines = [("SHIP IT!!!", 0.05, 0.07, 0.095, 2),
             ("DAYS OF CRUNCH", 0.05, 0.43, 0.06, 1),
             ("BUGS:", 0.67, 0.08, 0.06, 2),
             ("847", 0.67, 0.17, 0.11, 2),
             ("DO NOT TOUCH", 0.64, 0.52, 0.035, 3),
             ("THE BUILD SERVER", 0.64, 0.58, 0.035, 3),
             ("(IT'S FINE)", 0.64, 0.64, 0.035, 3)]
    text = text_screen(g, lines, aspect=1.47, ins={"UV": uv}, name="Marker")
    tally = g.custom("Tally", [("UV", "Vec2")], [("Tally", "Float")], WHITEBOARD_CODE, {"UV": uv})
    blue = g.add(text["Mask1"], tally["Tally"])
    color = g.add(g.add(g.mul(blue, g.color((0.05, 0.15, 0.6))), g.mul(text["Mask2"], g.color((0.75, 0.05, 0.05)))),
                  g.mul(text["Mask3"], g.color((0.05, 0.4, 0.15))))
    alpha = g.sat(g.add(g.add(blue, text["Mask2"]), text["Mask3"]))
    g.outputs(Base_Color=color, Alpha=g.mul(alpha, g.node("Decal")["Fade"]), Roughness=0.4)
    return g


# ---------------------------------------------------------------------------------------------
# Effects

LIGHTNING_CODE = """
float y = UV.y;
float path = 0.0;
float amp = 0.16;
float freq = 3.0;
for (int i = 0; i < 5; i++)
{
    float fi = float(i);
    float k = y * freq + Seed * (fi + 1.0) * 1.7;
    float a = fract(sin(floor(k) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    float b = fract(sin((floor(k) + 1.0) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    path += mix(a, b, fract(k)) * amp;
    amp *= 0.5;
    freq *= 2.3;
}
float d = abs(UV.x - 0.5 - path);
float branchY = clamp((y - 0.35) / 0.3, 0.0, 1.0);
float branch = abs(UV.x - 0.5 - path - branchY * 0.12 - sin(y * 47.0 + Seed) * 0.01);
branch = (1.0 - smoothstep(0.0, 0.004, branch)) * step(0.35, y) * step(y, 0.65) * (1.0 - branchY);
float core = 1.0 - smoothstep(0.0, 0.005, d);
float halo = exp(-d * 45.0) * 0.45;
float ends = smoothstep(0.0, 0.04, y) * smoothstep(1.0, 0.94, y);
float flick = 0.55 + 0.45 * step(0.4, fract(Time * 19.0));
Glow = (core + halo + branch) * ends * flick;
"""


def lightning():
    """A forked bolt on a tall card (scaled to zero between flashes by the Storm sequence)."""
    g = Graph("Unlit", Surface="Transparent", Blend="Additive", RenderFace="Both", CastShadows=False)
    color = g.prop("Bolt Color", "Vec3", [0.75, 0.82, 1.0], color=True, hdr=True)
    intensity = g.prop("Intensity", "Float", 60.0, rng=(0, 400))
    seed = g.prop("Seed", "Float", 3.0)
    bolt = g.custom("Bolt", [("UV", "Vec2"), ("Time", "Float"), ("Seed", "Float")], [("Glow", "Float")], LIGHTNING_CODE,
                    {"UV": g.node("UV"), "Time": g.time()["Time"], "Seed": seed})
    glow = g.mul(bolt["Glow"], intensity)
    g.outputs(Color=g.mul(color, glow), Alpha=g.sat(glow))
    return g


def paper_sheet():
    """A sheet of printed paper for the photocopier's spew and the resignation letters."""
    g = Graph("Particle", Surface="Transparent")
    particle = g.node("Particle")
    quad = g.split(particle["Quad UV"])
    sheet = g.mul(g.mul(g.node("Step", {"A": 0.18, "B": quad["R"]}), g.node("Step", {"A": quad["R"], "B": 0.82})),
                  g.mul(g.node("Step", {"A": 0.08, "B": quad["G"]}), g.node("Step", {"A": quad["G"], "B": 0.92})))
    rows = g.node("Fraction", {"In": g.mul(quad["G"], 22.0)})
    printed = g.mul(g.mul(g.node("Step", {"A": 0.62, "B": rows}), g.node("Step", {"A": 0.16, "B": quad["G"]})),
                    g.mul(g.node("Step", {"A": quad["G"], "B": 0.72}), g.mul(g.node("Step", {"A": 0.26, "B": quad["R"]}), g.node("Step", {"A": quad["R"], "B": 0.74}))))
    shade = g.sub(1.0, g.mul(printed, 0.55))
    color = g.mul(g.swizzle(particle["Color"], "xyz"), shade)
    g.outputs(Color=color, Alpha=g.mul(sheet, g.split(particle["Color"])["A"]))
    return g


POST_CODE = """
float n = fract(sin(dot(floor(UV * vec2(960.0, 540.0)) + vec2_splat(fract(Time * 7.0) * 113.0), vec2(12.9898, 78.233))) * 43758.5453);
vec2 c = UV - vec2_splat(0.5);
float edge = smoothstep(0.25, 0.75, length(c * vec2(1.3, 1.0)));
float pulse = 0.5 + 0.5 * sin(Time * 4.4);
Grain = (n - 0.5);
Alarm = edge * pulse * pulse;
"""


def night_shift():
    """After tonemapping: film grain, a hint of chromatic fringing and a red alarm pulse at the edges."""
    g = Graph("PostProcess", Injection="AfterTonemap")
    grain_amount = g.prop("Grain", "Float", 0.035, rng=(0, 0.3))
    fringe = g.prop("Fringe", "Float", 0.0025, rng=(0, 0.02))
    alarm_amount = g.prop("Alarm", "Float", 0.06, rng=(0, 1))
    uv = g.node("ScreenPosition")["UV"]
    shift = g.mul(g.sub(uv, [0.5, 0.5]), fringe)
    red = g.split(g.node("SceneColor", {"UV": g.add(uv, shift)}))["R"]
    green = g.split(g.node("SceneColor", {"UV": uv}))["G"]
    blue = g.split(g.node("SceneColor", {"UV": g.sub(uv, shift)}))["B"]
    scene = g.combine(red, green, blue)["RGB"]
    fx = g.custom("NightShift", [("UV", "Vec2"), ("Time", "Float")], [("Grain", "Float"), ("Alarm", "Float")], POST_CODE,
                  {"UV": uv, "Time": g.time()["Time"]})
    alarm = g.mul(g.mul(fx["Alarm"], alarm_amount), [1.0, 0.05, 0.02])
    g.outputs(Color=g.add(g.add(scene, g.mul(fx["Grain"], grain_amount)), alarm))
    return g


GRAPHS = {
    "CodeScreen": code_screen,
    "Countdown": countdown_board,
    "BuildStatus": build_status,
    "BlueScreen": blue_screen,
    "Screensaver": screensaver,
    "Compiling": compiling,
    "CCTVServerRoom": lambda: cctv("CAM 04 SERVER RM", True),
    "CCTVLobby": lambda: cctv("CAM 01 LOBBY", False),
    "RoadmapSlide": roadmap_slide,
    "ArcadeScreen": arcade_screen,
    "ServerLEDs": server_leds,
    "RainGlass": rain_glass,
    "CityWindows": city_windows,
    "BlinkLight": blink_light,
    "Neon": neon,
    "FishTankWater": fish_tank_water,
    "FloodWater": flood_water,
    "Whiteboard": whiteboard,
    "Lightning": lightning,
    "PaperSheet": paper_sheet,
    "NightShift": night_shift,
}
