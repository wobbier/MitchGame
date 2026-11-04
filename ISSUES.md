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
| 2 | Fix terrain rendering bugs | In Progress | Terrain / Rendering | Engine |
| 3 | Optimize terrain LOD system | To Do | Terrain / Rendering | Engine |
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
| 19 | Optimize collision detection | To Do | Physics | Engine |
| 20 | Add visual scripting support | Backlog | Scripting / Editor | Engine |
| 21 | Editor: generate terrain heights from noise | To Do | Terrain / Editor | Engine |

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
- **Status:** In Progress · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Resolve issues with texture tiling on large terrain meshes.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

### 3 · Optimize terrain LOD system
- **Status:** To Do · **Area:** Terrain / Rendering · **Owner:** Engine
- **Description:** Improve performance by reducing draw calls for terrain LOD.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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
- **Status:** To Do · **Area:** Physics · **Owner:** Engine
- **Description:** Reduce physics calculation time by 25% for complex object interactions.
- **Findings:** —
- **Work:** —
- **Follow-ups:** —

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

## Changelog

- 2026-11-04 · Board created from the imported issue list (20 issues).
- 2026-11-04 · #1 Perlin terrain generator (Tools/GenerateTerrain.py), Procedural.terrain asset, TerrainProceduralTest scene + flow, 18 unit tests; #21 opened.
