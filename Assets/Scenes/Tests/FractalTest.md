# Mandelbrot

Open `FractalTest.lvl` and use **Game View**. The `Mandelbrot Camera` renders
`Assets/ShaderGraphs/Mandelbrot.shadergraph` before tonemapping, with fixed
exposure, subtle bloom and FXAA.

The animated view repeats Mandelbrot detail by scale. Time moves through a
fixed logarithmic-radius pattern; there is no screen wipe or camera reset.
Neighboring spatial tiles share their endpoint coordinates, orientation and
escape-potential offset, so both values and slopes join across the loop.
The two distance evaluations join those spatial tiles, rather than switching
between camera views. Palette animation follows the same loop phase.

The default detail is centered at `(-0.101096363845622, 0.956286510809142)`.
Its critical orbit reaches a repelling fixed point; three iterations give a
local scale factor of approximately `2.34379` and rotation of `-0.0233993`
radians. Repeating that detail produces a clean inward zoom at finite shader
precision. This is a scale-repeating visualization; set **Zoom Speed** to `0`
for an ordinary, static view of the Mandelbrot parameter plane.

Exterior distance estimates filter contour bands, palette cycles, edge
coverage and relief below a pixel. A tiny filtered center suppresses the
logarithmic mapping's singularity.

Select the camera and expand **PostProcess > Graph Properties > Mandelbrot**:

| Control | Use |
| --- | --- |
| Center | Complex-plane detail sampled by the loop; defaults to the point above |
| Zoom | Magnification of the source detail; defaults to `64` |
| Zoom Speed | Zoom doublings per second; `0.22` gives a complete loop about every `5.59` seconds; `0` selects the static view |
| Iterations | `512` by default, clamped to `32–512`; lower for faster rendering |
| Palette Phase | Offset the navy, teal, gold and pearl palette |
| Palette Cycles | Whole palette cycles per zoom loop, rounded to `0–4`; `0` keeps the palette fixed |
| Contour Density | Number of palette cycles across escape iterations |
| Glow | Cyan light along the boundary |
| Brightness | Linear HDR intensity before exposure and bloom |

For the static overview, set **Zoom Speed** to `0`, **Center** to `(-0.65, 0)`
and **Zoom** to `1`. Reset overrides to return to the animated loop. Manual
zooms eventually reach single-precision limits.

Save graph edits in the Shader Graph editor to regenerate `Mandelbrot.sg/`.
To capture the animated scene from the project root:

```bash
nix develop --command Engine/Tools/Headless.sh \
  ./.build/Game_linux_Debug/Game_EntryPoint_x64 \
  --scene Assets/Scenes/Tests/FractalTest.lvl \
  --frames 12 --frame-time 0.016666667 --width 1280 --height 720 \
  --no-audio --no-debug-overlay --screenshot .tmp/Mandelbrot.png --exit
```
