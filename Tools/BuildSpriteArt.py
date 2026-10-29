#!/usr/bin/env python3
"""Writes the 2D sprite art under Assets/Textures/Sprites/ (LOOK-S2), drawn procedurally so it
stays reproducible: a crate, a ball, a plank, a stone tile with 9-slice borders, a windmill blade,
a sky gradient, a 4-frame coin strip (sliced by Coins.spritesheet) and a 6-frame character
(Hero.spritesheet: idle and walk, animated by Hero_Idle / Hero_Walk .spriteanim clips), plus
normal maps for the crate and the stone (from height fields) for lit sprites (LOOK-S9). RGBA PNGs; run from the project root:  python3 Tools/BuildSpriteArt.py
"""
import math
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Assets/Textures/Sprites")


def write_png(path, width, height, pixel):
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            r, g, b, a = pixel(x, y)
            rows += bytes((max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))), max(0, min(255, int(a)))))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(rows), 9)))
        f.write(chunk(b"IEND", b""))
    print("wrote", os.path.relpath(path, ROOT))


def noise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xff) / 255.0


def crate(x, y):
    # 64 x 64: a light frame, darker boards, a diagonal brace; neutral so a tint colours it.
    edge = min(x, y, 63 - x, 63 - y)
    grain = 0.9 + 0.1 * noise(x // 2, y, 1)
    if edge < 6:
        v = 235 if edge > 0 else 120
    elif abs((x - 6) - (y - 6)) < 4 and 6 <= x < 58:
        v = 225
    else:
        v = 170 + (20 if (y // 13) % 2 else 0)
        if (y - 6) % 13 == 0:
            v = 120
    v *= grain
    return (v, v * 0.97, v * 0.92, 255)


def ball(x, y):
    # 64 x 64: a shaded disc with an antialiased edge, lit from the top left.
    cx, cy, r = 31.5, 31.5, 30.5
    d = math.hypot(x - cx, y - cy)
    alpha = max(0.0, min(1.0, r - d + 0.5))
    nx, ny = (x - cx) / r, (y - cy) / r
    nz = math.sqrt(max(0.0, 1.0 - nx * nx - ny * ny))
    light = max(0.0, -0.5 * nx - 0.6 * ny + 0.62 * nz)
    v = 90 + 165 * light
    spec = max(0.0, (-0.35 * nx - 0.45 * ny + 0.82 * nz)) ** 30 * 120
    return (v + spec, v + spec, v + spec, 255 * alpha)


def plank(x, y):
    # 64 x 16: a board with grain and dark ends.
    grain = 0.85 + 0.15 * noise(x // 4, y, 2)
    v = (200 if 2 <= y < 14 else 140) * grain
    if x < 2 or x > 61:
        v = 120
    if x in (6, 57) and 6 <= y <= 9:
        v = 80   # nails
    return (v, v * 0.95, v * 0.88, 255)


def stone(x, y):
    # 48 x 48 with a 12-texel border (9-slice): a bevelled rim around a cobbled middle.
    edge = min(x, y, 47 - x, 47 - y)
    if edge < 12:
        v = 200 - edge * 4 if edge > 1 else 90
        v *= 0.92 + 0.08 * noise(x, y, 3)
    else:
        cell = ((x - 12) // 8 + (y - 12) // 8) % 2
        v = (150 if cell else 135) * (0.9 + 0.1 * noise(x // 2, y // 2, 4))
        if (x - 12) % 8 == 0 or (y - 12) % 8 == 0:
            v = 105
    return (v, v * 0.97, v * 0.93, 255)


def blade(x, y):
    # 128 x 16: a tapered blade with a rounded hub in the middle.
    cx, cy = 63.5, 7.5
    if math.hypot(x - cx, y - cy) < 7.5:
        v = 120 if math.hypot(x - cx, y - cy) < 3 else 230
        return (v, v, v, 255)
    half = 7.5 - abs(x - cx) / 64 * 3.5
    inside = abs(y - cy) <= half
    v = 210 - abs(y - cy) * 6
    return (v, v, v, 255 if inside else 0)


def sky(x, y):
    # 4 x 64: a vertical gradient, light at the horizon (the bottom).
    t = y / 63.0
    return (60 + 120 * t, 90 + 110 * t, 150 + 80 * t, 255)


def coins(x, y):
    # 64 x 16: four 16 x 16 frames of a spinning coin (a sprite sheet: Coins.spritesheet slices it),
    # each narrower than the last, on transparent texels.
    frame, fx = x // 16, x % 16
    half_width = (7.0, 5.0, 2.5, 1.0)[frame]
    dx, dy = (fx - 7.5) / half_width, (y - 7.5) / 7.0
    inside = dx * dx + dy * dy <= 1.0
    if not inside:
        return (0, 0, 0, 0)
    rim = dx * dx + dy * dy > 0.6
    v = 200 if rim else 245
    return (v, v * 0.8, 60, 255)


def hero(x, y):
    # 144 x 24: six 24 x 24 frames of a little character (Hero.spritesheet): two idle frames (a
    # breathing bob) then four walk frames (legs and arms swinging). Top-down rows: y 0 is the top.
    frame, fx = x // 24, x % 24
    bob = 1 if frame == 1 else 0
    swing = (0, 0, 3, 0, -3, 0)[frame]
    lift = (0, 0, 0, 1, 0, 1)[frame]
    skin, shirt, trousers, boots, hair = (240, 196, 160), (60, 110, 210), (50, 50, 70), (90, 60, 40), (70, 45, 30)
    # Head (rows 3-9), hair on top.
    if (fx - 12) ** 2 + (y - 6 - bob) ** 2 <= 10:
        return hair + (255,) if y - bob <= 4 else skin + (255,)
    # Body (rows 10-16) with arms swinging.
    if 9 <= fx <= 15 and 10 + bob <= y <= 16:
        return shirt + (255,)
    if 10 + bob <= y <= 15 and (fx == 8 - (swing > 0) or fx == 16 + (swing < 0)):
        return skin + (255,)
    # Legs (rows 17-22): apart by the swing, one lifted on passing frames.
    left, right = 10 - swing // 2 - (swing > 0), 14 + swing // 2 + (swing < 0)
    for leg, top in ((left, 17), (right, 17 + lift)):
        if leg - 1 <= fx <= leg and top <= y <= 22 - (lift if leg == right else 0):
            return (boots if y >= 21 - (lift if leg == right else 0) else trousers) + (255,)
    return (0, 0, 0, 0)


def normal_map(height, width, rows, strength):
    # A tangent-space normal map from a height field (Sobel), green = up (y grows down the image,
    # so up is -y).
    def h(x, y):
        return height(max(0, min(width - 1, x)), max(0, min(rows - 1, y)))

    def pixel(x, y):
        dx = (h(x + 1, y - 1) + 2 * h(x + 1, y) + h(x + 1, y + 1)) - (h(x - 1, y - 1) + 2 * h(x - 1, y) + h(x - 1, y + 1))
        dy = (h(x - 1, y + 1) + 2 * h(x, y + 1) + h(x + 1, y + 1)) - (h(x - 1, y - 1) + 2 * h(x, y - 1) + h(x + 1, y - 1))
        nx, ny, nz = -dx * strength, dy * strength, 1.0
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        return (128 + 127 * nx / length, 128 + 127 * ny / length, 128 + 127 * nz / length, 255)
    return pixel


def crate_height(x, y):
    # Raised frame and brace over sunken boards with grooves between them.
    edge = min(x, y, 63 - x, 63 - y)
    if edge < 6:
        return 1.0 if edge > 0 else 0.4
    if abs((x - 6) - (y - 6)) < 4 and 6 <= x < 58:
        return 0.9
    return 0.2 if (y - 6) % 13 == 0 else 0.45


def stone_height(x, y):
    # A bevelled rim (rising towards the middle) and cobbles with mortar lines.
    edge = min(x, y, 47 - x, 47 - y)
    if edge < 12:
        return min(edge, 6) / 6.0 * 0.8
    if (x - 12) % 8 == 0 or (y - 12) % 8 == 0:
        return 0.3
    return 0.75 + 0.1 * noise(x // 2, y // 2, 4)


def main():
    os.makedirs(OUT, exist_ok=True)
    write_png(os.path.join(OUT, "Crate.png"), 64, 64, crate)
    write_png(os.path.join(OUT, "Ball.png"), 64, 64, ball)
    write_png(os.path.join(OUT, "Plank.png"), 64, 16, plank)
    write_png(os.path.join(OUT, "Stone.png"), 48, 48, stone)
    write_png(os.path.join(OUT, "Blade.png"), 128, 16, blade)
    write_png(os.path.join(OUT, "Sky.png"), 4, 64, sky)
    write_png(os.path.join(OUT, "Coins.png"), 64, 16, coins)
    write_png(os.path.join(OUT, "Hero.png"), 144, 24, hero)
    write_png(os.path.join(OUT, "Crate_Normal.png"), 64, 64, normal_map(crate_height, 64, 64, 1.2))
    write_png(os.path.join(OUT, "Stone_Normal.png"), 48, 48, normal_map(stone_height, 48, 48, 1.5))


if __name__ == "__main__":
    main()
