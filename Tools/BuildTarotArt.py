#!/usr/bin/env python3
"""Generate the tarot card art in Assets/UI/Drive/Tarot/: a gold line icon for each of the 22 Major
Arcana (named after the Arcana enum in TarotCards.cs) and the card back that the UI and the dashboard
deck (TarotDeck.cs) use. Draws SVG and rasterizes it with ImageMagick (librsvg)."""

import math
import os
from pathlib import Path
import subprocess
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1] / "Assets/UI/Drive/Tarot")
GOLD = "#F6D58A"
os.makedirs(OUT, exist_ok=True)

def star(cx, cy, r, points=5, inner=0.45, rot=-90):
    pts = []
    for i in range(points * 2):
        rad = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / points)
        pts.append(f"{cx + rad * math.cos(a):.2f},{cy + rad * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}"/>'

def rays(cx, cy, r0, r1, n, rot=0):
    d = ""
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        d += f"M{cx + r0 * math.cos(a):.2f} {cy + r0 * math.sin(a):.2f} L{cx + r1 * math.cos(a):.2f} {cy + r1 * math.sin(a):.2f} "
    return f'<path d="{d}"/>'

INF = '<path d="M50 {y} C42 {a} 30 {a} 30 {y} C30 {b} 42 {b} 50 {y} C58 {a} 70 {a} 70 {y} C70 {b} 58 {b} 50 {y} Z"/>'
def infinity(y, h=7):
    return INF.format(y=y, a=y - h, b=y + h)

FILL = f'fill="{GOLD}" fill-opacity="0.22"'

ICONS = {
"Fool": f'''
<circle cx="20" cy="22" r="8" {FILL}/>{rays(20, 22, 11, 16, 8)}
<path d="M8 92 L8 64 L40 64 L46 70"/>
<circle cx="56" cy="34" r="6"/>
<path d="M56 40 L54 58 M54 58 L46 72 M54 58 L64 70 M55 46 L42 40 M55 46 L68 38 L72 26"/>
<path d="M72 26 L80 30 L76 36 Z" {FILL}/>
<path d="M20 64 Q24 54 30 58" />''',
"Magician": f'''
{infinity(16)}
<path d="M50 30 L50 70 M44 30 L56 30 M44 70 L56 70"/>
<path d="M14 82 L86 82 M20 82 L20 92 M80 82 L80 92"/>
<circle cx="24" cy="74" r="5" {FILL}/>
<path d="M36 78 L36 66 M33 69 L39 69"/>
{star(66, 74, 6)}
<path d="M76 68 L82 68 L80 78 L78 78 Z"/>''',
"HighPriestess": f'''
<path d="M14 92 L14 26 L26 26 L26 92 Z M74 92 L74 26 L86 26 L86 92 Z" {FILL}/>
<path d="M10 26 L30 26 M70 26 L90 26 M10 92 L90 92"/>
<path d="M58 36 A16 16 0 1 0 58 64 A12 12 0 1 1 58 36 Z" {FILL}/>
<path d="M38 76 L62 76 M50 70 L50 86"/>''',
"Empress": f'''
{star(28, 18, 5)}{star(50, 12, 5)}{star(72, 18, 5)}
<circle cx="50" cy="44" r="16" {FILL}/>
<path d="M50 60 L50 88 M38 74 L62 74"/>
<path d="M18 92 Q24 70 30 92 M70 92 Q76 70 82 92"/>''',
"Emperor": f'''
<path d="M26 34 L26 18 L38 28 L50 12 L62 28 L74 18 L74 34 Z" {FILL}/>
<path d="M22 92 L22 46 L78 46 L78 92 M22 62 L78 62 M30 92 L30 62 M70 92 L70 62"/>
<path d="M22 46 Q10 40 14 30 Q18 26 22 32 M78 46 Q90 40 86 30 Q82 26 78 32"/>''',
"Hierophant": f'''
<path d="M50 8 L50 92 M38 18 L62 18 M34 28 L66 28 M30 38 L70 38"/>
<circle cx="24" cy="74" r="7"/><path d="M29 79 L44 92 M36 86 L32 90"/>
<circle cx="76" cy="74" r="7"/><path d="M71 79 L56 92 M64 86 L68 90"/>''',
"Lovers": f'''
<path d="M38 80 C14 62 14 42 26 38 C34 35 38 42 38 46 C38 42 42 35 50 38 C62 42 62 62 38 80 Z" {FILL}/>
<path d="M62 80 C38 62 38 42 50 38 C58 35 62 42 62 46 C62 42 66 35 74 38 C86 42 86 62 62 80 Z"/>
{rays(50, 18, 4, 10, 8)}<circle cx="50" cy="18" r="3"/>''',
"Chariot": f'''
{star(30, 14, 4)}{star(50, 10, 4)}{star(70, 14, 4)}
<path d="M24 26 L76 26 L70 32 L30 32 Z" {FILL}/>
<path d="M30 32 L30 48 M70 32 L70 48"/>
<path d="M22 48 L78 48 L74 70 L26 70 Z"/>
<circle cx="30" cy="78" r="11" {FILL}/><circle cx="70" cy="78" r="11" {FILL}/>
{rays(30, 78, 0, 11, 6)}{rays(70, 78, 0, 11, 6)}''',
"Strength": f'''
{infinity(14, 6)}
<path d="M50 32 {" ".join(f"L{50 + (30 if i % 2 == 0 else 24) * math.sin(math.radians(i * 20)):.1f} {58 - (30 if i % 2 == 0 else 24) * math.cos(math.radians(i * 20)):.1f}" for i in range(19))} Z" {FILL}/>
<circle cx="50" cy="58" r="17"/>
<circle cx="43" cy="53" r="2" fill="{GOLD}"/><circle cx="57" cy="53" r="2" fill="{GOLD}"/>
<path d="M46 62 L54 62 L50 67 Z M50 67 L50 70 M44 72 Q50 76 56 72"/>''',
"Hermit": f'''
<path d="M70 10 L70 92"/>
<path d="M34 22 L46 22 M40 16 L40 22"/>
<path d="M28 30 L52 30 L48 60 L32 60 Z" {FILL}/>
{star(40, 45, 9, 6, 0.5)}
<path d="M28 30 L34 22 M52 30 L46 22 M30 66 L50 66"/>''',
"WheelOfFortune": f'''
<circle cx="50" cy="50" r="38" {FILL}/>
<circle cx="50" cy="50" r="26"/><circle cx="50" cy="50" r="6"/>
{rays(50, 50, 6, 38, 8, 22.5)}
<path d="M50 8 L46 2 L54 2 Z" fill="{GOLD}"/>''',
"Justice": f'''
<path d="M50 10 L50 90 M36 90 L64 90 M18 26 L82 26"/>
<path d="M18 26 L8 54 L28 54 Z M82 26 L72 54 L92 54 Z"/>
<path d="M8 54 Q18 64 28 54 M72 54 Q82 64 92 54" {FILL}/>
<circle cx="50" cy="12" r="4" {FILL}/>''',
"HangedMan": f'''
<path d="M14 12 L86 12 M24 12 L24 92 M76 12 L76 92"/>
<path d="M50 12 L50 30"/>
<path d="M50 30 L50 60 M50 30 L40 40 L50 46 M50 54 L36 62 M50 54 L64 62"/>
<circle cx="50" cy="70" r="9" {FILL}/>
<circle cx="50" cy="70" r="14" stroke-width="1.2" stroke-dasharray="3 3"/>''',
"Death": f'''
<path d="M24 46 C24 18 76 18 76 46 C76 58 70 62 66 64 L66 76 L34 76 L34 64 C30 62 24 58 24 46 Z" {FILL}/>
<circle cx="39" cy="46" r="7" fill="{GOLD}"/><circle cx="61" cy="46" r="7" fill="{GOLD}"/>
<path d="M50 54 L46 62 L54 62 Z"/>
<path d="M42 70 L42 76 M50 70 L50 76 M58 70 L58 76"/>
<path d="M14 92 L86 92"/>''',
"Temperance": f'''
<path d="M14 30 L36 30 L32 52 L18 52 Z" {FILL}/>
<path d="M64 60 L86 60 L82 82 L68 82 Z" {FILL}/>
<path d="M34 34 C52 34 58 46 70 58" stroke-dasharray="4 4"/>
<path d="M25 52 L25 62 M75 82 L75 92 M18 62 L32 62 M68 92 L82 92"/>
{star(50, 16, 5, 4, 0.4)}''',
"Devil": f'''
<path d="M28 34 Q14 22 20 6 Q26 22 38 26 M72 34 Q86 22 80 6 Q74 22 62 26"/>
<circle cx="50" cy="56" r="30" {FILL}/>
{star(50, 58, 26, 5, 0.38, 90)}''',
"Tower": f'''
<path d="M34 92 L38 34 L62 34 L66 92 Z" {FILL}/>
<path d="M32 34 L68 34 L66 26 L34 26 Z M44 52 L44 60 M56 66 L56 74 M46 92 L46 80 L54 80 L54 92"/>
<path d="M60 4 L48 18 L56 18 L44 32 L48 30" />
<path d="M22 22 Q18 30 24 34 Q22 28 28 26 Z M78 40 Q84 46 78 52 Q80 46 74 44 Z" fill="{GOLD}"/>''',
"Star": f'''
{star(50, 40, 26, 8, 0.38, -90)}
{star(18, 18, 6, 8, 0.4)}{star(82, 18, 6, 8, 0.4)}{star(16, 58, 5, 8, 0.4)}{star(84, 58, 5, 8, 0.4)}
<path d="M10 84 Q30 76 50 84 T90 84 M18 92 Q34 86 50 92 T82 92"/>''',
"Moon": f'''
<path d="M60 10 A26 26 0 1 0 60 62 A20 20 0 1 1 60 10 Z" {FILL}/>
<path d="M10 92 L10 70 L22 70 L22 92 M78 92 L78 70 L90 70 L90 92 M8 70 L24 70 M76 70 L92 70"/>
<path d="M34 88 Q50 74 66 88"/>
<circle cx="72" cy="22" r="1.5" fill="{GOLD}"/><circle cx="80" cy="38" r="1.5" fill="{GOLD}"/><circle cx="68" cy="48" r="1.5" fill="{GOLD}"/>''',
"Sun": f'''
<circle cx="50" cy="46" r="20" {FILL}/>
{rays(50, 46, 25, 38, 12)}{rays(50, 46, 25, 32, 12, 15)}
<circle cx="43" cy="42" r="2" fill="{GOLD}"/><circle cx="57" cy="42" r="2" fill="{GOLD}"/>
<path d="M42 52 Q50 58 58 52"/>
<path d="M14 92 L86 92"/>''',
"Judgement": f'''
<path d="M12 18 L54 44" stroke-width="4.5"/>
<path d="M50 38 L76 26 L74 66 L56 52 Z" {FILL}/>
<path d="M26 27 L26 48 L35 44 L44 48 L44 38 M35 32 L35 42 M31 36 L39 36"/>
{rays(76, 46, 8, 18, 5, -50)}
<path d="M12 92 L12 78 M24 92 L24 74 M36 92 L36 80 M8 82 L16 82 M20 78 L28 78 M32 84 L40 84"/>''',
"World": f'''
<ellipse cx="50" cy="50" rx="26" ry="38"/>
{"".join(f'<ellipse cx="{50 + 26 * math.cos(math.radians(a)):.1f}" cy="{50 + 38 * math.sin(math.radians(a)):.1f}" rx="3" ry="5" transform="rotate({a + 90} {50 + 26 * math.cos(math.radians(a)):.1f} {50 + 38 * math.sin(math.radians(a)):.1f})" {FILL}/>' for a in range(0, 360, 30))}
{star(50, 50, 14, 5, 0.45)}
<circle cx="12" cy="12" r="4"/><circle cx="88" cy="12" r="4"/><circle cx="12" cy="88" r="4"/><circle cx="88" cy="88" r="4"/>''',
}

def write(name, body, w=100, h=100, pw=256, ph=256, background=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}" height="{ph}" viewBox="0 0 {w} {h}">{background}'
           f'<g fill="none" stroke="{GOLD}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')
    path = os.path.join(OUT, name)
    open(path + ".svg", "w").write(svg)
    subprocess.run(["magick", "-background", "none", path + ".svg", "-depth", "8", "-define", "png:exclude-chunks=date,time",
                    "PNG32:" + path + ".png"], check=True)
    os.remove(path + ".svg")

for name, body in ICONS.items():
    write(name, body)

# The card back: deep violet, a gold border, a sun inside a crescent and scattered stars.
back = f'''<defs><radialGradient id="g" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#4B2A86"/><stop offset="1" stop-color="#160A2E"/></radialGradient></defs>
<rect width="100" height="160" rx="6" fill="url(#g)"/>'''
body = f'''<rect x="5" y="5" width="90" height="150" rx="4"/>
<rect x="10" y="10" width="80" height="140" rx="2" stroke-width="1.2"/>
<path d="M62 52 A30 30 0 1 0 62 108 A24 24 0 1 1 62 52 Z" fill="{GOLD}" fill-opacity="0.25"/>
<circle cx="58" cy="80" r="9" fill="{GOLD}" fill-opacity="0.5"/>{rays(58, 80, 12, 17, 12)}
{star(24, 24, 4)}{star(76, 24, 4)}{star(24, 136, 4)}{star(76, 136, 4)}{star(50, 30, 3)}{star(50, 130, 3)}'''
write("Back", body, 100, 160, 256, 410, back)
print("wrote", len(ICONS) + 1, "images to", OUT)
