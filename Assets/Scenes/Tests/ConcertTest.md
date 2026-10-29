# Concert arena lighting study

Open **Assets/Scenes/Tests/ConcertTest.lvl** in Havana and press Play. The camera
looks down from the seating bowl toward a singer on a small circular stage.
The photo's red floor guides are interpreted as the arena footprint; the green
beam guides become actual light scattering in the fog.

![Concert arena preview](Reference/ConcertTest.png)

The arena has a 34 × 64 m floor, stepped seating, roof trusses, a runway to the
rear stage with its LED wall, a small mixing position, a camera operator in a stand
aisle whose camera puts the singer on the LED wall, and 2,255 static audience
figures. Most of the venue stays in darkness. Raised hands, scattered phones and
dim aisle markers give the crowd scale without filling the arena with light.

## Light controls

| Select in the hierarchy | What it controls |
| --- | --- |
| **Performer Spotlight** | Narrow, warm-white followspot from the upper left, aimed at the singer. The inner/outer cone half-angles are 1.8°/3.0°; the gap between them is the feathered edge. |
| **Box light beam 1-1** through **Box light beam 4-3** | Twelve cool-white **Rectangle** lights, each the size of its luminous face (0.79 × 0.47 m). A rectangle's beam leaves the whole panel and spreads through the **Inner / Outer Cone Angle** (2°/5.5°), measured from the panel's edge, so the twelve soft-edged beams overlap into one wash. Intensity 10,000 per panel (an area source puts far more light into the haze beside its face than a point spot of the same figure). |
| **Crowd Wash** | Transform group containing the twelve fixtures. The emitters fan gently outward by column and row to cover the stage surroundings and crowd. |
| **Box Light Bank** | The suspended 3-column × 4-row bank. Moving or rotating this group moves all twelve fixtures and their individual lights together. |
| **LED video wall** | The screen behind the main stage: a dark panel whose emission is the crowd camera's live feed (`Assets/Textures/ConcertTest/LedWall.rendertexture` in its Emissive slot, intensity 5), shown upright with Tiling (1, -1) and Offset (0, 1). **LED video wall glow** is a wall-sized rectangle light with an 89° cone that casts the screen's light into the haze and onto the main stage. |
| **Crowd Camera** (in **Camera crew - stand aisle**) | The camera crew: an operator on a riser in a stand aisle, and a broadcast camera filming the singer with a 6° lens. It renders every frame into the LED wall's render texture (384 × 200, close to the wall's shape) instead of the screen, with sun shadows, ambient occlusion and volumetric fog switched off on the camera; its own **PostProcess** keeps analytic fog, bloom and fixed exposure. Move or re-aim it and the wall follows, in the editor and in Play. |
| **Main Camera → PostProcess** | Fog, volumetric scattering (temporal, 64 steps, local-light anisotropy), bloom and fixed exposure. |

The performer light casts shadows. Rectangle lights are unshadowed extended
emitters; each still lights surfaces and scatters through the native volumetric
fog pass, where its beam starts the full panel size instead of as a point. The
fixture and its emitter share the same aim. **Outer Cone Angle** sets a panel's
beam size and **Inner Cone Angle** how much of it is full intensity; widen the gap
for a softer edge.

Set an individual beam's **Intensity** to zero to disable that panel's beam. To isolate
one panel, disable the performer light and the other eleven bank lights. Turn
**Fog** off to compare the surface illumination with
the beam silhouettes removed. **FogDensity** controls the haze; **FogSunIntensity**
also scales local-light scattering, despite its name, and **Local Light Anisotropy**
makes the beams glow more where they point towards the camera. **Volumetric
Temporal** accumulates the half-resolution raymarch over frames (turn it off to see
a single frame's jitter). A low height falloff keeps fog around the ceiling
fixtures. Exposure is fixed so the dark room does not brighten automatically when
one light is disabled.

The zero-intensity **Indoor ambient - suppress sky fallback** directional is
intentional: it suppresses the renderer's automatic daylight fallback for a
solid-color camera. It contributes no illumination.

## Rebuild and verify

```bash
python3 Tools/BuildConcertTest.py

Engine/Tools/NixEnv.sh Engine/Tools/Headless.sh \
  .build/Game_linux_Debug/Game_EntryPoint_x64 \
  --scene Assets/Scenes/Tests/ConcertTest.lvl \
  --frames 32 --frame-time 0.016666667 --width 1280 --height 800 \
  --no-audio --no-debug-overlay --screenshot .tmp/ConcertTest/concert.png --exit

Engine/Tools/NixEnv.sh Engine/Tools/Headless.sh \
  .build/Editor_Debug/Havana --scene Assets/Scenes/Tests/ConcertTest.lvl \
  --editor-exec Assets/Scenes/Tests/ConcertTest.edscript
```

The builder overwrites this scene, the LED wall's render texture (`LedWall.rendertexture`
and its `.meta`) and, when the local Synty Prototype pack is installed, its four normalized crowd OBJ assets
(without the pack the committed OBJs are reused). Save editor variations under
another name before rebuilding. It uses the Prototype pack for the static crowd
and the Office pack for the singer; source assets are left intact. Crowd meshes share geometry and opaque materials
for automatic instancing. See `Tools/ConcertAssets.py` and
`Assets/Models/ConcertTest/README.md` for the asset sources.

The editor flow checks all twelve emitters, their independent intensity and cone
controls, save/reopen, fog settings, undo and Play/Stop. **Crowd Wash** contains no shared
Light component. The flow also checks the crowd camera's feed with the `rtt-*` commands:
the camera isn't the current one, its pass switches are off, the camera and wall links
survive save/reopen, the texture is 384 × 200, it renders every frame with a lit image,
and dousing the followspot changes it, while editing and in Play. Comparison captures in
`.tmp/ConcertTestFlows/` show the complete scene, the bank alone, one panel alone, the
performer alone, fog disabled and the restored scene, plus the feed itself
(`crowd-feed.png`) and the crowd camera's inspector.

RunChecks' test-scene screenshots compare the game's capture with
`Reference/ConcertTest.png`. `Reference/ConcertTest.regions.json` also holds the LED
wall to 8% changed pixels on its own, so a broken feed can't hide inside the whole
frame's 3% limit.
