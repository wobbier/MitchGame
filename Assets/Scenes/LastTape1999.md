# Last Tape — July 1999

A blue-hour cul-de-sac, an open-garage LAN party, a sofa dragged outside, a CRT
and console, abandoned pizza, home-video cassettes and party lights. Built from
individual Synty Town assets, with 193 authored entities and four editable shader
graphs. The palette is cool moonlight against tungsten, sodium and CRT phosphor.

Open **Assets/Scenes/LastTape1999.lvl** in Havana and press Play. The Game View
shows the camcorder image; the World View remains available for editing.

To run the standalone game on Linux, from the repository root:

```bash
nix develop --command .build/Game_linux_Debug/Game_EntryPoint_x64 \
  --scene Assets/Scenes/LastTape1999.lvl --no-debug-overlay
```

`--no-debug-overlay` hides the game debug menu and profiler bar. It also works
for screenshot captures; it leaves game UI and performance recording available.

## Camera controls

| Control | Action |
| --- | --- |
| 1 | Street establishing shot |
| 2 | Garage / console close-up |
| 3 | View from the opposite side of the court |
| WASD | Fly horizontally |
| Q / E | Lower / raise the camera |
| Arrow keys | Pan / tilt |
| Left Shift | Move faster |
| Space | Toggle gentle handheld sway |

This is a free camera for exploring the set, with no collision. Shot transitions
ease into position. Sway and movement speed are exposed on `LastTapeCamera`.

## Shader graphs

All graphs live in `Assets/ShaderGraphs/LastTape/`, with their generated `.sg/`
sources beside them. Open them in Havana's Shader Graph editor.

| Graph | Purpose and controls |
| --- | --- |
| `Camcorder1999` | One After Tonemap pass: a 480-line raster, lens bow, transport jitter, chroma bleed, shadow-weighted CCD grain, alternating scanlines, a narrow head-switching band and lens vignette. Exposes Tape Wear, Sensor Grain, Chroma Bleed, Lens Vignette, Camera OSD and 4:3 Frame. |
| `CRTAfterHours` | Animated phosphor terminal windows, scanlines, cursor and a rolling refresh band. Brightness and Phosphor are exposed per screen. |
| `DampAsphalt` | World-space grit, patchy dampness, surface normals and variable roughness. Exposes Dampness. |
| `BlueHourSky` | A violet horizon, cool upper sky, sparse stars and a soft moon. No atmosphere raymarch or sky-probe capture. |

The camcorder OSD has a blinking REC light, battery, SP indicator and a running
seconds counter. The original 96 × 64 pixel font atlas costs one texture sample
for the whole display. Its 4:3 frame crops the sides on wide windows and adds
letterboxing on narrow ones. The image effect and OSD work directly in the
camera's graph stack, including when the editor is not in Play mode.

The Custom Function nodes expose the transport, signal, display and surface
calculations as named blocks, connected with ordinary UV, Time, Scene Color,
texture and property nodes. Their code is stored in the graphs, not the engine.

## Rendering budget

- Compact model hierarchies and shared opaque palette materials allow repeated
  fences, vegetation, curbs and props to use the existing instancing path.
- Only the moon key and driveway spot request shadows; the camera light,
  practical lights and CRT fills do not. Shadow distance is limited to 38 m.
- Analytic height fog, fixed exposure and FXAA keep the camera stack inexpensive.
  Volumetric fog and TAA are disabled.
- The tape effect uses four scene-color reads and one font read in a single
  pass. There are no per-character draw calls or per-screen render textures.
- Only the camera has an update script. CRTs, sky and tape animation run in
  shaders. The complete Synty demo town is not loaded.

Synty's FBXs contain obsolete publisher PSD paths. Scene material overrides
explicitly bind the included `PolygonTown_01_A.png` to each part. Source-import
warnings about those old paths can still appear; the scene uses the supplied
PNG without modifying the original models or their import settings.

## Rebuild and validation

`python3 Tools/BuildLastTape.py` reconstructs the scene, graph documents and
original pixel artwork without Python packages. It overwrites those authored
files, so save custom edits elsewhere before using it. `LastTapeSyntyParts.json`
records the imported part paths, including FBX pivot nodes.

After regenerating, open and save the graphs in Havana to export their sources,
or run the scene's editor flow:

```bash
nix develop --command Engine/Tools/Headless.sh .build/Editor_Debug/Havana \
  --scene Assets/Scenes/LastTape1999.lvl --no-audio \
  --editor-exec Assets/Scenes/LastTape1999.edscript
```

The flow checks graph compilation and GPU previews, then enters and exits Play.
Portable shader stages have also been compiled with shaderc for SPIR-V,
GLSL 430 and Metal. Rendering has been checked on Linux software Vulkan;
Metal and Direct3D rendering have not been exercised here.

The editor reports a 16-byte bgfx UniformCache leak during shutdown after graph
preview checks. This also reproduces with only the existing ShaderGraphTest
scene and Vignette graph in an isolated workspace. All flow assertions pass;
standalone scene captures shut down cleanly.
