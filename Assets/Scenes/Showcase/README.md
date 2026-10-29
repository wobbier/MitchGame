# Showcase scenes

Manual QA scenes and screenshot-regression references for the engine's major systems.

| Scene | What it shows |
|-------|---------------|
| `Lighting.lvl` | PBR metallic / roughness sphere grid, textured exhibits, neon emissives with bloom, coloured point lights on bobbing orbs, a shadowed spot light, a fire with soft particles, SSAO, procedural sky ambient, temporal anti-aliasing |
| `Playground.lvl` | Playable: third-person `CharacterController` (Move / Look / Jump / Sprint actions), orbit follow camera, crate stacks, a domino run, a kinematic sweeper in a ball pit, a wrecking ball on a distance joint, a camp fire with 3D audio, Synty props, and three `NavMeshAgent` chasers that path to the player |
| `Fog.lvl` | Volumetric height fog at dusk: a low sun shining through a slatted wall towards the camera (light shafts and shadowed volumes), a street lamp's shadowed spot cone, lanterns glowing in the haze, fogged transparents, accumulated over frames (temporal volumetric fog) |
| `Physics2D.lvl` | Box2D: a 55-box pyramid, a motorised windmill with balls dropping on it, a hinged rope bridge with crates; orthographic camera |
| `ShaderGraph.lvl` | Shader graphs (`Assets/ShaderGraphs/Examples/`): a dissolving sphere (alpha clip with an emissive edge, also in its shadow), a hologram (unlit additive fresnel and scan lines), a wind-swayed post (vertex offset with matching shadows), triplanar concrete, water from scrolling noise normals, a graph scorch decal, a graph fire particle system and a vignette post pass |
| `Decals.lvl` | Projected decals: a scorch wrapping a wall corner and a ball (angle fade where surfaces turn away), road arrows on the floor and a ramp, a glossy normal-mapped puddle with an arrow sorted on top, an emissive glyph with bloom, an untextured paint swatch |
| `SplitDiopter.lvl` | Synty Office Pack doorway shot: a near employee on the left and his boss behind a desk on the right stay sharp at independent focus depths; [setup and comparisons](SplitDiopter.md) |
| `RenderTexture.lvl` | Camera render textures: a studio set on a turntable (`Spinner`, 25°/s) filmed by a studio camera (480 × 270, every frame) and a security camera (128 × 72, every other frame, with sun shadows, ambient occlusion and volumetric fog switched off on the camera). A monitor wall shows the feeds through each kind of consumer: emissive, diffuse (lit by a spot), a shader graph (`Examples/CameraFeed`, scan lines) and the security feed. A monitor on the set is in the studio camera's own shot, so it is black in that feed (a camera never samples its own target) and shows the studio feed in the security camera's. Rebuild it, and its two `.rendertexture` assets in `Assets/Textures/RenderTexture/`, with `python3 Tools/BuildRenderTextureShowcase.py` |
| `RenderScale.lvl` | Render scaling (LOOK-S1): the Lighting set through four split-screen cameras rendering below their output, one per upscale filter. Top left Bilinear at 0.5, top right Nearest at 0.35, bottom left Pixel at 0.25 (exact 4×4 blocks), bottom right Sharp at 0.5 (bicubic + contrast-adaptive sharpening). Bloom and SSAO are off (four full post chains pass bgfx's framebuffer limit). Rebuild it with `python3 Tools/BuildRenderScaleShowcase.py` |

Scripts live in `Assets/Scripts/Showcase/` (`PlayerController`, `FollowCamera`, `Chaser`, `Spinner`, `Bobber`). The playground's navmesh is baked to `Playground.NavSurface.navmesh` (select NavSurface > Bake, or Navigation.BakeAll).

## Regression

From the project root, with a game build:

```bash
# compare with the references (exit 1 on drift); --wrapper can point the game at a virtual display
Engine/Tools/ScreenshotRegression.py --game .build/Game_linux_Debug/Game_EntryPoint_x64 \
    --reference Assets/Scenes/Showcase/Reference Assets/Scenes/Showcase/*.lvl
# accept the current look
Engine/Tools/ScreenshotRegression.py ... --update
```

Captures run 480 frames at a fixed 1/60 s (`--frame-time`), so they are repeatable; diffs land in `.tmp/ScreenshotRegression/`. A reference can also name regions that matter more than their share of the frame in `Reference/<scene>.regions.json`, each failing on its own limit:

```json
{ "Regions": [ { "Name": "Studio monitor (emissive)", "Rect": [0.1, 0.13, 0.4, 0.39], "MaxChanged": 0.1 } ] }
```

`Rect` is x, y, width, height, normalized from the top left; `MaxChanged` defaults to `--max-changed`. `RenderTexture.regions.json` holds each monitor to 10% of its own pixels, so a broken feed can't hide inside the whole frame's 3% limit (the screens are a small part of the frame).

`PlaygroundFlows.edscript` checks the playground's gameplay scripts in the editor (`Havana --scene Assets/Scenes/Showcase/Playground.lvl --editor-exec Assets/Scenes/Showcase/PlaygroundFlows.edscript`), and `DecalFlows.edscript` the decal component's editing and undo. `RenderTextureFlows.edscript` checks the render texture links, sizes and update intervals, the black self-view, live feeds while editing and in Play, undo and save/reopen (the `rtt-*` commands); `RenderTextureReloadFlows.edscript` resizes the security feed by editing its asset and puts it back, so `RunEditorFlows.py` skips it while another Havana is open.
