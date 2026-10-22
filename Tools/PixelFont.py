"""A 5x7 pixel font compiled into shader code, so graphs can print text without a texture.

    code = text_function([("SHIP IT", 0.1, 0.6, 0.2)])

Each glyph is 35 bits (7 rows of 5), stored as two floats below 2^20 so every bit survives in
float maths (no integer ops, which the bgfx dialects don't share). The generated Custom Function
body walks the characters of each line with an if/else chain; text is fixed at build time.
Digits can also be chosen at runtime from a float (see digit_code), which the countdown uses.
"""

GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "10001", "11001", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000"] * 7,
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "%": ["11001", "11001", "00010", "00100", "01000", "10011", "10011"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    "<": ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "*": ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "@": ["01110", "10001", "10111", "10101", "10111", "10000", "01111"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    # A sad face for the crashed monitor, drawn on the 5x7 grid.
    "~": ["00000", "01010", "00000", "00000", "01110", "10001", "00000"],
}


def encode(char):
    """The glyph as (lo, hi): bit row*5+col, rows 0-3 in lo, rows 4-6 in hi (row 0 is the top)."""
    rows = GLYPHS[char.upper()]
    lo = hi = 0
    for row, bits in enumerate(rows):
        for col, bit in enumerate(bits):
            if bit == "1":
                index = row * 5 + col
                if index < 20:
                    lo |= 1 << index
                else:
                    hi |= 1 << (index - 20)
    return lo, hi


def f(value):
    """A float literal valid in every shader dialect, exact for the glyph codes (< 2^20)."""
    value = float(value)
    if value.is_integer():
        return "%d.0" % value
    return ("%.6f" % value).rstrip("0")


# Reads one bit of the glyph (lo, hi) at cell pixel (px, py); writes `hit`.
BIT_LOOKUP = """
{{
    float b = {py} * 5.0 + {px};
    float word = b < 20.0 ? glo : ghi;
    float shift = b < 20.0 ? b : b - 20.0;
    {hit} = mod(floor(word / exp2(shift)), 2.0);
}}
"""


def chain(index_var, codes, indent="        "):
    """Sets glo/ghi from codes[index]; blank glyphs are skipped (glo/ghi start at zero)."""
    lines = []
    for i, (lo, hi) in enumerate(codes):
        if lo or hi:
            lines.append("%sif (%s > %s && %s < %s) { glo = %s; ghi = %s; }" % (
                indent, index_var, f(i - 0.5), index_var, f(i + 0.5), f(lo), f(hi)))
    return "\n".join(lines)


def text_function(lines, aspect=1.0, uv="UV", dots=False):
    """Custom Function code reading the Vec2 input `uv` and writing the outputs Mask1..Mask3.

    lines: (text, x, y, height[, layer]) - the text's left edge and top in UV space (y measured
    downwards: uv.y = 0 at the top), the cap height in UV units, and which Mask output it adds to
    (1-3). text is a string, or a list of slots: a character, or ("digit", expression) for a digit
    computed at runtime from a float expression of the function's inputs. aspect is the surface's
    width/height, so glyph pixels stay square on wide screens. dots draws each pixel as a round LED.
    """
    out = ["Mask1 = 0.0;", "Mask2 = 0.0;", "Mask3 = 0.0;"]
    for line in lines:
        text, x, y, height = line[:4]
        layer = line[4] if len(line) > 4 else 1
        slots = list(text)
        pixel = height / 7.0
        cell_w = pixel * 6.0 / aspect
        cell_h = pixel * 7.0
        out.append("{")
        out.append("    vec2 q = vec2((%s.x - %s) / %s, (%s.y - %s) / %s);" % (uv, f(x), f(cell_w), uv, f(y), f(cell_h)))
        out.append("    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < %s)" % f(len(slots)))
        out.append("    {")
        out.append("        float ci = floor(q.x);")
        out.append("        float px = floor(fract(q.x) * 6.0);")
        out.append("        float py = floor(q.y * 7.0);")
        out.append("        float glo = 0.0;")
        out.append("        float ghi = 0.0;")
        static = [encode(c) if isinstance(c, str) else (0, 0) for c in slots]
        out.append(chain("ci", static))
        for i, slot in enumerate(slots):
            if not isinstance(slot, str):
                out.append("        if (ci > %s && ci < %s)" % (f(i - 0.5), f(i + 0.5)))
                out.append("        {")
                out.append("            float dv = clamp(floor(%s), 0.0, 9.0);" % slot[1])
                out.append(chain("dv", [encode(str(d)) for d in range(10)], "            "))
                out.append("        }")
        out.append("        float hit = 0.0;")
        out.append("        if (px < 5.0)")
        out.append(BIT_LOOKUP.format(px="px", py="py", hit="hit").replace("\n", "\n        "))
        if dots:
            out.append("        vec2 sub = vec2(fract(fract(q.x) * 6.0), fract(q.y * 7.0)) - vec2_splat(0.5);")
            out.append("        hit *= 1.0 - smoothstep(0.3, 0.46, length(sub));")
        out.append("        Mask%d = max(Mask%d, hit);" % (layer, layer))
        out.append("    }")
        out.append("}")
    return "\n".join(out)


def width(text, height, aspect=1.0):
    """The UV width a line of text covers."""
    return len(text) * height / 7.0 * 6.0 / aspect
