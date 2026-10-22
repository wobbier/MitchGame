"""Ambient sound for LaunchNight.lvl, synthesized: seamless mono loops in Assets/Sounds/LaunchNight/.

    python3 Tools/LaunchNightAudio.py          # write any loop that is missing
    python3 Tools/LaunchNightAudio.py --force  # rewrite them all

Everything is generated from fixed seeds (pure Python, no dependencies), so the files are
reproducible. Loops whose events follow a Sequence share its length and timing (the storm's
thunder follows the Storm clip's flashes, the snoring the guard's breathing, the buzz the hero's
failing panel), so they stay in step when both start on Play.
"""
import math
import random
import struct
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = "Assets/Sounds/LaunchNight/"
RATE = 32000
TAU = 2.0 * math.pi


# ---------------------------------------------------------------------------------------------
# Building blocks: buffers are plain lists of floats.

def silence(seconds):
    return [0.0] * int(seconds * RATE)


def white(n, rng):
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def lowpass(x, cutoff):
    a = 1.0 - math.exp(-TAU * cutoff / RATE)
    y, out = 0.0, []
    for v in x:
        y += a * (v - y)
        out.append(y)
    return out


def highpass(x, cutoff):
    low = lowpass(x, cutoff)
    return [v - l for v, l in zip(x, low)]


def bandpass(x, low, high):
    return lowpass(highpass(x, low), high)


def brown(n, rng, cutoff=120.0):
    return lowpass(white(n, rng), cutoff)


def gain(x, g):
    return [v * g for v in x]


def mix(*buffers):
    n = max(len(b) for b in buffers)
    out = [0.0] * n
    for b in buffers:
        for i, v in enumerate(b):
            out[i] += v
    return out


def normalize(x, peak=0.9):
    top = max(abs(v) for v in x) or 1.0
    return [v * peak / top for v in x]


def smooth_noise(seconds, rate_hz, rng, low=0.0, high=1.0):
    """A slowly wandering control curve (cosine-interpolated random points), for gusts and swells."""
    n = int(seconds * RATE)
    points = [rng.uniform(low, high) for _ in range(int(seconds * rate_hz) + 2)]
    out = []
    for i in range(n):
        f = i / RATE * rate_hz
        k = int(f)
        u = (1 - math.cos((f - k) * math.pi)) / 2
        out.append(points[k] * (1 - u) + points[k + 1] * u)
    return out


def loop_bed(make, seconds, fade=0.5):
    """A seamless loop from a generator of `seconds + fade` of audio: its tail is crossfaded (equal
    power) into its head, so the last sample runs straight into the first."""
    x = make(seconds + fade)
    n, f = int(seconds * RATE), int(fade * RATE)
    out = x[:n]
    for i in range(f):
        u = i / f
        out[i] = x[i] * math.sin(u * math.pi / 2) + x[n + i] * math.cos(u * math.pi / 2)
    return out


def place(buffer, event, at):
    """Add an event into a loop at `at` seconds, wrapping round the end."""
    start, n = int(at * RATE), len(buffer)
    for i, v in enumerate(event):
        buffer[(start + i) % n] += v


def decay(seconds, tau, attack=0.002):
    n = int(seconds * RATE)
    a = max(int(attack * RATE), 1)
    return [(i / a if i < a else 1.0) * math.exp(-(i / RATE) / tau) for i in range(n)]


def shaped(x, env):
    return [v * e for v, e in zip(x, env)]


def tone(freq, seconds, phase=0.0, harmonics=((1, 1.0),)):
    n = int(seconds * RATE)
    return [sum(a * math.sin(TAU * freq * h * i / RATE + phase * h) for h, a in harmonics) for i in range(n)]


def click(rng, length=0.012, low=1500.0, high=7000.0, tau=0.003):
    return shaped(bandpass(white(int(length * RATE), rng), low, high), decay(length, tau, 0.0005))


def thump(freq, length, tau):
    return [math.sin(TAU * freq * i / RATE) * math.exp(-(i / RATE) / tau) for i in range(int(length * RATE))]


def chirp(f0, f1, length, tau):
    out, phase = [], 0.0
    n = int(length * RATE)
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        phase += TAU * f / RATE
        out.append(math.sin(phase) * math.exp(-(i / RATE) / tau) * min(1.0, i / (0.002 * RATE)))
    return out


# ---------------------------------------------------------------------------------------------
# The sounds


def storm():
    """Rain on the storm glass, wind gusts, and thunder after each of the Storm clip's flashes
    (strikes at 3.0 s and 14.0-14.7 s of 23 s; sound arrives a little later)."""
    rng = random.Random(1)
    seconds = 23.0

    def bed(length):
        n = int(length * RATE)
        rain = gain(bandpass(white(n, rng), 500.0, 7000.0), 0.35)
        hiss = gain(highpass(white(n, rng), 3000.0), 0.08)
        gust = smooth_noise(length, 0.4, rng, 0.2, 1.0)
        wind = [v * g for v, g in zip(gain(lowpass(lowpass(white(n, rng), 260.0), 260.0), 6.0), gust)]
        return mix(rain, hiss, wind)
    out = loop_bed(bed, seconds, fade=1.0)
    # Drops ticking on the glass.
    for _ in range(int(seconds * 90)):
        place(out, gain(click(rng, 0.008, 1200.0, 6000.0, 0.0015), rng.uniform(0.05, 0.3)), rng.uniform(0, seconds))

    def thunder(length, crack, rumble_tau):
        n = int(length * RATE)
        body = lowpass(brown(n, rng, 90.0), 90.0)
        swell = smooth_noise(length, 3.0, rng, 0.3, 1.0)
        env = [min(1.0, (i / RATE) / 0.08) * math.exp(-(i / RATE) / rumble_tau) for i in range(n)]
        rumble = gain([b * s * e for b, s, e in zip(body, swell, env)], 160.0)
        snap = shaped(lowpass(white(n, rng), 2500.0), decay(length, 0.12, 0.003))
        return mix(rumble, gain(snap, crack))
    place(out, thunder(6.0, 0.9, 1.6), 3.55)   # the close double strike: a crack, then rolling
    place(out, thunder(8.0, 0.25, 2.6), 15.6)  # the long rolling one, further away
    return normalize(out, 0.85)


def server_hum():
    """The server room: mains hum, fans, a faint whine."""
    rng = random.Random(2)
    seconds = 8.0

    def bed(length):
        n = int(length * RATE)
        fans = gain(lowpass(white(n, rng), 1400.0), 0.9)
        rush = gain(bandpass(white(n, rng), 200.0, 900.0), 0.6)
        return mix(fans, rush)
    out = loop_bed(bed, seconds)
    # Whole cycles in 8 s, so the tones loop cleanly.
    out = mix(out, gain(tone(60.0, seconds, harmonics=((1, 1.0), (2, 0.5), (3, 0.25))), 0.25), gain(tone(2900.0, seconds), 0.015))
    return normalize(out, 0.8)


def fire():
    """BUILD-01 burning: a roar and crackles."""
    rng = random.Random(3)
    seconds = 10.0

    def bed(length):
        n = int(length * RATE)
        roar = lowpass(lowpass(white(n, rng), 420.0), 420.0)
        breathe = smooth_noise(length, 2.5, rng, 0.5, 1.0)
        return gain([r * b for r, b in zip(roar, breathe)], 9.0)
    out = loop_bed(bed, seconds)
    for _ in range(int(seconds * 28)):
        pop = click(rng, rng.uniform(0.004, 0.02), rng.uniform(600, 2000), rng.uniform(3000, 9000), rng.uniform(0.001, 0.005))
        place(out, gain(pop, rng.uniform(0.1, 1.0) ** 2 * 1.4), rng.uniform(0, seconds))
    return normalize(out, 0.85)


def alarm():
    """The fire alarm: temporal-three beeps, in step with the 5 s Server Room Alarm clip."""
    seconds = 5.0
    out = silence(seconds)
    beep = tone(880.0, 0.5, harmonics=((1, 1.0), (3, 0.33), (5, 0.2), (7, 0.14)))
    edge = int(0.004 * RATE)
    beep = [v * min(1.0, i / edge, (len(beep) - i) / edge) for i, v in enumerate(beep)]
    for t in (0.0, 1.0, 2.0):
        place(out, beep, t)
    return normalize(out, 0.8)


def sprinklers():
    """Sprinkler heads hissing and water spattering on the floor."""
    rng = random.Random(5)

    def bed(length):
        n = int(length * RATE)
        hiss = gain(highpass(white(n, rng), 2500.0), 0.5)
        flutter = smooth_noise(length, 18.0, rng, 0.4, 1.0)
        spatter = [v * f for v, f in zip(gain(bandpass(white(n, rng), 300.0, 2500.0), 1.2), flutter)]
        return mix(hiss, spatter)
    out = loop_bed(bed, 6.0)
    return normalize(out, 0.8)


def typing():
    """The last developer's keyboard, in step with the 2 s Typing clip (a key every 1/8 s, with a
    pause to read the error at keys 5-6 of each 8)."""
    rng = random.Random(6)
    seconds = 2.0
    out = silence(seconds)
    for i in range(16):
        if i % 8 in (5, 6):
            continue
        key = mix(gain(click(rng, 0.018, 1800.0, 7000.0, 0.004), 0.7), gain(thump(rng.uniform(180, 260), 0.03, 0.006), 0.5))
        place(out, gain(key, rng.uniform(0.6, 1.0)), i * 0.125 + rng.uniform(-0.01, 0.01))
        if rng.random() < 0.35:  # a second key in the same stroke
            place(out, gain(click(rng, 0.015, 1500.0, 6000.0, 0.003), 0.4), i * 0.125 + 0.05 + rng.uniform(0, 0.02))
    return normalize(out, 0.8)


def panel_buzz():
    """The hero's failing ceiling panel: a 120 Hz buzz that cuts and crackles where the Office
    Life clip (12 s) flickers it (2.15-2.45 s and 7.05-7.7 s)."""
    rng = random.Random(7)
    seconds = 12.0
    buzz = tone(120.0, seconds, harmonics=((1, 1.0), (2, 0.6), (3, 0.5), (5, 0.3), (7, 0.2)))
    level = [1.0] * len(buzz)
    for start, end, low in [(2.15, 2.2, 0.1), (2.3, 2.45, 0.05), (7.05, 7.45, 0.15), (7.6, 7.7, 0.2)]:
        for i in range(int(start * RATE), int(end * RATE)):
            level[i] = low
    level = lowpass(level, 200.0)
    out = [b * l * 0.4 for b, l in zip(buzz, level)]
    for t in (2.15, 2.2, 2.3, 2.45, 7.05, 7.45, 7.6, 7.7):
        place(out, gain(click(rng, 0.02, 800.0, 6000.0, 0.004), 0.9), t)
    return normalize(out, 0.7)


def sparks():
    """The fallen cable arcing: bursts of crackle and buzz."""
    rng = random.Random(8)
    seconds = 6.0
    out = silence(seconds)
    t = 0.0
    while t < seconds:
        length = rng.uniform(0.03, 0.25)
        n = int(length * RATE)
        jitter = [1.0 if rng.random() < 0.35 else 0.15 for _ in range(n)]
        crackle = [v * j for v, j in zip(highpass(white(n, rng), 1500.0), lowpass(jitter, 3000.0))]
        hum = tone(60.0, length, harmonics=((1, 0.4), (3, 0.3), (5, 0.2)))
        env = [min(1.0, i / 64) * math.exp(-(i / RATE) / (length * 0.6)) for i in range(n)]
        place(out, gain(shaped(mix(crackle, gain(hum, 0.5)), env), rng.uniform(0.3, 1.0)), t)
        t += length + rng.uniform(0.05, 0.6)
    return normalize(out, 0.8)


def copier():
    """The jammed photocopier: motor whirr and a sheet thrown out twice a second."""
    rng = random.Random(9)
    seconds = 4.0

    def bed(length):
        n = int(length * RATE)
        return gain(bandpass(white(n, rng), 150.0, 900.0), 0.6)
    out = mix(loop_bed(bed, seconds), gain(tone(90.0, seconds, harmonics=((1, 1.0), (2, 0.4))), 0.15))
    for k in range(8):
        t = k * 0.5
        place(out, gain(thump(70.0, 0.12, 0.03), 0.8), t)
        place(out, gain(click(rng, 0.03, 400.0, 3000.0, 0.01), 0.5), t + 0.02)
        swish = shaped(bandpass(white(int(0.18 * RATE), rng), 2000.0, 8000.0),
                       [math.sin(math.pi * i / int(0.18 * RATE)) for i in range(int(0.18 * RATE))])
        place(out, gain(swish, 0.25), t + 0.15)
    return normalize(out, 0.75)


def microwave():
    """The microwave still running, popcorn popping (and burning)."""
    rng = random.Random(10)
    seconds = 8.0

    def bed(length):
        return gain(bandpass(white(int(length * RATE), rng), 300.0, 2000.0), 0.4)
    out = mix(loop_bed(bed, seconds), gain(tone(120.0, seconds, harmonics=((1, 1.0), (2, 0.5), (3, 0.3))), 0.25))
    for _ in range(int(seconds * 2.5)):
        pop = mix(click(rng, 0.03, 300.0, 3000.0, 0.008), gain(thump(rng.uniform(150, 300), 0.04, 0.01), 0.6))
        place(out, gain(pop, rng.uniform(0.3, 1.0)), rng.uniform(0, seconds))
    return normalize(out, 0.75)


def coffee():
    """Coffee running off the counter and splashing on the floor."""
    rng = random.Random(11)
    seconds = 5.0

    def bed(length):
        n = int(length * RATE)
        bubble = smooth_noise(length, 40.0, rng, 0.2, 1.0)
        return [v * b for v, b in zip(gain(bandpass(white(n, rng), 800.0, 3500.0), 0.8), bubble)]
    out = loop_bed(bed, seconds)
    for _ in range(int(seconds * 14)):
        f = rng.uniform(700, 1400)
        place(out, gain(chirp(f, f * 1.6, 0.03, 0.01), rng.uniform(0.1, 0.4)), rng.uniform(0, seconds))
    return normalize(out, 0.7)


def fish_tank():
    """The tank's bubbler and pump."""
    rng = random.Random(12)
    seconds = 6.0
    out = gain(tone(50.0, seconds, harmonics=((1, 1.0), (2, 0.5))), 0.08)
    for _ in range(int(seconds * 22)):
        f = rng.uniform(400, 1300)
        place(out, gain(chirp(f, f * rng.uniform(1.3, 2.0), rng.uniform(0.01, 0.035), 0.008), rng.uniform(0.15, 0.6)), rng.uniform(0, seconds))
    return normalize(out, 0.6)


def arcade():
    """The arcade cabinet's attract mode: a square-wave tune, 16 beats at 120 bpm."""
    seconds = 8.0
    out = silence(seconds)
    beat = 0.5

    def square(freq, length, level):
        n = int(length * RATE)
        return [level * (1.0 if math.sin(TAU * freq * i / RATE) >= 0 else -1.0) * math.exp(-(i / RATE) / (length * 0.8)) for i in range(n)]
    notes = [0, 4, 7, 12, 7, 4, 0, 4, 5, 9, 12, 17, 12, 9, 7, 11]
    bass = [0, 0, 5, 7]
    for k, note in enumerate(notes):
        place(out, square(523.25 * 2 ** (note / 12), beat * 0.45, 0.25), k * beat)
        place(out, square(523.25 * 2 ** (note / 12 + 1), beat * 0.2, 0.08), k * beat + beat / 2)
    for k in range(16):
        place(out, square(130.81 * 2 ** (bass[(k // 4) % 4] / 12), beat * 0.4, 0.3), k * beat)
    return normalize(lowpass(out, 6000.0), 0.6)


def snoring():
    """The security guard, in step with the 11 s Guard Dozing clip: snores on the in-breaths
    (0-2 s, 4-6 s), sighs out, then the nod at 8.2 s and the snort that jerks him awake."""
    rng = random.Random(14)
    seconds = 11.0
    out = silence(seconds)

    def snore(length):
        n = int(length * RATE)
        pulses, phase = [], 0.0
        for i in range(n):
            phase += TAU * (55.0 + 15.0 * math.sin(math.pi * i / n)) / RATE
            pulses.append(max(math.sin(phase), 0.0) ** 6)
        rasp = mix(gain(pulses, 1.0), gain(bandpass(white(n, rng), 150.0, 1200.0), 0.25))
        env = [math.sin(math.pi * i / n) ** 1.5 for i in range(n)]
        return lowpass(shaped(rasp, env), 1800.0)

    def sigh(length):
        n = int(length * RATE)
        env = [math.sin(math.pi * i / n) ** 2 for i in range(n)]
        return shaped(bandpass(white(n, rng), 300.0, 2500.0), env)
    place(out, snore(1.8), 0.1)
    place(out, gain(sigh(1.6), 0.25), 2.2)
    place(out, snore(1.8), 4.1)
    place(out, gain(sigh(1.4), 0.25), 6.1)
    snort = shaped(mix(lowpass(white(int(0.25 * RATE), rng), 900.0), gain(tone(80.0, 0.25), 0.5)), decay(0.25, 0.07, 0.005))
    place(out, gain(snort, 1.4), 8.45)
    place(out, gain(sigh(1.2), 0.2), 9.3)
    return normalize(out, 0.8)


def ceiling_fan():
    """The boss's ceiling fan: a soft whoosh per blade (one turn every 2 s, four blades)."""
    rng = random.Random(15)
    seconds = 2.0

    def bed(length):
        n = int(length * RATE)
        air = lowpass(white(n, rng), 700.0)
        return [v * (0.55 + 0.45 * math.sin(TAU * 2.0 * i / RATE) ** 2) for i, v in enumerate(air)]
    out = mix(loop_bed(bed, seconds, 0.25), gain(tone(100.0, seconds), 0.02))
    return normalize(out, 0.6)


def office_air():
    """The floor's air handling: a low, even room tone under everything."""
    rng = random.Random(16)

    def bed(length):
        n = int(length * RATE)
        return mix(lowpass(lowpass(white(n, rng), 300.0), 300.0), gain(bandpass(white(n, rng), 300.0, 1500.0), 0.04))
    return normalize(loop_bed(bed, 12.0, 1.0), 0.6)


SOUNDS = {
    "Storm": storm, "ServerHum": server_hum, "Fire": fire, "Alarm": alarm, "Sprinklers": sprinklers, "Typing": typing,
    "PanelBuzz": panel_buzz, "Sparks": sparks, "Copier": copier, "Microwave": microwave, "Coffee": coffee, "FishTank": fish_tank,
    "Arcade": arcade, "Snoring": snoring, "CeilingFan": ceiling_fan, "OfficeAir": office_air,
}


def path(name):
    return FOLDER + name + ".wav"


def write(name, samples):
    target = ROOT / path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in samples)
    with wave.open(str(target), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(data)


def write_all(force=False):
    for name, make in SOUNDS.items():
        if force or not (ROOT / path(name)).exists():
            write(name, make())
            print("wrote", path(name))


if __name__ == "__main__":
    write_all("--force" in sys.argv)
