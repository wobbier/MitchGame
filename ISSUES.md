# MitchGame Issue Board

A lightweight Jira-style board for the MitchGame project, kept in the repository root so it travels with the code.
Statuses: **Backlog** → **To Do** → **In Progress** → **In Review** → **Done**; **Blocked** when work cannot proceed from this repo.

Each issue records the area it touches, which repository owns the change (**Game** = this repo, **Engine** = the
`Engine/` submodule, [MitchEngine](https://github.com/wobbier/MitchEngine)), what was found, what was done, and any follow-ups.
Follow-ups and newly found bugs get their own IDs (21+) at the bottom. Keep the **Changelog** in step with every edit.

## Board

| ID | Title | Status | Area | Owner |
|---:|-------|--------|------|-------|
| 1 | Implement terrain generation algorithm | Done | Terrain | Game |
| 2 | Fix terrain rendering bugs | Blocked | Terrain / Rendering | Engine |
| 3 | Optimize terrain LOD system | Blocked | Terrain / Rendering | Engine |
| 4 | Fix editor lighting issues | Blocked | Editor / Rendering | Engine |
| 5 | Implement particle system | Done | Rendering / VFX | Engine |
| 6 | Optimize asset memory | Done | Assets | Game |
| 7 | Add ECS unit tests | Done | ECS / Tests | Game + Engine |
| 8 | Refactor camera system | Done | Gameplay / Camera | Game |
| 9 | Add multiplayer networking | Done | Networking | Engine + Game |
| 10 | Update documentation | Done | Docs | Game + Engine |
| 11 | Fix Dementia module memory leaks | Blocked | Dementia | Engine |
| 12 | Improve Havana editor UI responsiveness | Blocked | Editor | Engine |
| 13 | Add new ImGUI widgets for tooling | Blocked | Editor | Engine |
| 14 | Optimize ScriptCore scripting performance | Blocked | Scripting | Engine |
| 15 | Enhance Player module networking | Blocked | Networking / Player | Engine |
| 16 | Write comprehensive tests for terrain module | Done | Terrain / Tests | Game + Engine |
| 17 | Fix editor crash on scene load | Blocked | Editor | Engine |
| 18 | Implement skybox system | Done | Rendering / Gameplay | Game + Engine |
| 19 | Optimize collision detection | Blocked | Physics | Engine |
| 20 | Add visual scripting support | Backlog | Scripting / Editor | Engine |
| 21 | Editor: generate terrain heights from noise | To Do | Terrain / Editor | Engine |
| 22 | Terrain shader: patch-local tiling varyings | To Do | Terrain / Rendering | Engine |
| 23 | Terrain atlas sampling: exact mip derivatives, aniso bias, guarded TileSize | In Progress | Terrain / Rendering | Engine |
| 24 | Terrain: merged per-terrain vertex/index buffers | To Do | Terrain / Rendering | Engine |
| 25 | Terrain: one material per terrain | To Do | Terrain / Rendering | Engine |
| 26 | Terrain: gate LOD selection and shadow caster bounds | To Do | Terrain / Rendering | Engine |
| 27 | Physics: revision-gated body sync and move events | To Do | Physics | Engine |
| 28 | Physics: allocation-free event routing and queries | In Progress | Physics | Engine |
| 29 | Physics: cheaper terrain collision cooks | To Do | Physics | Engine |
| 30 | Playable two-pawn multiplayer sample | Done | Networking / Gameplay | Game |
| 31 | Net: replicate prefab spawns from C# | In Progress | Networking | Engine |
| 32 | Net: C# session control | To Do | Networking / Scripting | Engine |
| 33 | Net: RTT-sized snapshot history | In Progress | Networking | Engine |
| 34 | Net: oversize sends and reliable starvation | In Progress | Networking | Engine |
| 35 | Net: reconnect path | To Do | Networking | Engine |
| 36 | Editor lighting: probe key independent of the camera | In Progress | Editor / Rendering | Engine |
| 37 | Editor lighting: temporal pops on rotation | To Do | Editor / Rendering | Engine |
| 38 | Havana: hierarchy, inspector and asset browser per-frame cost | To Do | Editor | Engine |
| 39 | Havana: texture viewer widgets | To Do | Editor | Engine |
| 40 | Particles: curves, mesh emitters, collision, vertex graphs | To Do | Rendering / VFX | Engine |
| 41 | Engine owns its cores, renderer, window and scene | To Do | Engine / Memory | Engine |
| 42 | Dementia::Buffer ownership | In Progress | Dementia | Engine |
| 43 | ScriptCore: cached per-phase run lists | In Progress | Scripting | Engine |
| 44 | ScriptCore: integer component ids and cheap wrappers | To Do | Scripting | Engine |
| 45 | ScriptCore: pool-driven queries and batched callbacks | To Do | Scripting | Engine |
| 46 | Editor crash: current camera destroyed | In Progress | Editor | Engine |
| 47 | Editor crash: pointer stability in CommandCache and scene streaming | In Progress | Editor / Rendering | Engine |
| 48 | Audit the remaining 4K textures | To Do | Assets | Game |
| 49 | Texture import: MaxSize setting | To Do | Assets / Engine | Engine |
| 50 | Editor rewrites .meta sidecars without a trailing newline | In Progress | Editor / Assets | Engine |
| 51 | C# Camera.FieldOfView and CameraRigs write the dead Zoom field | In Progress | Scripting / Rendering | Engine |

## Columns

### Backlog
- 20 Add visual scripting support

### To Do
- 21 Editor: generate terrain heights from noise
- 22 Terrain shader: patch-local tiling varyings
- 24 Terrain: merged per-terrain vertex/index buffers
- 25 Terrain: one material per terrain
- 26 Terrain: gate LOD selection and shadow caster bounds
- 27 Physics: revision-gated body sync and move events
- 29 Physics: cheaper terrain collision cooks
- 32 Net: C# session control
- 35 Net: reconnect path
- 37 Editor lighting: temporal pops on rotation
- 38 Havana: hierarchy, inspector and asset browser per-frame cost
- 39 Havana: texture viewer widgets
- 40 Particles: curves, mesh emitters, collision, vertex graphs
- 41 Engine owns its cores, renderer, window and scene
- 44 ScriptCore: integer component ids and cheap wrappers
- 45 ScriptCore: pool-driven queries and batched callbacks
- 48 Audit the remaining 4K textures
- 49 Texture import: MaxSize setting

### In Progress
- 23 Terrain atlas sampling: exact mip derivatives, aniso bias, guarded TileSize
- 28 Physics: allocation-free event routing and queries
- 31 Net: replicate prefab spawns from C#
- 33 Net: RTT-sized snapshot history
- 34 Net: oversize sends and reliable starvation
- 36 Editor lighting: probe key independent of the camera
- 42 Dementia::Buffer ownership
- 43 ScriptCore: cached per-phase run lists
- 46 Editor crash: current camera destroyed
- 47 Editor crash: pointer stability in CommandCache and scene streaming
- 50 Editor rewrites .meta sidecars without a trailing newline
- 51 C# Camera.FieldOfView and CameraRigs write the dead Zoom field

### In Review
- (none)

### Done
- 1 Implement terrain generation algorithm
- 5 Implement particle system
- 6 Optimize asset memory
- 7 Add ECS unit tests
- 8 Refactor camera system
- 9 Add multiplayer networking
- 10 Update documentation
- 16 Write comprehensive tests for terrain module
- 18 Implement skybox system
- 30 Playable two-pawn multiplayer sample

### Blocked
- 2 Fix terrain rendering bugs
- 3 Optimize terrain LOD system
- 4 Fix editor lighting issues
- 11 Fix Dementia module memory leaks
- 12 Improve Havana editor UI responsiveness
- 13 Add new ImGUI widgets for tooling
- 14 Optimize ScriptCore scripting performance
- 15 Enhance Player module networking
- 17 Fix editor crash on scene load
- 19 Optimize collision detection

## Issues

### 1 · Implement terrain generation algorithm
- **Status:** Done · **Area:** Terrain · **Owner:** Game
- **Description:** Create a new algorithm for procedural terrain generation based on Perlin noise.
- **Findings:** The engine already has a mature resident/streamed terrain system (`Engine/Source/Terrain/`, `Engine/Docs/Terrain.md`) and a `Noise` library in Dementia (`Modules/Dementia/Source/Math/Noise.h`: gradient noise, fBm, ridged, hybrid multifractal, Voronoi), but nothing turns noise into a terrain asset: the only generator was the hand-written bump in `Engine/Tools/BuildTerrainTest.py`, and C# has no terrain bindings yet (Terrain.md caveats).
- **Work:** Added `Tools/GenerateTerrain.py`: a pure-Python procedural generator writing version 1 terrain sources (manifest + Float32 `.thp` pages with the engine's FNV-1a checksums + `.meta`). Perlin gradient noise with a quintic fade, rotated-octave fBm, Musgrave ridged multifractal and domain warping; presets `hills`, `mountains`, `island`; heights are a pure function of the terrain-wide lattice so tiles agree on shared edges; HeightBase/HeightRange are derived so UInt16 cooks work; `--scene` writes a test scene. Generated `Assets/Terrain/Procedural.terrain` (2×2 tiles, 64 quads, 2 m spacing, seed 7) and `Assets/Scenes/Tests/TerrainProceduralTest.lvl` + `TerrainProceduralFlows.edscript`. **Verified:** 18 unit tests pass (`python3 -I -m unittest discover -s Tools/Tests`) and the editor flow passed in a headless Havana (editor_debug, lavapipe): the terrain loads as one entity, the three boxes come to rest on the noise surface in Play, save/reopen keeps the asset.
- **Follow-ups:** - 21 (Engine): an in-editor "Generate from noise" tool on top of `Noise::Fbm2` / `Ridged2` so artists don't need the script.
### 2 · Fix terrain rendering bugs
- **Status:** Blocked · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Resolve issues with texture tiling on large terrain meshes.
- **Findings:** Audited `Engine/Assets/Shaders/TerrainSurface.{vert,sh}`, `TerrainMaterial.cpp`, `TerrainTexturePacking.cpp`, `RenderCore.cpp`.
  - **Confirmed precision bug:** layer UVs come from `v_worldPos.xz - u_terrainOrigin.xy` (`TerrainSurface.sh:39-45`), both Float32 world values (`TerrainSurface.vert:9-18`; per-patch model = `glm::translate(world, Offset)` at `RenderCore.cpp:491`). At |X| ≈ 8 km the ULP is ~1 mm; with the default 4 m `TileSize` (`TerrainSurface.h:17`) one texel is ~8 mm, so UVs quantise to 1/8 texel (shimmer under camera motion); at `TileSize ≤ 1` or ≥ 30 km it reaches a whole texel. This is the "tiling on large terrains" bug.
  - Atlas path: gutters/wrap match the packer, no seam found, but explicit `texture2DLod` disables anisotropic filtering (grazing-angle blur) and the derivative scale `(u_terrainTextures.y - 4.0)` uses the mip-0 interior for every mip (LOD bias up to ~0.18 at mip 4); cell size 512 / max mip 7 are hard-coded in `TerrainMaterial.cpp:68`.
  - `RenderCore.cpp:343` divides by `TileSize` unguarded (validated on load/save only).
  - Weight sampling at patch borders is correct (shared border texels, clamped).
- **Work:** Findings and fixes written up; the fix is engine-side.
- **Follow-ups:** - 22 (Engine): tile from a patch-local varying + per-layer `fract(Offset / TileSize)` uniform computed in double; drop world-space tiling.
- 23 (Engine): exact per-mip derivative scale, aniso-aware LOD bias, cell/maxMip from `TerrainTextureSet`; guard `1.f / TileSize`.
- Blocked here: this session has no push access to MitchEngine (add_repo denied), so engine fixes are tracked, not landed.
### 3 · Optimize terrain LOD system
- **Status:** Blocked · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Improve performance by reducing draw calls for terrain LOD.
- **Findings:** Audited `RenderCore.cpp`, `Renderer.cpp`, `TerrainLod.cpp`, `ShadowCascades.cpp`, `TerrainMaterial.cpp`.
  - **One draw per patch per view; instancing is dead code.** Each patch has its own `MeshData` (own vertex buffer, `RenderCore.cpp:213-228`), its own material instance (`Mesh.cpp:59`) and weight texture; batches key on vertex buffer + `GetInstanceBatchKey`, which mixes in the per-patch weight texture handle (`TerrainMaterial.cpp:88`), so `SupportsInstancing = true` never merges anything. Every draw pays `Material::Use` (12 `std::pow` sRGB conversions, 5 uniform + 4 texture sets).
  - Shadows: casters are culled per cascade, but a large terrain in `m_casterBounds` pulls every cascade's near plane back up to 2000 m (`ShadowCascades.cpp:72-83`), so far more patches intersect each cascade.
  - CPU: `SelectTerrainLods` runs every frame per terrain, O(patches × views) in double with 5 temporary containers, and `RenderCore.cpp:329-360` rewrites all 4 layers of every patch material every frame; nothing is gated on camera pose or terrain revision.
- **Work:** Findings and a reduction plan written up; engine-side.
- **Follow-ups:** - 24 (Engine): one vertex buffer per terrain + a per-terrain index buffer concatenated from the shared (quads, level, edges) patterns, rebuilt only when the LOD choices change → one draw per terrain per view/cascade.
- 25 (Engine): one material per terrain (weights as a texture array indexed by patch id) so the batch key is patch-independent.
- 26 (Engine): gate `SelectTerrainLods` + the material loop on a hash of quantised view poses/translation/revision; member scratch buffers; exclude terrain from the cascade caster-bounds extension.
### 4 · Fix editor lighting issues
- **Status:** Blocked · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Resolve flickering in the editor's lighting preview when rotating the camera.
- **Findings:** Frame order for the editor camera is sound: `EditorCameraController::Update` moves the camera, then `EditorApp::UpdateCameras` snapshots it, then culling, clusters, cascades and fog all read that snapshot (`EditorApp.cpp:203-279`, `Renderer.cpp:1750, 2224`). No one-frame lights-vs-view mismatch. **Most likely cause (high confidence): environment-probe ping-pong.** `DynamicSky::GetEnvironmentKey` hashes the current camera's altitude at 10 m (and x/z at 250 m with clouds, `DynamicSky.cpp:795-804`); in the editor both the editor camera and the main camera render each frame but `EnvironmentLighting::Prepare` keeps one probe for all procedural-sky cameras (`EnvironmentLighting.cpp:163-213`), so when the two cameras sit in different buckets the probe recaptures every two frames and IBL ambient/specular pops. Orbiting changes altitude, so "rotating" crosses buckets. Secondary: volumetric fog drops its history when the view turns > ~25° (`PostProcess.cpp:357-360`) and switches blur kernels; clusters are built from the TAA-jittered projection (`Renderer.cpp:1092-1113`); cascade depth extension isn't rounded (`ShadowCascades.cpp:72-80`).
- **Work:** Findings written up; engine-side.
- **Follow-ups:** - 36 (Engine): key procedural probes by sky state only (or one probe per camera; `m_probes` already holds 3).
- 37 (Engine): soften the fog history cut, build clusters from the unjittered projection, round the cascade extension.
### 5 · Implement particle system
- **Status:** Done · **Area:** Rendering / VFX · **Owner:** Engine
- **Description:** Create a new particle system with customizable shaders and emitter types.
- **Findings:** A particle system already exists: `ParticleSystem` (`Engine/Source/Components/Effects/`) with Point/Sphere/Hemisphere/Cone/Box emitters (+shell), world/local space, rate + burst, ranged lifetime/speed/size/rotation/spin, two start colours, size/colour/alpha over life, gravity, drag, noise, Additive/Alpha blend, Billboard/Stretched/Horizontal alignment, flipbooks, soft particles, lit particles and a **Particle shader-graph target** (`Graph` + `GraphParams`; fragment stage only). CPU simulation on jobs, instanced quads; C# exposes Play/Stop/Burst/ParticleCount. The issue text is therefore mostly satisfied; remaining gaps: curves/gradients over life (linear `mix` only), mesh/edge emitters and emit-from-surface, trails/sub-emitters/mesh particles, collision, a vertex-stage graph, GPU simulation, and property access from C#.
- **Work:** Verified against the engine: the particle system the issue asks for already exists (CPU-simulated `ParticleSystem` with five emitter shapes, world/local space, rate + bursts, ranged start values, size/colour/alpha over life, gravity/drag/noise, additive/alpha blending, billboard/stretched/flat alignment, flipbooks, soft particles, lit particles, and customizable shading through the Particle shader-graph target with per-system `GraphParams`; C# Play/Stop/Burst). `Assets/Scenes/Tests/ParticleTest.lvl` and `ApiFlows` exercise it in this repo. Nothing remains to implement for the issue as written; the extensions beyond it are tracked as #40.
- **Follow-ups:** - 40 (Engine): curve/gradient over-lifetime, mesh/edge emitters, collision, vertex-stage particle graphs, richer C# `ParticleSystem` API.
### 6 · Optimize asset memory
- **Status:** Done · **Area:** Assets · **Owner:** Game
- **Description:** Reduce memory usage by 20% for commonly used assets like textures and models.
- **Findings:** Measured with the editor's Resource Monitor (`asset-costs` report, headless Havana) on the three showcase scenes that use the big materials. Texture memory is what matters (models are < 1 MiB):
  - Playground 36.8 MiB, Lighting 65.3 MiB, Fog 33.3 MiB in total.
  - `ConcreteNormal.png` (4096², BC5, 13 mips) = 21.3 MiB and `ConcreteDiffuse.png` (4096², BC1) = 10.7 MiB appear in all three; `MarbleDark_Normal/Diffuse` add 32 MiB more to Lighting. The 4K pair is 87 % of Playground, 96 % of Fog and 49 % of Lighting.
  - Compression is already in place (`Format: Auto` → BC1/BC5 with mips for every texture; `tga` sources cook the same way), so the remaining lever is resolution. A 2K round trip of the Concrete sources loses nothing visible (PSNR 45.9 dB normal, 42.0 dB diffuse: the 4K files carry no detail above 2K), whereas `MarbleDark_Normal` is genuine 4K grain (17.9 dB) and stays.
  - The engine's quality presets already cap uploads (`MaxTextureSize` 1024 / 2048 for Low / Medium, `Texture.cpp` skips mips above the cap), so players on those presets were never paying for 4K; the default (no cap) and the showcase references were.
- **Work:** Downscaled `Assets/Textures/Concrete/ConcreteNormal.png` and `ConcreteDiffuse.png` from 4096² to 2048² (Lanczos; the sources shrink from 32 MB to 8 MB on disk too). **Measured** with the Resource Monitor after the change: Playground 36.8 → 12.8 MiB (-65 %; the pair now costs 5.3 + 2.7 MiB), which also makes Fog 33.3 → 9.3 MiB (-72 %) and Lighting 65.3 → 41.3 MiB (-37 %), well past the 20 % target for the commonly used set. **Verified visually:** the showcase screenshot regression (game build, lavapipe, 480 frames at a fixed frame time) reports 0.00 % changed pixels against the committed references for Playground (mean difference 0.17 %), Lighting (0.01 %), Fog (0.02 %) and RenderScale (0.02 %), so no reference needed updating.
- **Follow-ups:** - 48 (Game): the remaining 4K sources (`MarbleDark_*`, `BrickWall101`, `TileGroundSand118`, the Synty metallic maps) are candidates for the same measurement when their scenes are profiled.
- 49 (Engine): a per-texture `MaxSize` import setting (cook-time downscale) so artists can keep 4K sources while shipping 2K, instead of editing source files.
### 7 · Add ECS unit tests
- **Status:** Done · **Area:** ECS / Tests · **Owner:** Game + Engine
- **Description:** Write tests for core ECS components and systems to ensure stability.
- **Findings:** The engine already has a C++ ECS suite (`Engine/Tests/Source/ECSTests.cpp`: generational ids, deferred removal, stable component addresses, core filters/activation, parent destruction, GUIDs, `World::Each`, priority ordering, singletons) plus Transform/Bounds cases. What the game had nothing for was the ECS *as scripts see it* (the C# bindings), which is the surface game code actually uses.
- **Work:** Added `Assets/Scripts/Tests/EcsTests.cs`: five `[GameTest]`s on `Assets/Scenes/Tests/EcsTest.lvl` covering entity lifetime (find, rename, deferred destruction, stale generational handles), components by type and by name with reflected field round trips and `Query.WithComponent`, hierarchy (parent/children, world positions through two levels, world-pose-preserving reparent, descendant destruction), activity/layers/GUIDs, and bulk create/destroy exactness. `EcsFlows.edscript` runs them (`console game-tests EcsTests`). **Verified:** all 5 pass in a headless editor_debug Havana (`GameTests: 5 passed, 0 failed`).
- **Follow-ups:** - Engine suite gaps worth adding upstream: component removal while a core iterates, `RunsAfter` cycles, additive-scene entity GUID collisions (Engine).
### 8 · Refactor camera system
- **Status:** Done · **Area:** Gameplay / Camera · **Owner:** Game
- **Description:** Improve camera movement logic for better player control and smooth transitions.
- **Findings:** `Game/Source/Cores/CharacterCore.cpp` was a first-person controller with real defects: mouse look scaled the per-frame mouse delta by `dt` (frame-rate dependent sensitivity), movement called `CharacterController::Walk(displacement)` with a 550 m/s "speed" × dt (bypassing the controller's velocity/acceleration model), it supported exactly one character (cached raw pointers it never cleared on removal), its constructor `new`ed six `AudioSource`s it never freed (pushing the four invalid-surface sounds twice, the first four never initialised) for a portal-gun feature that had moved to C# (`Tools/BuildPortalGun.py`), and the camera child was found by name once with no recovery. `Character` was an empty, unreflected component, so nothing was tunable per scene. No smoothing or transitions existed.
- **Work:** Rewrote the pair. `Character` is now a reflected component with the tunables (walk speed, sprint/crouch multipliers, look sensitivity, stick look speed, look smoothing, pitch limit, invert Y, standing/crouch eye heights, crouch and FOV transition times, sprint FOV boost) and a per-entity `Runtime` state block. `CharacterCore` reads the project's input actions (Move / Look / Jump / Sprint / Crouch, so gamepads and rebinding work), separates mouse (per-frame) from stick (per-second) look, eases yaw/pitch, eye height and FOV with frame-rate-independent exponential smoothing, drives the controller through `SetMoveInput` + `MaxSpeed`, supports any number of characters and rebinds a missing camera child each frame. Dead portal/audio code removed. **Verified** in a headless editor_debug Havana: `CharacterFlows.edscript` (W walks the player along +Z at the configured speed with no drift; the camera stays a child at eye height facing forward) plus three `[GameTest]`s in `Assets/Scripts/Tests/CharacterTests.cs` — a direct `Jump()` lifts the capsule 0.90 → 2.05 m, a held Space key through the core does the same (0.89 → 2.04 m), and a held W walks forward within the expected speed band — all pass (`GameTests: 3 passed, 0 failed`).
- **Follow-ups:** - Mouse-look can't be injected by edscripts; a `scene-mouse-delta` automation command would let the look path be covered too (Engine).
- Head bob is available as the engine's `CameraSway` component on the camera child; not wired by default.
- The old `Portals.lvl` / `DemoScene.lvl` characters keep working with the defaults (their `Character` component had no fields).
### 9 · Add multiplayer networking
- **Status:** Done · **Area:** Networking · **Owner:** Engine + Game
- **Description:** Implement basic multiplayer functionality using the existing Net module.
- **Findings:** The Net module is complete and tested end to end (`Engine/Source/Net/`, `NetCore`, `NetLaunch`, headless Server build; C# `Net` API in `Modules/ScriptCore/Source/Net/Net.cs`: role/tick, owners, `Command`/`LocalCommand`, `SetAim`, RPC attributes, `NetClientJoined`/`NetClientLeft` events, lag-compensated raycasts). The game repo exercises it with `Assets/Scenes/Tests/NetTest.lvl` + `NetProbe.cs` (predicted dash, RPC round trip) and `RunNetSmoke.py`; nothing playable uses it, and no template or sample does. API gaps for a *playable* sample: no C# `Net.Host/Connect/Disconnect` (sessions start from the command line only), `NetIdentity` isn't a registered C# component and `InstantiatePrefab` never fills `NetIdentity::Prefab` (`NetReplication.cpp:204-212`, `SceneSerializer.cpp:1002`), so dynamically spawned pawns replicate as bare transforms; only `Dash` is a networked input action.
- **Work:** Built the playable sample: `Assets/Scenes/NetArena.lvl` (two placed pawns with `NetIdentity` + `CharacterController`, a walled 60 m arena, pillars, overview camera) and `Assets/Scripts/NetPawn.cs` (the server hands each joining client the first free pawn on `NetClientJoined` with a per-frame sweep as a safety net and releases it on `NetClientLeft`; every peer simulates from `Net.Command` / `Net.LocalCommand` (networked Move / Jump / Sprint, aim yaw via `Net.SetAim`), the owner predicts and drives a third-person follow camera; `[Replicated]` owner/jump counters). `Move`, `Jump` and `Sprint` are now `Networked` in `Assets/Config/Input.inputactions`. `Tools/TestNetArena.py` is a headless smoke: the game build hosts on a free UDP port, two autopiloted clients join (`Game.NetPawnAutoPilot` in their user settings). **Verified:** the smoke passes end to end: the server logs both hand-overs and both pawns moving, each client owns its pawn, walks 4.6–5.2 m and jumps once with 0 prediction corrections, and sees the other pawn move; the server exits when the last client leaves. Play it with `Engine/Tools/RunNetLocal.py --scene Assets/Scenes/NetArena.lvl --clients 2`.
- **Follow-ups:** - 31 (Engine): prefab spawns from C# replicate as bare transforms (`NetIdentity::Prefab` never filled); the sample places its pawns in the scene to avoid it.
- 32 (Engine): `Net.Host/Connect/Disconnect` from C# for a menu-driven session.
- The smoke rendering three lavapipe windows on one small machine shows 400–1300 ms RTT; run it alone.
### 10 · Update documentation
- **Status:** Done · **Area:** Docs · **Owner:** Game + Engine
- **Description:** Complete the Architecture.md file with detailed diagrams and explanations.
- **Findings:** `Engine/Docs/Architecture.md` (engine repo) already has a module graph, the `Engine::Init` sequence, a Mermaid frame-loop diagram, the stage table and feature-flag table, verified against recent engine commits; it is complete for the engine. What was missing was any architecture description of *this* project: the game module, where game code runs, the content/scene formats, the C# pipeline and how to verify changes. The README linked none of the docs.
- **Work:** Added `ARCHITECTURE.md` at the root (226 lines, five Mermaid diagrams: build-target graph, engine↔game lifecycle sequence, first-person character data flow, script build/hot-reload pipeline, network topology) with tables for build targets, the C++ module, update stages and the verification commands; linked it, the issue board and the engine docs from `README.md`.
- **Follow-ups:** - Keep `ARCHITECTURE.md` in step when cores/components are added (the module table) — a one-line rule for future PRs.
- Engine: `Engine/Docs/Architecture.md` could gain a diagram of the engine-owned core order inside one frame (today a flowchart of stages, not of cores).
### 11 · Fix Dementia module memory leaks
- **Status:** Blocked · **Area:** Dementia · **Owner:** Engine
- **Description:** Address memory leaks in the Dementia module's entity management system.
- **Findings:** **Mismatch:** Dementia (`Modules/Dementia/`) has no entity management; the ECS is `Engine/Source/ECS/` + `World.cpp`. Both audited. Verified **not** leaking: `ResourceCache` (keep-alive eviction + `ReleaseAll`), `EventManager` (receivers deregister in `~EventReceiver`), `JobSystem` contexts, Meyers singletons, `World::AddCore` duplicates, `ComponentPool` pages (high-water mark by design), `Reflection` registry (intentional static). Real items: (1) **engine systems are never freed** — every engine core, the window, the renderer and `CurrentScene` are raw `new` in `Engine.cpp:395-488` and neither `~Engine` nor `Engine::Shutdown` (`:1185-1230`) deletes them (process-lifetime leak; what LSan/CRT reports show); (2) `Dementia::Buffer` (`Core/Buffer.h:9-37`) owns a raw pointer with a defaulted copy constructor, so `ScopedBuffer(const Buffer&)` double-frees or leaks; `PlatformUtils::ReadBytes` returns one nobody releases (dead API today).
- **Work:** Findings written up; engine-side.
- **Follow-ups:** - 41 (Engine): own the engine cores/renderer/window/`CurrentScene` with `unique_ptr`, released in `Shutdown` after `GameWorld.reset()`.
- 42 (Engine): `Dementia::Buffer` on `unique_ptr<uint8_t[]>` with the copy constructor deleted; remove or fix `PlatformUtils::ReadBytes`.
### 12 · Improve Havana editor UI responsiveness
- **Status:** Blocked · **Area:** Editor · **Owner:** Engine
- **Description:** Optimize the editor's UI to reduce lag during scene editing.
- **Findings:** Per-frame work that scales with scene size (`Modules/Havana/Source/`): the hierarchy draws every node with no `ImGuiListClipper` and copies child vectors per node (`SceneHierarchyWidget.cpp:270-328`); the filter re-lowercases names per node per frame (`:108-143`); two full `ForEachEntity` scans per frame (`:672-680`, `SceneViewWidget.cpp:1249`); `Selection::Contains` is a linear `std::find` per row (`Selection.cpp:138`); the inspector re-serializes every component of the selection to JSON on any input frame, i.e. throughout drags (`PropertiesWidget.cpp:558-585`), and builds string keys per component per frame (`:39`); the asset browser rescans `Assets/` on every search keystroke (`AssetBrowser.cpp:936-939`).
- **Work:** Findings written up; engine-side.
- **Follow-ups:** - 38 (Engine): cached flattened hierarchy rows + list clipper, lowercase-name cache, selection set, inspector snapshot only on edit begin, in-memory asset search.
### 13 · Add new ImGUI widgets for tooling
- **Status:** Blocked · **Area:** Editor · **Owner:** Engine
- **Description:** Create custom widgets for common editor tasks like texture adjustment.
- **Findings:** Existing widgets: `HavanaUtils` (label/value layout, drag axes, editable vectors, colour/toggle buttons), `ImGuiTheme`, `CurveEditor`, reflection-driven field drawers (`ReflectionUI.cpp`), `AssetPreviewWidget` (a plain image + size). The texture inspector (`Texture.cpp:789+`) offers Type/Format/Quality combos, mips, Pixel Art and Make Sprite Sheet — no channel, mip, histogram, tiling or before/after view anywhere.
- **Work:** Proposals written up (engine-side).
- **Follow-ups:** - 39 (Engine): `HavanaUtils::TextureViewer` (zoom/pan, checkerboard alpha, channel isolate, mip slider) in `AssetPreviewWidget` and the import inspector; tiling preview; source-vs-cooked compare with PSNR; per-channel histogram; gradient/curve field drawers reusing `CurveEditor`.
### 14 · Optimize ScriptCore scripting performance
- **Status:** Blocked · **Area:** Scripting · **Owner:** Engine
- **Description:** Reduce script execution time by 15% through caching.
- **Findings:** Hot paths (`Source/Cores/Scripting/ScriptCore.cpp`, `Bindings/`, `Modules/ScriptCore/Source/`): (1) `RunList()` (`ScriptCore.cpp:239-266`) rebuilds and `std::sort`s the script run list for **every** phase — each fixed step, Update and LateUpdate; (2) every `Entity.GetComponent<T>()` / `Entity.Transform` / `Component.transform` does a string-keyed native `HasComponent` (`BindingContext.cpp:96-99`, temporary `std::string` + `std::function`) and allocates a new wrapper, so `transform.Position` in `OnUpdate` costs a lookup and a GC allocation per script per frame; (3) `World_FindAllWithComponent` scans all entities (`Query.bindings.cpp:73-83`) and `Query.Fill` may call native twice; (4) one managed transition + dictionary lookup + try/catch per script per phase (`Engine.cs:551-566`). No evidence of per-frame JSON, function-pointer re-resolution or runtime reflection. (1)+(2)+(4) plausibly reach the 15 % target in script-heavy scenes.
- **Work:** Findings written up; engine-side.
- **Follow-ups:** - 43 (Engine): cache one sorted run list per callback mask, invalidated on add/remove/enable/active/reload.
- 44 (Engine): integer component-type-id binding (`Entity_ResolveComponentType` once per `ComponentName<T>`, `Mask.test(id)` per call) and struct or cached C# component wrappers.
- 45 (Engine): pool-driven `World_FindAllWithComponent`; batch `ScriptOnUpdate/FixedUpdate/LateUpdate` into one managed call per phase.
### 15 · Enhance Player module networking
- **Status:** Blocked · **Area:** Networking / Player · **Owner:** Engine
- **Description:** Add support for more reliable client-server synchronization.
- **Findings:** The Player module (`Modules/Player/Source/main.cpp`, 40 lines) has no networking of its own: the dedicated server is the engine's `NetLaunch` in the Server config, so the work is in `Engine/Source/Net`. Audit (ranked): (1) **Delta baseline eviction on high-RTT links** — both snapshot histories are 32 ticks (`NetReplication.cpp:15`); above ~530 ms RTT at 60 Hz the server's delta baseline has left the client's history, every snapshot fails `NetSnapshotCodec::Read` and sync stalls until a full state is resent (stall/burst cycle). (2) **No fragmentation, silent oversize drops** — `SendReliable/SendUnreliable` return false above 1024 B and `NetSession::SendOn` ignores it; `OwnerState` appends unbounded `[Predicted]` bytes, so a pawn with ~950+ predicted bytes never reconciles. (3) **Reliable traffic starves unreliable state** — a late joiner's Spawn burst fills packets for several ticks (`NetConnection.cpp:114-150`), and one reliable stream head-of-line blocks RPCs behind a lost Spawn. (4) **No reconnect/resume** — `NetClient::Connect` works once, a client past the 10 s timeout is dead for good; clients are keyed by address so a restart on the same port is dropped as duplicates until the stale entry times out. (5) Prediction stops reconciling silently beyond the 128-tick history. Found sound: duplicate/out-of-order handling, 16-bit sequence wrap, spawn/snapshot ordering, interpolation underflow, clock resync, RPC reliability.
- **Work:** Findings and fixes written up; engine-side.
- **Follow-ups:** - 33 (Engine): time-based snapshot history (≥ 2×RTT) or full-state fallback when the acked tick leaves history.
- 34 (Engine): log/assert oversize sends in `SendOn`, cap `[Predicted]` state in NetGenerator, reserve a per-packet byte floor for unreliable state.
- 35 (Engine): reconnect path (client token in Hello, `Net.Reconnect` + `NetDisconnected` retry) and a stale-reconcile stat.
### 16 · Write comprehensive tests for terrain module
- **Status:** Done · **Area:** Terrain / Tests · **Owner:** Game + Engine
- **Description:** Create unit tests covering all terrain generation and rendering cases.
- **Findings:** Terrain is already the engine's most-tested system: `Engine/Tests/Source/Terrain*Tests.cpp` (addressing, borders, serialization, LOD topology, streaming, textures, editing, recovery, files, runtime) plus 30 `Terrain*Flows.edscript` fixtures in this repo. What was missing: tests for procedural *generation* (there was no generator) and any end-to-end check that the collision the engine builds agrees with the data in the pages.
- **Work:** Generation: 18 unit tests in `Tools/Tests/test_generate_terrain.py` (noise properties, determinism, shared edges, format/checksum round trip, corruption detection, settings validation, scene output, CLI). Runtime: `Assets/Scripts/Tests/TerrainTests.cs`, four `[GameTest]`s on the procedural scene that raycast the physics terrain at five lattice points and one in-quad point and compare with the generator's exact Float32 heights (±2 cm), check the reflected component, and that boxes rest on the surface; `TerrainProceduralFlows.edscript` runs them. **Verified:** the flow passes in a headless editor_debug Havana with `GameTests: 4 passed, 0 failed` (the first run caught a sample point sitting under a physics box; moved).
- **Follow-ups:** - Render-side coverage: a screenshot reference for `TerrainProceduralTest.lvl` once the look is final (then the Showcase regression can carry it).
### 17 · Fix editor crash on scene load
- **Status:** Blocked · **Area:** Editor · **Owner:** Engine
- **Description:** Resolve segmentation fault when loading large scenes in Havana editor.
- **Findings:** Ranked segfault candidates: (1) **`Camera::CurrentCamera` null deref** — `~Camera` nulls it (`Camera.cpp:81-85`) and only `CameraCore::Init` (which runs *before* `World::Unload`) or a new camera's `Init` repopulates it; `EditorApp.cpp:249/256` and `AssetPreviewWidget.cpp:94` deref it every editor frame, so destroying the current camera outside `LoadSceneInternal` (deleting the camera entity, unloading an additive scene, a camera that fails to deserialize) crashes next frame. (2) `CommandCache<T>::Get` returns pointers into a reallocating `std::vector` (`CommandCache.h:31-82`); every camera/mesh push can move all `CameraData*` / `MeshCommand*` — bigger scenes, more pushes; `CameraCore::OnEntityRemoved` also derefs `camData->Buffer` unchecked. (3) `SceneStreaming::Pump` holds an `Entry&` across instantiation while `m_scenes.push_back` can reallocate (`SceneStreaming.cpp:123-150`). (4) `World::SyncEntity` iterates `m_sortedCores` while `OnEntityAdded → AddCore → SortCores` can clear it. Verified safe: paged address-stable component storage, deque entity records, flat (non-recursive) scene deserialization, queued scene loads.
- **Work:** Findings written up; engine-side.
- **Follow-ups:** - 46 (Engine): fall back to `DefaultCamera` when the current camera is destroyed; null-check the three editor sites.
- 47 (Engine): address-stable `CommandCache` (deque/paged or ids) and a null-check in `CameraCore::OnEntityRemoved`; index loop in `SceneStreaming::Pump`; iterate a copy of `m_sortedCores` in `World::SyncEntity`.
### 18 · Implement skybox system
- **Status:** Done · **Area:** Rendering / Gameplay · **Owner:** Game + Engine
- **Description:** Create a dynamic skybox system with day/night cycles and weather effects.
- **Findings:** The engine already ships a full procedural sky: `DynamicSky` (atmosphere tables, sun/moon/stars/Milky Way, volumetric clouds with wind, the sky's own directional light, per-camera `ProceduralSkySettings`: Time, TimeScale, Latitude, Month, Turbidity, moon, clouds, wind) selected with the camera's `ClearType = Procedural`, plus textured sky boxes. So a "skybox system" exists; what the project lacked was a gameplay-facing day/night and weather driver and events for gameplay to react to.
- **Work:** Added `Assets/Scripts/DayNightCycle.cs`: owns the clock (24 h per `DayLengthSeconds`, wrapping; writes the camera's authored `ProceduralSky.Time` so the inspector and automation stay authoritative), four weather presets (Clear, Cloudy, Overcast, Storm: cloud coverage/density, wind, haze) blended with a frame-rate-independent exponential ease, an optional automatic weather cycle, `SetHour` / `SetWeather` / `Phase` / `IsNight`, `DayPhaseChanged` and `WeatherChanged` EventBus events, and inspector buttons. `Assets/Scripts/NightLight.cs` shows gameplay reacting: lamps subscribe to `DayPhaseChanged` and fade on for Dusk/Night. `Assets/Scenes/Tests/DayNightTest.lvl` (procedural sky over the Perlin terrain, two lamps) + `DayNightFlows.edscript`. **Verified:** the flow passes headlessly: Dawn → Day → Dusk → Night at the expected hours while the weather cycles Clear → Cloudy → Overcast → Storm, both lamps switch off at Dawn and on at Dusk (intensity reaches 8), the sky fields follow the script, and Stop restores the authored time; the Day capture shows sun shadows and clouds.
- **Follow-ups:** - Weather could also drive the `PostProcess` fog density and an `AudioSource` (rain/wind) through the same presets.
- Engine: expose `ProceduralSkySettings` as a typed C# wrapper instead of field paths.
### 19 · Optimize collision detection
- **Status:** Blocked · **Area:** Physics · **Owner:** Engine
- **Description:** Reduce physics calculation time by 25% for complex object interactions.
- **Findings:** Audited `PhysicsCore.cpp`, `CollisionRouter.cpp`, `TerrainCollisionCook.cpp`.
  - **Full passes every fixed step regardless of sleep:** `SyncBodies` (`PhysicsCore.cpp:761-921`) walks every entity (6 `TryGetComponent` each), builds two `unordered_map`s + a vector per owner, sorts, and recomputes `ComputeShapeSignature` for every body; `FixedUpdate` then loops all bodies twice and `WritePoses` (`:1479-1530`) allocates, walks parent chains for depth and `stable_sort`s each step (up to 8 steps/frame). Box3D's `b3Body_IsAwake` / `b3World_GetBodyEvents` are unused by the core.
  - Event routing: `events.swap(m_pendingEvents)` (`:1467`) drops capacity every step; `CollisionRouter::Deliver` copies a `std::function` per listener and resolves targets with parent walks + 2 `TryGetComponent`s per side.
  - Queries: `RaycastAll` / `OverlapSphere` / `OverlapBox` return `std::vector` by value and dedup with linear `std::find` (O(n²)).
  - Terrain cooks weld an already-indexed grid (`weldVertices = true`) and run synchronously on the main thread for resident terrain; `kSubSteps = 4` is fixed.
- **Work:** Findings and the top-3 plan written up; engine-side.
- **Follow-ups:** - 27 (Engine): structure-revision-gated `SyncBodies` and move-event-driven pose capture/write (the bulk of non-solver time in static-heavy scenes).
- 28 (Engine): keep `m_pendingEvents` capacity, call listeners by reference, cache body depth; out-param/`span` overloads of `RaycastAll`/`Overlap*` with sorted dedup.
- 29 (Engine): terrain cook without welding, on the job system, N concurrent streamed cooks; `kSubSteps` in Project Settings.
### 20 · Add visual scripting support
- **Status:** Backlog · **Area:** Scripting / Editor · **Owner:** Engine
- **Description:** Integrate a node-based visual scripting system for non-programmers.
- **Findings:** Feasibility: the shader-graph stack (`Graph`/`Node`/`Link` with JSON serialization, the typed `PinDef`/`NodeDef` registry, `ShaderGraphDocument` with undo/dirty/automation, on `imgui-node-editor`) is a 60-70% starting point. Missing for gameplay graphs: non-shader value types (Entity, String, Event), execution-flow pins (today a pure dataflow DAG with one output), a C# codegen or interpreter `Compiler` target, event/entry nodes and variables, a runtime host component plus the ScriptCore side, and live debugging. `Graph.h` hard-codes shader targets, so fork rather than share.
- **Work:** —
- **Follow-ups:** - Spike a `GameGraph` fork of `Graph`/`NodeDef` with exec pins and a C# codegen compiler before committing to the feature (Engine).
## Follow-ups and new issues

### 21 · Editor: generate terrain heights from noise
- **Status:** To Do · **Area:** Terrain / Editor · **Owner:** Engine
- **Description:** Expose Dementia's Noise (fBm, ridged, hybrid multifractal, Voronoi) as a terrain authoring tool in Havana's Terrain panel: seed, frequency, octaves, amplitude, preset; writes into the TerrainDocument as one undo step. Tools/GenerateTerrain.py is the offline reference implementation.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 22 · Terrain shader: patch-local tiling varyings
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Replace world-space layer UVs with a patch-local varying plus per-layer fract(Offset / TileSize) uniforms computed in double (see #2).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 23 · Terrain atlas sampling: exact mip derivatives, aniso bias, guarded TileSize
- **Status:** In Progress · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Per-mip interior in the derivative scale, aniso-aware LOD bias, cell size and max mip from TerrainTextureSet, guard 1/TileSize in RenderCore.cpp:343 (see #2).
- **Findings:** —
- **Work:** Engine (branch engine-fixes in the submodule checkout, pushed to MitchEngine overhaul once verified): `RenderCore.cpp` divides by `max(TileSize, 0.01)`; `TerrainMaterial::Use` takes the atlas cell size and last mip from `TerrainTextureSet` instead of the hard-coded 512 / 7. The aniso-aware LOD bias and exact per-mip derivative scale are still open.
- **Follow-ups:** —

### 24 · Terrain: merged per-terrain vertex/index buffers
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** One vertex buffer per terrain and a per-terrain index buffer built from the shared stitched patterns, rebuilt only on LOD-choice change: one draw per terrain per view/cascade (see #3).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 25 · Terrain: one material per terrain
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Weights as a texture array indexed by patch id so TerrainMaterial::GetInstanceBatchKey no longer varies per patch (see #3).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 26 · Terrain: gate LOD selection and shadow caster bounds
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Skip SelectTerrainLods and the per-patch material rewrite when view poses and the terrain revision are unchanged; exclude terrain from the cascade caster-bounds extension (see #3).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 27 · Physics: revision-gated body sync and move events
- **Status:** To Do · **Area:** Physics · **Owner:** Engine
- **Description:** Only re-resolve owners/signatures when a physics structure revision changed; capture/write poses from Box3D move events instead of all bodies (see #19).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 28 · Physics: allocation-free event routing and queries
- **Status:** In Progress · **Area:** Physics · **Owner:** Engine
- **Description:** Keep m_pendingEvents capacity, call listeners by reference, cache body depth; span/out-param RaycastAll and Overlap* with O(n log n) dedup (see #19).
- **Findings:** —
- **Work:** Engine: `PhysicsCore` delivers collision events from a member buffer swapped back after delivery, so neither vector reallocates every fixed step. Listener-by-reference was deliberately not done (the copy protects against a callback unsubscribing and the listener vector rehashing); the O(n²) overlap dedup stays (result counts are tiny).
- **Follow-ups:** —

### 29 · Physics: cheaper terrain collision cooks
- **Status:** To Do · **Area:** Physics · **Owner:** Engine
- **Description:** No vertex welding for grid tiles, cook resident tiles on the job system, allow concurrent streamed cooks, expose sub-steps in Project Settings (see #19).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 30 · Playable two-pawn multiplayer sample
- **Status:** Done · **Area:** Networking / Gameplay · **Owner:** Game
- **Description:** NetArena scene + NetPawn.cs: pawns placed in the scene, NetClientJoined → Net.SetOwner, Move/Jump/Sprint marked Networked, aim via Net.SetAim; run with RunNetLocal.py --clients 2 (see #9).
- **Findings:** —
- **Work:** Done as part of #9: NetArena.lvl + NetPawn.cs + Tools/TestNetArena.py, verified headlessly.
- **Follow-ups:** —

### 31 · Net: replicate prefab spawns from C#
- **Status:** In Progress · **Area:** Networking · **Owner:** Engine
- **Description:** Copy the entity's PrefabAsset into NetIdentity::Prefab at spawn and register NetIdentity as a C# component (see #9).
- **Findings:** —
- **Work:** Engine: a dynamic spawn whose `NetIdentity.Prefab` is empty takes the entity's `PrefabAsset` (what `World.Instantiate` / `CreateFromPrefab` recorded), so prefab spawns replicate as that prefab; `NetIdentity` is registered as a script component. Docs updated.
- **Follow-ups:** —

### 32 · Net: C# session control
- **Status:** To Do · **Area:** Networking / Scripting · **Owner:** Engine
- **Description:** Net.Host(port) / Net.Connect(host) / Net.Disconnect() script API so menus can start and stop sessions (see #9).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 33 · Net: RTT-sized snapshot history
- **Status:** In Progress · **Area:** Networking · **Owner:** Engine
- **Description:** Time-based snapshot history (≥ 2×RTT) or full-state fallback when the acked tick has left the 32-tick history (see #15).
- **Findings:** —
- **Work:** Engine: clients keep 128 decoded snapshots (`kReceivedHistory`) as delta baselines, the server its 32 sent (`kSentHistory`), so the baseline still exists when the server's delta arrives a round trip later (stall threshold moves from ~530 ms to ~2 s RTT at 60 Hz). Docs updated.
- **Follow-ups:** —

### 34 · Net: oversize sends and reliable starvation
- **Status:** In Progress · **Area:** Networking · **Owner:** Engine
- **Description:** Log/assert when SendReliable/SendUnreliable fail in SendOn, cap [Predicted] state size in NetGenerator, reserve a per-packet byte floor for unreliable state (see #15).
- **Findings:** —
- **Work:** Engine: `NetSession::SendOn` logs (once a second) a message it had to drop for exceeding 1024 bytes instead of failing silently; `NetConnection::SendPacket` reserves room in each packet for the largest unreliable message queued that tick, so Spawn bursts no longer starve snapshots and owner state. Docs updated. Capping `[Predicted]` state in NetGenerator is still open.
- **Follow-ups:** —

### 35 · Net: reconnect path
- **Status:** To Do · **Area:** Networking · **Owner:** Engine
- **Description:** Client token in Hello to adopt a stale same-address entry, Net.Reconnect plus a NetDisconnected retry policy, a stale-reconcile stat (see #15).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 36 · Editor lighting: probe key independent of the camera
- **Status:** In Progress · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Drop or coarsen m_cameraKm in DynamicSky::GetEnvironmentKey, or keep one procedural probe per camera, so the editor and main cameras stop fighting over the single probe (see #4).
- **Findings:** —
- **Work:** Engine: `DynamicSky` quantises the camera terms of the environment-probe key to 1 km of altitude and 4 km of travel (was 10 m / 250 m), so the editor and main cameras, which share the one procedural probe, stop recapturing it in turns while orbiting. Docs updated.
- **Follow-ups:** —

### 37 · Editor lighting: temporal pops on rotation
- **Status:** To Do · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Soften the volumetric fog history cut, build light clusters from the unjittered projection, round the cascade depth extension (see #4).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 38 · Havana: hierarchy, inspector and asset browser per-frame cost
- **Status:** To Do · **Area:** Editor · **Owner:** Engine
- **Description:** Flattened visible-row cache with ImGuiListClipper, lowercase-name filter cache, selection set lookup, inspector JSON snapshot on edit begin only, in-memory asset search (see #12).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 39 · Havana: texture viewer widgets
- **Status:** To Do · **Area:** Editor · **Owner:** Engine
- **Description:** Channel/mip/tiling viewer, source-vs-cooked compare with PSNR, per-channel histogram in AssetPreviewWidget and the texture import inspector; gradient/curve field drawers (see #13).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 40 · Particles: curves, mesh emitters, collision, vertex graphs
- **Status:** To Do · **Area:** Rendering / VFX · **Owner:** Engine
- **Description:** Curve/gradient over lifetime, mesh/edge emitters and emit-from-surface, depth or raycast collision, vertex-stage particle shader graphs, property access from C# (see #5).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 41 · Engine owns its cores, renderer, window and scene
- **Status:** To Do · **Area:** Engine / Memory · **Owner:** Engine
- **Description:** unique_ptr ownership released in Engine::Shutdown after GameWorld.reset(), in reverse creation order (see #11).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 42 · Dementia::Buffer ownership
- **Status:** In Progress · **Area:** Dementia · **Owner:** Engine
- **Description:** unique_ptr<uint8_t[]> storage, copy constructor deleted; remove or fix PlatformUtils::ReadBytes (see #11).
- **Findings:** —
- **Work:** Engine: `Dementia::Buffer` owns its bytes through `unique_ptr<uint8_t[]>`, is move-only (copying shared the allocation and double freed on Release) and exposes `Data()`; the broken, unused `ScopedBuffer` is gone; `PlatformUtils::ReadBytes` updated.
- **Follow-ups:** —

### 43 · ScriptCore: cached per-phase run lists
- **Status:** In Progress · **Area:** Scripting · **Owner:** Engine
- **Description:** Keep one sorted run list per callback mask, invalidated on entity add/remove, enable/active changes and script reload instead of rebuilding and sorting every phase (see #14).
- **Findings:** —
- **Work:** Engine: `ScriptCore` keeps one ordered script list, re-sorted only when a script joins, leaves or starts or the scripts reload; every fixed step, update and late update filters it without sorting or allocating.
- **Follow-ups:** —

### 44 · ScriptCore: integer component ids and cheap wrappers
- **Status:** To Do · **Area:** Scripting · **Owner:** Engine
- **Description:** Resolve component names to type ids once per ComponentName<T>, test the entity mask per call, make C# component wrappers structs or cache them per script (see #14).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 45 · ScriptCore: pool-driven queries and batched callbacks
- **Status:** To Do · **Area:** Scripting · **Owner:** Engine
- **Description:** World_FindAllWithComponent from the component pool entries; one managed transition per phase for OnUpdate/OnFixedUpdate/OnLateUpdate (see #14).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 46 · Editor crash: current camera destroyed
- **Status:** In Progress · **Area:** Editor · **Owner:** Engine
- **Description:** Reset Camera::CurrentCamera to DefaultCamera when a camera is destroyed; null-check EditorApp.cpp:249/256 and AssetPreviewWidget.cpp:94 (see #17).
- **Findings:** —
- **Work:** Engine: `Camera::FallbackCamera` (CameraCore's default camera) replaces a destroyed current camera in `~Camera`; `CameraCore::OnEntityRemoved` hands a removed current camera back to the default one; the unguarded readers in `EditorApp.cpp` (environment camera, post settings), `AssetPreviewWidget.cpp` and `RmlUiCore.cpp` (camera cache lookup) are null-checked.
- **Follow-ups:** —

### 47 · Editor crash: pointer stability in CommandCache and scene streaming
- **Status:** In Progress · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Address-stable CommandCache storage, null-check in CameraCore::OnEntityRemoved, index loop in SceneStreaming::Pump, iterate a copy of m_sortedCores in World::SyncEntity (see #17).
- **Findings:** —
- **Work:** Engine: `CommandCache<T>` stores its commands in a `std::deque`, so the `CameraData*` / `MeshCommand*` pointers callers keep survive later pushes; `CameraCore::OnEntityRemoved` null-checks the cache slot. The `SceneStreaming::Pump` index loop and the `m_sortedCores` copy are still open.
- **Follow-ups:** —

### 48 · Audit the remaining 4K textures
- **Status:** To Do · **Area:** Assets · **Owner:** Game
- **Description:** Measure MarbleDark_*, BrickWall101, TileGroundSand118 and the Synty metallic maps with the Resource Monitor and the 2K round-trip PSNR; downscale the ones that carry no 4K detail (see #6).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 49 · Texture import: MaxSize setting
- **Status:** To Do · **Area:** Assets / Engine · **Owner:** Engine
- **Description:** A per-texture MaxSize import setting that downscales at cook time, so 4K sources can ship as 2K without editing the files (see #6).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 50 · Editor rewrites .meta sidecars without a trailing newline
- **Status:** In Progress · **Area:** Editor / Assets · **Owner:** Engine
- **Description:** Opening a project in Havana rewrites unchanged sidecars (seen: Engine/Assets/Shaders/OutlineHull*.meta, Post/Outline.frag.meta, Assets/Terrain/Procedural.terrain.meta) with 4-space indentation and no final newline, dirtying the engine submodule and every game checkout. The metadata writer should keep the file byte-identical when nothing changed (and end with a newline).
- **Findings:** —
- **Work:** Engine: `MetaBase::Save` writes sidecars with a trailing newline and treats a file that differs only by its final newline as unchanged, so opening a project no longer dirties checkouts.
- **Follow-ups:** —

### 51 · C# Camera.FieldOfView and CameraRigs write the dead Zoom field
- **Status:** In Progress · **Area:** Scripting / Rendering · **Owner:** Engine
- **Description:** Camera::Zoom is a hidden legacy field nothing reads (the projection uses the private m_FOV, reflected as FieldOfView), yet ScriptCore's Camera.FieldOfView property, Kit/CameraRigs.cs and CameraRigFlows go through "Zoom"; many scenes still author "Zoom". Route the wrapper to FieldOfView and migrate Zoom on load (found by the review of #8, where the sprint FOV boost had no visible effect).
- **Findings:** —
- **Work:** Engine: C# `Camera.FieldOfView` and the `CameraBrain` rig read and write the reflected `FieldOfView` (the field the projection uses) instead of the dead `Zoom`. Scenes were left alone: 54 cameras (showcase references among them) author only `Zoom`, so migrating them on load would change their look and needs a separate decision. Game: `CameraRigTest.lvl` authors `FieldOfView` 55 and `CameraRigFlows` asserts it.
- **Follow-ups:** - Decide whether to migrate `Zoom`-only cameras to `FieldOfView` on load (and refresh the showcase references), or keep the hidden field as a no-op forever.
## Changelog

- 2026-11-04 · Board created from the imported issue list (20 issues).
- 2026-11-04 · #1 Perlin terrain generator (Tools/GenerateTerrain.py), Procedural.terrain asset, TerrainProceduralTest scene + flow, 18 unit tests; #21 opened.
- 2026-11-04 · #2 #3 #19 audited (terrain tiling precision, terrain draw calls, physics sync cost): findings recorded, engine follow-ups #22-#29 opened; marked Blocked (no MitchEngine push access from this session).
- 2026-11-04 · Audits recorded for #4 #5 #9 #12 #13 #15 #20; follow-ups #30-#40 opened. Board header repaired (a helper bug had merged the Columns and Issues sections).
- 2026-11-04 · #1 verified in the editor (TerrainProceduralFlows passed headlessly) → Done. #11 #14 #17 audited; follow-ups #41-#47 opened.
- 2026-11-04 · #7 C# ECS tests verified in the editor (5/5) → Done.
- 2026-11-04 · #10 ARCHITECTURE.md (game-level architecture with diagrams) + README links → Done.
- 2026-11-04 · Board brought up to date with in-flight work: #6 measurements + Concrete downscale, #8 character rewrite, #16 TerrainTests.cs, #18 DayNightCycle.cs, #9/#30 NetArena sample; #48 #49 opened. Verifications pending on the editor rebuild and the game build.
- 2026-11-04 · #50 opened (editor dirties .meta files); #18 flow passed, #8 flow caught two test-script mistakes (fixed, rerunning).
- 2026-11-04 · #6 verified: Playground 36.8 → 12.8 MiB and 0.00 % regression change on all four Concrete scenes → Done. NetArena smoke passed end to end (ownership, prediction, remote pawns) but the autopilot walks off the floor; fixing the arena.
- 2026-11-04 · #9 / #30 NetArena sample verified by the headless smoke → Done.
- 2026-11-04 · #16 (TerrainTests 4/4 in the editor) and #18 (DayNight + lamps flow) → Done.
- 2026-11-04 · #8 verified (CharacterFlows + 3 play-mode tests incl. both jump paths) → Done.
- 2026-11-04 · #5 closed: the particle system exists in the engine (customizable shaders via the Particle graph target, five emitter shapes); extensions tracked in #40.
- 2026-11-04 · Adversarial review of the new code (41 agents, 18 candidates, 8 confirmed) fixed: sprint FOV wrote the dead Camera.Zoom (#51 opened for the engine side), initial yaw via Euler folding, NetPawn session events never subscribed outside the editor, NightLight reload resync, per-client Xvfb displays in the NetArena smoke, terrain in-quad tolerance, two ARCHITECTURE.md corrections; my scenes now author FieldOfView.
- 2026-11-04 · Re-verified after the review fixes: CharacterFlows (3/3 play-mode tests), TerrainProceduralFlows (4/4) and the NetArena smoke all pass on a rebuilt editor.
- 2026-11-05 · Engine push access granted: clone at /home/user/mitchengine (overhaul). First engine batch implemented in the submodule checkout: #23 (partial) #28 (partial) #31 #33 #34 #36 #42 #43 #46 #47 (partial) #50 #51; building and verifying.
