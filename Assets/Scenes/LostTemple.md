# The Lost Temple

A rendering showcase built from the Synty Explorer Kit. A December sun sets ten degrees above the
horizon over a jungle gorge. A stepped temple stands in the clearing, its shrine glowing, and a
waterfall drops into a plunge pool. An expedition has made camp in front of it: a jeep with its
headlights on, a camp fire and a map table. The surveyor reads the map while the expedition
leader shines a flashlight up at the temple.

The scene has 709 entities, 111 distinct Synty models and 14 shader graphs. A camera tour and
the post-process stack are set up so a camera graph (such as a camcorder pass) can be added on top.

## Running it

Open **Assets/Scenes/LostTemple.lvl** in Havana and press Play. To run it standalone on Linux,
from the repository root:

```bash
nix develop --command .build/Game_linux_Debug/Game_EntryPoint_x64 --scene Assets/Scenes/LostTemple.lvl --no-debug-overlay
```

### Camera (`LostTempleCamera`)

The camera tours seven shots on its own. Each shot holds for 9 s while drifting slowly towards
its subject, then eases over 4.5 s into the next shot.

| Control | Action |
| --- | --- |
| 1-7 | Go to a shot: the camp and temple; the camp fire; up the stairs; the shrine door; the pool and falls; high over the gorge; into the sun |
| T | Toggle the tour |
| P | Start/pause the eight-second dolly zoom (subject holds size as background perspective changes) |
| WASD, Q / E | Fly (leaves the tour) |
| Arrow keys | Look |
| Left Shift | Fly faster |
| Space | Toggle the hand-held sway |

`Shot` (the starting shot, 0-6), `Hold`, `Blend`, `Sway`, `FlySpeed` and `LookSpeed` are script fields. The shot table is
generated into `Assets/Scripts/LostTemple/LostTempleShots.cs` together with the scene.

The active Main Camera also has a **Sequence** named **Camera Dolly Zoom**. Open **View >
Sequencer** with that camera selected to scrub or edit its transform and FieldOfView keys in
edit mode. Its animation lives in `Assets/Animations/LostTempleDollyZoom.sequence`; the player
binds the asset's **Camera** slot to Main Camera. Use **Clip... > Save clip** to persist key edits to the
asset. It is off by default so the tour still starts normally. **P** starts its loop in Play.
FOV compensates for the distance to the foreground subject while focus distance follows the
camera. Press **P** again to resume manual control at the current camera pose. The standalone primitive
demo is `Assets/Scenes/Tests/SequenceTest.lvl`; see `Engine/Docs/Sequences.md` for authoring and
script controls.

### Adding a camera graph (camcorder)

The Main Camera's PostProcess runs `LostTemple/LensDirt` **Before Tonemap**. To add another
graph, such as a camcorder pass, append it to **Graphs** after LensDirt. Use **After Tonemap**
injection for a graph that works on the display image.

## What it shows

| Feature | Where |
| --- | --- |
| Procedural sky, clouds, sun-driven directional light | Main Camera > Procedural Sky (latitude 14°, December, 17:12). The Sun is an Automatic directional that follows the sky |
| Cascaded sun shadows | Long tree and temple shadows across the clearing; shadow distance 80 m |
| Volumetric height fog | Shafts from the western tree line and the natural arch; headlight and flashlight cones; glow around the torches |
| Spot-light shadows (3 of 4) | The jeep's two headlights and the leader's flashlight |
| Point-light shadows (2 of 2) | The camp fire and the idol |
| Clustered local lights | 19 point lights, including torches, fireflies (`Wander`) and mushroom glows, with the box, bar and rectangle lights below |
| Bar, box and rectangle lights | The map table's tube lamp, the glow inside the treasure chest, and the shrine doorway |
| Metallic PBR and image-based lighting | Gold coins and chest trim, wet stone, the idol |
| Decals | Two rune circles (graph), pool caustics (graph), normal-mapped cracks on the temple, jeep tyre tracks, a glossy puddle |
| Transparency | The plunge pool and the waterfall sheet |
| Particles | Graph flames on the torches and camp fire, spirit wisps (graph), stretched embers and splash, lit smoke, waterfall spray, pollen in the light and falling leaves, firefly swarm |
| Alpha-clipped foliage | Ivy cards (`FoliageCutout`), clipped in their shadows too |
| Vertex animation with matching shadows | All foliage sways in the wind (`Foliage`) |
| Skinned meshes | Both explorers, hand-posed (see below) |
| LODs | Trees, large bushes, grass fields, cliffs and the arch generate two LOD levels |
| Automatic instancing | The repeated foliage, rocks and coin piles share materials and batch |
| SSAO, TAA, bloom, eye adaptation, ACES, grading and vignette | Main Camera > PostProcess |
| Post-process graph | `LensDirt`, before tonemapping |

## Shader graphs

All graphs are in `Assets/ShaderGraphs/LostTemple/`, with their generated sources in `<Name>.sg/`.

| Graph | Target | What it does |
| --- | --- | --- |
| `AncientStone` | Lit | Triplanar rock and procedural masonry courses: running-bond blocks with bevels and mortar, and per-block colour, aligned to the temple through `Frame Yaw`. Adds moss on upward faces and in the joints, and darker, glossy stone below `Wet Height`. Used on every stone surface: cliffs, rocks, statues and the temple. |
| `JungleFloor` | Lit | Dirt and grass mixed in large noise patches, with grass normals, darker and wetter around the pool. |
| `TempleWater` | Lit, transparent | Ripples from two drifting noise layers, fresnel depth colour and foam under the falls. Specular ambient is dimmed because the gorge hides most of the sky. |
| `Waterfall` | Lit, transparent | Streaks falling in object space, foam at the base and a thin lip. |
| `IdolGold` | Lit | Polished gold with pulsing veins of light. |
| `Foliage` / `FoliageCutout` | Lit | Wind sway that grows with height and also moves the shadows. The cutout variant clips ivy leaves by alpha. A negative `Sway Height` is for hanging vines. |
| `GlowMushroom` | Lit | Breathing bioluminescent caps. |
| `SpiritBeam` | Unlit, additive | The column of light over the stair rune. |
| `RuneCircle` | Decal | Rings, a turning band of glyphs and a star, pulsing outwards. The pattern is a Custom Function. |
| `Caustics` | Decal | Animated water caustics on the pool bed, faded to a round pool. The pattern is a Custom Function. |
| `SpiritWisp` | Particle | A hot core in a torn, swirling halo. |
| `Flame` | Particle | The flame texture torn by rising noise, hotter in the core. |
| `LensDirt` | Post Process (before tonemap) | Filtered scene light catches on lens dirt, with a soft brightness threshold and slight chromatic fringing. A mip chain covers the full frame so small lights do not flash as the camera moves. The response is exposed for the actual Synty dirt texture, clearest when facing the sun (shot 7); `Dirt Intensity` controls its strength and `Glow Focus` its spread. |

## The explorers

The Synty explorers have no animation clips here, so the scene contains their expanded skeletons
with some bones turned. A saved Model reuses its node entities by name, so the pose holds in the
editor and in play. Hats, hair, the beard and the backpacks are attached to the head and
`spine_03` bones. `build_explorers` in the builder holds the poses, written as directions the
bones aim at.

## Rebuilding

```bash
python3 Tools/BuildLostTemple.py             # the scene, the shot table and the graphs
python3 Tools/BuildLostTemple.py --graphs    # the graphs only
```

Both overwrite their files, so save custom edits elsewhere first. After changing a graph,
regenerate its `.sg/` sources in either of two ways:

- Open the graph and save it in Havana.
- Run `ME_SHADERGRAPH_UPDATE=1 .build/Game_linux_Debug/MitchEngine_Tests -tc="*project graphs*"`, which updates every project graph.

The flow checks every graph and plays the scene:

```bash
Engine/Tools/Headless.sh .build/Editor_Debug/Havana --scene Assets/Scenes/LostTemple.lvl --editor-exec Assets/Scenes/LostTemple.edscript
```

### Asset notes

- **Materials.** The Explorer Kit's models reference textures from other Synty packs by old
  absolute paths. The scene gives every part an explicit material, so the models' import
  settings stay untouched. `Tools/LostTempleParts.json` records each model's part paths and
  `Tools/LostTempleRigs.json` the explorers' skeletons. Both were captured by loading the models
  in Havana.
- **LODs.** Fifteen vegetation and cliff models have `GenerateLODs` turned on in their `.meta`.
- **Orientation.** The import mirrors FBX Z, so Synty models face -Z in the engine. The waterfall
  mesh therefore curves out along -Z, and the explorers face -Z in model space.

## Vulkan program reuse

Vulkan program slots must clear sampler bindings when reused. Otherwise a shader graph can
inherit bindings for stages it doesn't declare and crash in `bgfx::vk::getDescriptorSet`.
`Engine/ThirdParty/Patches/bgfx-vulkan-program-samplers.patch` fixes `ProgramVK::create`;
the Linux Debug and Release archives include it, and `GenerateSolutions.sh --build-bgfx`
applies it before rebuilding. LostTemple's repeated Play/Stop regression passes with the fix.
