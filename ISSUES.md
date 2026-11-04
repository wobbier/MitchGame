# MitchGame Issue Board

A lightweight Jira-style board for the MitchGame project, kept in the repository root so it travels with the code.
Statuses: **Backlog** → **To Do** → **In Progress** → **In Review** → **Done**; **Blocked** when work cannot proceed from this repo.

Each issue records the area it touches, which repository owns the change (**Game** = this repo, **Engine** = the
`Engine/` submodule, [MitchEngine](https://github.com/wobbier/MitchEngine)), what was found, what was done, and any follow-ups.
Follow-ups and newly found bugs get their own IDs (21+) at the bottom. Keep the **Changelog** in step with every edit.

## Board

| ID | Title | Status | Area | Owner |
|---:|-------|--------|------|-------|
| 1 | Implement terrain generation algorithm | In Review | Terrain | Game |
| 2 | Fix terrain rendering bugs | Blocked | Terrain / Rendering | Engine |
| 3 | Optimize terrain LOD system | Blocked | Terrain / Rendering | Engine |
| 4 | Fix editor lighting issues | Blocked | Editor / Rendering | Engine |
| 5 | Implement particle system | In Review | Rendering / VFX | Engine |
| 6 | Optimize asset memory | To Do | Assets | Game |
| 7 | Add ECS unit tests | In Progress | ECS / Tests | Game + Engine |
| 8 | Refactor camera system | To Do | Gameplay / Camera | Game |
| 9 | Add multiplayer networking | In Review | Networking | Engine + Game |
| 10 | Update documentation | To Do | Docs | Game + Engine |
| 11 | Fix Dementia module memory leaks | In Progress | Dementia | Engine |
| 12 | Improve Havana editor UI responsiveness | Blocked | Editor | Engine |
| 13 | Add new ImGUI widgets for tooling | Blocked | Editor | Engine |
| 14 | Optimize ScriptCore scripting performance | In Progress | Scripting | Engine |
| 15 | Enhance Player module networking | Blocked | Networking / Player | Engine |
| 16 | Write comprehensive tests for terrain module | To Do | Terrain / Tests | Game + Engine |
| 17 | Fix editor crash on scene load | In Progress | Editor | Engine |
| 18 | Implement skybox system | To Do | Rendering / Gameplay | Game + Engine |
| 19 | Optimize collision detection | Blocked | Physics | Engine |
| 20 | Add visual scripting support | Backlog | Scripting / Editor | Engine |
| 21 | Editor: generate terrain heights from noise | To Do | Terrain / Editor | Engine |
| 22 | Terrain shader: patch-local tiling varyings | To Do | Terrain / Rendering | Engine |
| 23 | Terrain atlas sampling: exact mip derivatives, aniso bias, guarded TileSize | To Do | Terrain / Rendering | Engine |
| 24 | Terrain: merged per-terrain vertex/index buffers | To Do | Terrain / Rendering | Engine |
| 25 | Terrain: one material per terrain | To Do | Terrain / Rendering | Engine |
| 26 | Terrain: gate LOD selection and shadow caster bounds | To Do | Terrain / Rendering | Engine |
| 27 | Physics: revision-gated body sync and move events | To Do | Physics | Engine |
| 28 | Physics: allocation-free event routing and queries | To Do | Physics | Engine |
| 29 | Physics: cheaper terrain collision cooks | To Do | Physics | Engine |
| 30 | Playable two-pawn multiplayer sample | To Do | Networking / Gameplay | Game |
| 31 | Net: replicate prefab spawns from C# | To Do | Networking | Engine |
| 32 | Net: C# session control | To Do | Networking / Scripting | Engine |
| 33 | Net: RTT-sized snapshot history | To Do | Networking | Engine |
| 34 | Net: oversize sends and reliable starvation | To Do | Networking | Engine |
| 35 | Net: reconnect path | To Do | Networking | Engine |
| 36 | Editor lighting: probe key independent of the camera | To Do | Editor / Rendering | Engine |
| 37 | Editor lighting: temporal pops on rotation | To Do | Editor / Rendering | Engine |
| 38 | Havana: hierarchy, inspector and asset browser per-frame cost | To Do | Editor | Engine |
| 39 | Havana: texture viewer widgets | To Do | Editor | Engine |
| 40 | Particles: curves, mesh emitters, collision, vertex graphs | To Do | Rendering / VFX | Engine |

## Columns

### Backlog
- 20 Add visual scripting support

### To Do
- 6 Optimize asset memory
- 8 Refactor camera system
- 10 Update documentation
- 16 Write comprehensive tests for terrain module
- 18 Implement skybox system
- 21 Editor: generate terrain heights from noise
- 22 Terrain shader: patch-local tiling varyings
- 23 Terrain atlas sampling: exact mip derivatives, aniso bias, guarded TileSize
- 24 Terrain: merged per-terrain vertex/index buffers
- 25 Terrain: one material per terrain
- 26 Terrain: gate LOD selection and shadow caster bounds
- 27 Physics: revision-gated body sync and move events
- 28 Physics: allocation-free event routing and queries
- 29 Physics: cheaper terrain collision cooks
- 30 Playable two-pawn multiplayer sample
- 31 Net: replicate prefab spawns from C#
- 32 Net: C# session control
- 33 Net: RTT-sized snapshot history
- 34 Net: oversize sends and reliable starvation
- 35 Net: reconnect path
- 36 Editor lighting: probe key independent of the camera
- 37 Editor lighting: temporal pops on rotation
- 38 Havana: hierarchy, inspector and asset browser per-frame cost
- 39 Havana: texture viewer widgets
- 40 Particles: curves, mesh emitters, collision, vertex graphs

### In Progress
- 7 Add ECS unit tests
- 11 Fix Dementia module memory leaks
- 14 Optimize ScriptCore scripting performance
- 17 Fix editor crash on scene load

### In Review
- 1 Implement terrain generation algorithm
- 5 Implement particle system
- 9 Add multiplayer networking

### Done
- (none)

### Blocked
- 2 Fix terrain rendering bugs
- 3 Optimize terrain LOD system
- 4 Fix editor lighting issues
- 12 Improve Havana editor UI responsiveness
- 13 Add new ImGUI widgets for tooling
- 15 Enhance Player module networking
- 19 Optimize collision detection

## Issues

### 1 · Implement terrain generation algorithm
- **Status:** In Review · **Area:** Terrain · **Owner:** Game
- **Description:** Create a new algorithm for procedural terrain generation based on Perlin noise.
- **Findings:** The engine already has a mature resident/streamed terrain system (`Engine/Source/Terrain/`, `Engine/Docs/Terrain.md`) and a `Noise` library in Dementia (`Modules/Dementia/Source/Math/Noise.h`: gradient noise, fBm, ridged, hybrid multifractal, Voronoi), but nothing turns noise into a terrain asset: the only generator was the hand-written bump in `Engine/Tools/BuildTerrainTest.py`, and C# has no terrain bindings yet (Terrain.md caveats).
- **Work:** Added `Tools/GenerateTerrain.py`: a pure-Python procedural generator writing version 1 terrain sources (manifest + Float32 `.thp` pages with the engine's FNV-1a checksums + `.meta`). Perlin gradient noise with a quintic fade, rotated-octave fBm, Musgrave ridged multifractal and domain warping; presets `hills`, `mountains`, `island`; heights are a pure function of the terrain-wide lattice so tiles agree on shared edges; HeightBase/HeightRange are derived so UInt16 cooks work; `--scene` writes a test scene. Generated `Assets/Terrain/Procedural.terrain` (2×2 tiles, 64 quads, 2 m spacing, seed 7) and `Assets/Scenes/Tests/TerrainProceduralTest.lvl` + `TerrainProceduralFlows.edscript` (boxes settle on the noise surface in Play, save/reopen keeps the asset). 18 unit tests in `Tools/Tests/test_generate_terrain.py` (`python3 -I -m unittest discover -s Tools/Tests`).
- **Follow-ups:** - 21: an in-editor "Generate from noise" tool on top of `Noise::Fbm2` / `Ridged2` (Terrain panel, Sculpt or Tiles workspace) so artists don't need the script (Engine).
- The editor flow still has to be run against a built Havana (see the Changelog).
 —

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
- **Status:** In Review · **Area:** Rendering / VFX · **Owner:** Engine
- **Description:** Create a new particle system with customizable shaders and emitter types.
- **Findings:** A particle system already exists: `ParticleSystem` (`Engine/Source/Components/Effects/`) with Point/Sphere/Hemisphere/Cone/Box emitters (+shell), world/local space, rate + burst, ranged lifetime/speed/size/rotation/spin, two start colours, size/colour/alpha over life, gravity, drag, noise, Additive/Alpha blend, Billboard/Stretched/Horizontal alignment, flipbooks, soft particles, lit particles and a **Particle shader-graph target** (`Graph` + `GraphParams`; fragment stage only). CPU simulation on jobs, instanced quads; C# exposes Play/Stop/Burst/ParticleCount. The issue text is therefore mostly satisfied; remaining gaps: curves/gradients over life (linear `mix` only), mesh/edge emitters and emit-from-surface, trails/sub-emitters/mesh particles, collision, a vertex-stage graph, GPU simulation, and property access from C#.
- **Work:** Verified against the engine; the ask is covered except the listed extensions (#40).
- **Follow-ups:** - 40 (Engine): curve/gradient over-lifetime, mesh/edge emitters, collision, vertex-stage particle graphs, richer C# `ParticleSystem` API.
### 6 · Optimize asset memory
- **Status:** To Do · **Area:** Assets · **Owner:** Game
- **Description:** Reduce memory usage by 20% for commonly used assets like textures and models.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 7 · Add ECS unit tests
- **Status:** In Progress · **Area:** ECS / Tests · **Owner:** Game + Engine
- **Description:** Write tests for core ECS components and systems to ensure stability.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 8 · Refactor camera system
- **Status:** To Do · **Area:** Gameplay / Camera · **Owner:** Game
- **Description:** Improve camera movement logic for better player control and smooth transitions.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 9 · Add multiplayer networking
- **Status:** In Review · **Area:** Networking · **Owner:** Engine + Game
- **Description:** Implement basic multiplayer functionality using the existing Net module.
- **Findings:** The Net module is complete and tested end to end (`Engine/Source/Net/`, `NetCore`, `NetLaunch`, headless Server build; C# `Net` API in `Modules/ScriptCore/Source/Net/Net.cs`: role/tick, owners, `Command`/`LocalCommand`, `SetAim`, RPC attributes, `NetClientJoined`/`NetClientLeft` events, lag-compensated raycasts). The game repo exercises it with `Assets/Scenes/Tests/NetTest.lvl` + `NetProbe.cs` (predicted dash, RPC round trip) and `RunNetSmoke.py`; nothing playable uses it, and no template or sample does. API gaps for a *playable* sample: no C# `Net.Host/Connect/Disconnect` (sessions start from the command line only), `NetIdentity` isn't a registered C# component and `InstantiatePrefab` never fills `NetIdentity::Prefab` (`NetReplication.cpp:204-212`, `SceneSerializer.cpp:1002`), so dynamically spawned pawns replicate as bare transforms; only `Dash` is a networked input action.
- **Work:** Scoped: a two-pawn arena (pawns placed in the scene, `NetClientJoined` → `Net.SetOwner`, networked Move/Jump/Sprint actions, aim via `Net.SetAim`) is buildable today with the existing API; tracked as #30.
- **Follow-ups:** - 30 (Game): `Assets/Scenes/Showcase/NetArena.lvl` + `NetPawn.cs`, Move/Jump/Sprint marked `Networked`, wired into `RunNetLocal.py` / the net smoke.
- 31 (Engine): copy the entity's `PrefabAsset` into `NetIdentity::Prefab` at spawn and register `NetIdentity` for C#, so `World.Instantiate` spawns replicate properly.
- 32 (Engine): `Net.Host(port)` / `Net.Connect(host)` / `Net.Disconnect()` script API for menu-driven sessions.
### 10 · Update documentation
- **Status:** To Do · **Area:** Docs · **Owner:** Game + Engine
- **Description:** Complete the Architecture.md file with detailed diagrams and explanations.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 11 · Fix Dementia module memory leaks
- **Status:** In Progress · **Area:** Dementia · **Owner:** Engine
- **Description:** Address memory leaks in the Dementia module's entity management system.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Status:** In Progress · **Area:** Scripting · **Owner:** Engine
- **Description:** Reduce script execution time by 15% through caching.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 15 · Enhance Player module networking
- **Status:** Blocked · **Area:** Networking / Player · **Owner:** Engine
- **Description:** Add support for more reliable client-server synchronization.
- **Findings:** The Player module (`Modules/Player/Source/main.cpp`, 40 lines) has no networking of its own: the dedicated server is the engine's `NetLaunch` in the Server config, so the work is in `Engine/Source/Net`. Audit (ranked): (1) **Delta baseline eviction on high-RTT links** — both snapshot histories are 32 ticks (`NetReplication.cpp:15`); above ~530 ms RTT at 60 Hz the server's delta baseline has left the client's history, every snapshot fails `NetSnapshotCodec::Read` and sync stalls until a full state is resent (stall/burst cycle). (2) **No fragmentation, silent oversize drops** — `SendReliable/SendUnreliable` return false above 1024 B and `NetSession::SendOn` ignores it; `OwnerState` appends unbounded `[Predicted]` bytes, so a pawn with ~950+ predicted bytes never reconciles. (3) **Reliable traffic starves unreliable state** — a late joiner's Spawn burst fills packets for several ticks (`NetConnection.cpp:114-150`), and one reliable stream head-of-line blocks RPCs behind a lost Spawn. (4) **No reconnect/resume** — `NetClient::Connect` works once, a client past the 10 s timeout is dead for good; clients are keyed by address so a restart on the same port is dropped as duplicates until the stale entry times out. (5) Prediction stops reconciling silently beyond the 128-tick history. Found sound: duplicate/out-of-order handling, 16-bit sequence wrap, spawn/snapshot ordering, interpolation underflow, clock resync, RPC reliability.
- **Work:** Findings and fixes written up; engine-side.
- **Follow-ups:** - 33 (Engine): time-based snapshot history (≥ 2×RTT) or full-state fallback when the acked tick leaves history.
- 34 (Engine): log/assert oversize sends in `SendOn`, cap `[Predicted]` state in NetGenerator, reserve a per-packet byte floor for unreliable state.
- 35 (Engine): reconnect path (client token in Hello, `Net.Reconnect` + `NetDisconnected` retry) and a stale-reconcile stat.
### 16 · Write comprehensive tests for terrain module
- **Status:** To Do · **Area:** Terrain / Tests · **Owner:** Game + Engine
- **Description:** Create unit tests covering all terrain generation and rendering cases.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 17 · Fix editor crash on scene load
- **Status:** In Progress · **Area:** Editor · **Owner:** Engine
- **Description:** Resolve segmentation fault when loading large scenes in Havana editor.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 18 · Implement skybox system
- **Status:** To Do · **Area:** Rendering / Gameplay · **Owner:** Game + Engine
- **Description:** Create a dynamic skybox system with day/night cycles and weather effects.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Per-mip interior in the derivative scale, aniso-aware LOD bias, cell size and max mip from TerrainTextureSet, guard 1/TileSize in RenderCore.cpp:343 (see #2).
- **Findings:** —
- **Work:** —
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
- **Status:** To Do · **Area:** Physics · **Owner:** Engine
- **Description:** Keep m_pendingEvents capacity, call listeners by reference, cache body depth; span/out-param RaycastAll and Overlap* with O(n log n) dedup (see #19).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 29 · Physics: cheaper terrain collision cooks
- **Status:** To Do · **Area:** Physics · **Owner:** Engine
- **Description:** No vertex welding for grid tiles, cook resident tiles on the job system, allow concurrent streamed cooks, expose sub-steps in Project Settings (see #19).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 30 · Playable two-pawn multiplayer sample
- **Status:** To Do · **Area:** Networking / Gameplay · **Owner:** Game
- **Description:** NetArena scene + NetPawn.cs: pawns placed in the scene, NetClientJoined → Net.SetOwner, Move/Jump/Sprint marked Networked, aim via Net.SetAim; run with RunNetLocal.py --clients 2 (see #9).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 31 · Net: replicate prefab spawns from C#
- **Status:** To Do · **Area:** Networking · **Owner:** Engine
- **Description:** Copy the entity's PrefabAsset into NetIdentity::Prefab at spawn and register NetIdentity as a C# component (see #9).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 32 · Net: C# session control
- **Status:** To Do · **Area:** Networking / Scripting · **Owner:** Engine
- **Description:** Net.Host(port) / Net.Connect(host) / Net.Disconnect() script API so menus can start and stop sessions (see #9).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 33 · Net: RTT-sized snapshot history
- **Status:** To Do · **Area:** Networking · **Owner:** Engine
- **Description:** Time-based snapshot history (≥ 2×RTT) or full-state fallback when the acked tick has left the 32-tick history (see #15).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 34 · Net: oversize sends and reliable starvation
- **Status:** To Do · **Area:** Networking · **Owner:** Engine
- **Description:** Log/assert when SendReliable/SendUnreliable fail in SendOn, cap [Predicted] state size in NetGenerator, reserve a per-packet byte floor for unreliable state (see #15).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 35 · Net: reconnect path
- **Status:** To Do · **Area:** Networking · **Owner:** Engine
- **Description:** Client token in Hello to adopt a stale same-address entry, Net.Reconnect plus a NetDisconnected retry policy, a stale-reconcile stat (see #15).
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 36 · Editor lighting: probe key independent of the camera
- **Status:** To Do · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Drop or coarsen m_cameraKm in DynamicSky::GetEnvironmentKey, or keep one procedural probe per camera, so the editor and main cameras stop fighting over the single probe (see #4).
- **Findings:** —
- **Work:** —
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

## Changelog

- 2026-11-04 · Board created from the imported issue list (20 issues).
- 2026-11-04 · #1 Perlin terrain generator (Tools/GenerateTerrain.py), Procedural.terrain asset, TerrainProceduralTest scene + flow, 18 unit tests; #21 opened.
- 2026-11-04 · #2 #3 #19 audited (terrain tiling precision, terrain draw calls, physics sync cost): findings recorded, engine follow-ups #22-#29 opened; marked Blocked (no MitchEngine push access from this session).
- 2026-11-04 · Audits recorded for #4 #5 #9 #12 #13 #15 #20; follow-ups #30-#40 opened. Board header repaired (a helper bug had merged the Columns and Issues sections).
