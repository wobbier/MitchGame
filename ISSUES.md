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
| 4 | Fix editor lighting issues | In Progress | Editor / Rendering | Engine |
| 5 | Implement particle system | To Do | Rendering / VFX | Engine |
| 6 | Optimize asset memory | To Do | Assets | Game |
| 7 | Add ECS unit tests | In Progress | ECS / Tests | Game + Engine |
| 8 | Refactor camera system | To Do | Gameplay / Camera | Game |
| 9 | Add multiplayer networking | Backlog | Networking | Engine + Game |
| 10 | Update documentation | To Do | Docs | Game + Engine |
| 11 | Fix Dementia module memory leaks | In Progress | Dementia | Engine |
| 12 | Improve Havana editor UI responsiveness | To Do | Editor | Engine |
| 13 | Add new ImGUI widgets for tooling | To Do | Editor | Engine |
| 14 | Optimize ScriptCore scripting performance | In Progress | Scripting | Engine |
| 15 | Enhance Player module networking | To Do | Networking / Player | Engine |
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

## Columns

### Backlog
- 9 Add multiplayer networking
- 20 Add visual scripting support

### To Do
- 1, 3, 5, 6, 8, 10, 12, 13, 15, 16, 18, 19

### In Progress
- 2, 4, 7, 11, 14, 17

### In Review
- (none)

### Done
- (none)

### Blocked
- (none)

## Issu### 1 · Implement terrain generation algorithm
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
- **Status:** In Progress · **Area:** Editor / Rendering · **Owner:** Engine
- **Description:** Resolve flickering in the editor's lighting preview when rotating the camera.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 5 · Implement particle system
- **Status:** To Do · **Area:** Rendering / VFX · **Owner:** Engine
- **Description:** Create a new particle system with customizable shaders and emitter types.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Status:** Backlog · **Area:** Networking · **Owner:** Engine + Game
- **Description:** Implement basic multiplayer functionality using the existing Net module.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Status:** To Do · **Area:** Editor · **Owner:** Engine
- **Description:** Optimize the editor's UI to reduce lag during scene editing.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 13 · Add new ImGUI widgets for tooling
- **Status:** To Do · **Area:** Editor · **Owner:** Engine
- **Description:** Create custom widgets for common editor tasks like texture adjustment.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 14 · Optimize ScriptCore scripting performance
- **Status:** In Progress · **Area:** Scripting · **Owner:** Engine
- **Description:** Reduce script execution time by 15% through caching.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 15 · Enhance Player module networking
- **Status:** To Do · **Area:** Networking / Player · **Owner:** Engine
- **Description:** Add support for more reliable client-server synchronization.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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

## Changelog

- 2026-11-04 · Board created from the imported issue list (20 issues).
- 2026-11-04 · #1 Perlin terrain generator (Tools/GenerateTerrain.py), Procedural.terrain asset, TerrainProceduralTest scene + flow, 18 unit tests; #21 opened.
- 2026-11-04 · #2 #3 #19 audited (terrain tiling precision, terrain draw calls, physics sync cost): findings recorded, engine follow-ups #22-#29 opened; marked Blocked (no MitchEngine push access from this session).
