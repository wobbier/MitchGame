# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MitchGame is an example game project built on top of [MitchEngine](https://github.com/wobbier/MitchEngine) (a git submodule at `Engine/`). The engine is a C++20 ECS-based game engine targeting Windows, macOS, and Linux, with a visual editor called Havana.

## Platform Compatibility

All code changes must compile and run correctly on **Win64, macOS, and Linux**. UWP compatibility is also required but held to a looser standard — it should not be actively broken, but UWP-specific quirks are acceptable as long as the other three platforms are unaffected.

Use the `USING( ME_PLATFORM_* )` feature flags (see below) to guard any platform-specific code rather than raw `#ifdef` or `#if defined(...)`. Prefer writing platform-agnostic code first and only branching when a platform truly requires it.

## Build Commands (Linux)

```bash
# Build the Havana editor (default VSCode build task)
make -f MitchGame.make Havana config=editor_debug -j$(nproc)

# Build the game executable
make -f MitchGame.make Game_EntryPoint config=game_linux_debug -j$(nproc)

# Run the editor
./.build/Editor_Debug/Havana

# Run the game
./.build/Game_linux_Debug/Game_EntryPoint_x64
```

The Nix dev shell (`nix develop`) provides all required dependencies. Without Nix, the README lists the required X11/Vulkan packages for a manual `nix-shell -p ...` invocation.

### Checks

`Engine/Tools/RunChecks.sh` (inside the dev shell, from the repo root) builds the editor, game and unit tests, then runs the unit tests, every editor flow (`Engine/Tools/RunEditorFlows.py`: each `*.edscript` under `Assets/Scenes` with the scene named in its header) and the showcase screenshot regression. GUI runs go through `Engine/Tools/Headless.sh` (private Xvfb display + lavapipe), never the desktop. `--skip-build` and `--only <flow filter>` narrow it.

### Solution / Project Generation

The Sharpmake generator scripts live in `Project/`: `GenerateSolution.bat` (Windows), `GenerateSolution.command` (macOS), and `GenerateSolution.sh` (Linux). Run the one for your platform to generate the Visual Studio solution / Xcode project / makefiles, then build in the IDE (or via `make` on Linux — see above). Also run `Engine/ThirdParty/GenerateSolutions.bat` once for third-party dependencies.

The generated build files (`Makefile`, `*.make`, `compile_commands.json`) are gitignored — like the generated `.sln`/`.vcxproj`/`.pbxproj` — and must never be committed. Runtime log/dump artifacts (`Engine.txt`, `fmod_log.txt`, `startup.json`) are also ignored.

## Architecture

### Entity-Component-Core (ECS) Pattern

The engine uses an ECS pattern where **Entities** hold **Components** (data) and **Cores** act as systems that process entities matching a component filter.

- `Engine/Source/ECS/Entity.h` — `AddComponent<T>()`, `GetComponent<T>()`, `HasComponent<T>()`
- `Engine/Source/ECS/Core.h` — `BaseCore` base class; implement `Update()`, `OnEntityAdded()`, `OnEntityRemoved()`
- `Engine/Source/Engine/World.h` — manages all entities and cores; `CreateEntity()`, `AddCore<T>()`, `CreateFromPrefab()`

Components are registered at compile time with `ME_REGISTER_COMPONENT(T)` and cores with `ME_REGISTER_CORE(T)`.

### Game Entry Point

Games inherit from the `Game` base class and are wired up with a macro:

```cpp
class MyGame : public Game {
    void OnInitialize() override;
    void OnStart() override;
    void OnUpdate(const UpdateContext&) override;
    void OnEnd() override;
};
ME_APPLICATION_MAIN(MyGame)
```

The game-specific code lives in `Game/Source/` and the executable entry point in `Game_EntryPoint/Source/main.cpp`.

### Major Subsystems

| Subsystem | Location | Backend |
|-----------|----------|---------|
| Rendering | `Engine/Modules/Moonlight/` + `Engine/Source/Cores/Rendering/` | BGFX |
| Physics | `Engine/Source/Cores/PhysicsCore.cpp`, `Physics2DCore.cpp` (see `Engine/Docs/Physics.md`) | Box3D (3D) + Box2D (2D, XY plane) |
| Animation | `Engine/Source/Cores/AnimationCore.cpp` + `Animator` component (see `Engine/Docs/Animation.md`) | Assimp clips, GPU skinning |
| Navigation | `Engine/Source/Cores/NavigationCore.cpp` + `Engine/Source/Navigation/` + `NavMeshSurface` / `NavMeshAgent` (see `Engine/Docs/Navigation.md`); baked `.navmesh` files sit next to their scene | Recast / Detour (DetourCrowd) |
| Audio | `Engine/Source/Cores/AudioCore.cpp` + `AudioSource` / `AudioListener` (see `Engine/Docs/Audio.md`) | FMOD (optional); automated runs are silent |
| UI | `Engine/Source/Cores/UI/` | Ultralight (HTML/CSS), being replaced by RmlUi behind `ME_RMLUI` (`UIDocument` + `RmlUiCore` + `Engine/Source/UI/Rml/`; see `Engine/Docs/UI-Ultralight-and-ImGui.md`) |
| Scripting | `Engine/Source/Scripting/` + `Engine/Modules/ScriptCore/` (see `Engine/Docs/Scripting-DotNet.md`); game scripts are any `.cs` under `Assets/`, built by `Project/Game.Script.csproj`; `[GenerateSchema]` scripts get compile-time field schemas/serializers from `Engine/Modules/ScriptCore/Generators/` | .NET 8 / C#, hot reload in the editor |
| VFS | `Engine/Modules/Dementia/Source/VFS/` behind `Path`/`File` (see `Engine/Docs/VFS.md`); game root over engine root as a priority overlay; `user://` is the per-user writable root (OS pref dir in shipped builds, `.tmp/User` in dev and automation) | DirectoryMount (paks arrive with VFS-3) |
| Shader graphs | `Engine/Source/ShaderGraph/` (compiler, nodes, targets) + `Engine/Modules/Havana/Source/Widgets/ShaderGraph/` (editor, previews) + `ShaderGraphMaterial` (see `Engine/Docs/ShaderGraph.md`); graphs are `.shadergraph` files with generated sources committed in `<Name>.sg/` (regenerate with `ME_SHADERGRAPH_UPDATE=1 MitchEngine_Tests -tc="*project graphs*"`) | bgfx shaderc (Lit, Unlit, Particle, Decal, Post Process targets) |
| Editor | `Engine/Modules/Havana/` | Ultralight + ImGui |
| Input | `Engine/Source/Engine/Input.h` + `Engine/Source/Input/` (actions, gamepads; see `Engine/Docs/Input.md`); the project map is `Assets/Config/Input.inputactions` | SDL2 |

The `Engine` class (singleton-like, `Engine/Source/Engine/Engine.h`) owns the main loop and provides access to the `World`, renderer, input, and job system.

### Rendering Pipeline

`RenderCore` (`Engine/Source/Cores/Rendering/RenderCore.cpp`) runs a **parallel mesh job** over visible entities and fills a POD `MeshCommand` (`Engine/Modules/Moonlight/Source/RenderCommands.h`) per mesh. The render-loop hot fields are precomputed in that parallel job so the serial submit loop in `BGFXRenderer` (`Renderer.cpp`) needs no virtual calls to sort and batch: `BatchKey`, `VertexBufferIdx`, `IndexBufferIdx`, `IsTransparent`, `SupportsInstancing` (binding the material, `Material::Use` / `GetRenderState`, is the one virtual step per draw).

**Automatic GPU instancing:** opaque meshes whose material sets `SupportsInstancing = true` (opt-in; see `StandardMaterial`) are grouped into `InstanceBatch`es keyed by geometry (vertex/index buffer) + `Material::GetInstanceBatchKey()`. The batch key is a hash of GPU state (program idx, texture idx, render state, `DiffuseColor`, `Tiling`) — **not the material pointer**, because each mesh gets a unique material instance. Each batch is drawn once via `RenderMeshInstanced` (chunked BGFX instance-data buffer, 64-byte/mat4 stride), bypassing the 65536-entry `setTransform` matrix cache. Transparent meshes still submit individually for correct ordering. Shared bind logic lives in `BindMeshDrawState`. See also the `instancing-render-path` memory.

**Lighting & frame (overhaul Wave 3):** each camera renders linear HDR (RGBA16F):

- **Shadows**: sun CSM (4 cascades) and spot-light shadows.
- **Opaque**: clustered-forward PBR opaque pass. `StandardMaterial` is metallic-roughness; `Light` components are Directional/Point/Spot; the clusters are a CPU-built 16×9×24 grid uploaded as textures.
- **Post**: SSAO, then height fog (analytic, or volumetric: half-res raymarch with sun shafts and clustered lights; `PostProcess` component Fog settings, `Fog.sh`), then transparents and particles (which fog themselves), then bloom / eye adaptation / tonemap / FXAA.
- **Ambient**: image-based, from per-camera environment probes.

Details:

- View IDs come from `ViewAllocator` (`RenderViews.h`).
- Shader binaries load next to their resolved source.
- `Engine/Tools/BuildShaders.sh` rebuilds everything, and the editor hot-reloads edited shaders and `.sh` includes.
- Test scenes for verification live in `Assets/Scenes/Tests/` (HierarchyTest, LightingTest, ShadowTest, ParticleTest, LodTest). Models get simplified LODs from their import settings (`GenerateLODs`); `--lod-bias 0` forces the coarsest level in captures.
- Showcase scenes (`Assets/Scenes/Showcase/`: Lighting, Playground, Physics2D, Fog, Decals, ShaderGraph) double as screenshot-regression references: `Engine/Tools/ScreenshotRegression.py --game .build/Game_linux_Debug/Game_EntryPoint_x64 --reference Assets/Scenes/Showcase/Reference Assets/Scenes/Showcase/*.lvl` (captures are deterministic via `--frame-time`; `--update` accepts new looks). See `Assets/Scenes/Showcase/README.md`.
- Full write-up: `Engine/Docs/Rendering-Pipeline.md` and `Engine/Docs/Materials-and-Shaders.md`.

**Transform dirty flags:** `Transform` (`Engine/Source/Components/Transform.cpp`) tracks `IsLocalToWorldDirty` / `IsWorldToLocalDirty` separately. `SetDirty` propagates downward to children eagerly but early-outs when already dirty; matrix recompute is lazy and cached. A static (unmutated) scene therefore costs near-nothing per frame.

### Serialization

Components serialize to/from JSON by overriding:

```cpp
virtual void OnSerialize(json& outJson) final;
virtual void OnDeserialize(const json& inJson) final;
```

Level/scene files are JSON (`.lvl`), prefabs are JSON stored in `Assets/`.

### Key Macros

- `ME_HARDSTUCK(T)` — disables copy/move (use on engine/core types)
- `ME_REGISTER_COMPONENT(T)` / `ME_REGISTER_CORE(T)` — compile-time ECS registration
- `ME_APPLICATION_MAIN(GameClass)` — defines `main()` and wires up the game class

### Feature Flags (`Dementia.h`)

Dementia provides a compile-time feature flag system built on preprocessor arithmetic. Each feature is defined as either `IN_USE` (`&&`) or `NOT_IN_USE` (`&&!`), and `USING(feature)` expands to `(1 <feature> 1)` — truthy when `IN_USE`, falsy when `NOT_IN_USE`.

```cpp
#if USING( ME_EDITOR )
    // editor-only code
#endif

#if USING( ME_PLATFORM_LINUX )
    // Linux-only code
#endif
```

Composite features use `USE_IF(expr)` which takes a boolean expression of `USING()` calls:

```cpp
// defined as: USE_IF( USING( ME_EDITOR ) || USING( ME_TOOLS ) )
#if USING( ME_IMGUI )
    // available in editor, tools, and profiling builds
#endif
```

**Available feature flags:**

| Flag | Meaning |
|------|---------|
| `ME_EDITOR` | Havana editor is included |
| `ME_PLATFORM_WIN64` / `ME_PLATFORM_MACOS` / `ME_PLATFORM_LINUX` | Target platform |
| `ME_PLATFORM_WINDOWS` | Win64 or UWP |
| `ME_DEBUG` / `ME_RELEASE` / `ME_RETAIL` | Build configuration |
| `ME_HEADLESS` | No window / no rendering |
| `ME_PHYSICS_3D` | 3D physics (always on; Box3D) |
| `ME_DOTNET` / `ME_SCRIPTING` | C# scripting via .NET 8 (`ME_SCRIPTING` is `USE_IF(USING(ME_DOTNET))`) |
| `ME_ULTRALIGHT` / `ME_UI` | Ultralight HTML UI |
| `ME_FMOD` | FMOD audio (disabled in headless) |
| `ME_OPTICK` / `ME_PROFILING` | Profiling support |
| `ME_IMGUI` | ImGui (editor, tools, or profiling builds) |
| `ME_TOOLS` / `ME_GAME_TOOLS` | Non-editor tool builds |

Never use plain `#ifdef ME_EDITOR` — always use `#if USING( ME_EDITOR )` so the flag participates correctly in composite `USE_IF` expressions.

### .NET Scripting Architecture

The scripting system migrated from Mono to **.NET 8** via the `hostfxr`/`nethost` hosting API. The feature flag chain is: `DEFINE_ME_DOTNET` (preprocessor define) → `ME_DOTNET` (Dementia flag) → `ME_SCRIPTING` (composite flag).

**C++ side** (`Engine/Source/Scripting/`):

- `ScriptHost` — thin RAII wrapper around `hostfxr`. Loads the .NET runtime from the system-installed `hostfxr.dll`, initializes it with `ScriptCore.runtimeconfig.json` (targets `net8.0`), and resolves `[UnmanagedCallersOnly]` function pointers via `LoadFunction()`.
- `ScriptEngine` — higher-level interface consumed by the rest of the engine. Calls into managed code through the function pointers loaded by `ScriptHost`. Public API: `Init()`, `CreateScript()`, `ScriptOnStart/Update/Destroy/EditorInspect()`, `GetFieldsJson/SetFieldsJson()`, `GetScriptCount/Name()`.
- `ScriptEngineAPI` (`Generated/ScriptEngineAPI.generated.h`) — plain C struct of function pointers passed from C++ to managed code at startup. **Generated** together with the C# `EngineAPIBindings.g.cs` from `Source/Scripting/ScriptAPI.def` by `Engine/Tools/GenerateScriptAPI.py` (append to the manifest, regenerate, fill the slot in a `Register_*Bindings`; `--check` verifies). Covers logging, time, entity lifecycle, transforms, world/scenes, input actions, audio, physics, debug draw, camera, UI and ImGui.
- `BindingContext` (`Bindings/BindingContext.h`, `ScriptBindings` namespace) — per-domain component registry. Call `ScriptBindings::RegisterComponent<T>("Name")` to make a component available to scripts by name via `Entity_HasComponent`/`Entity_AddComponent`. Individual binding files live under `Bindings/Components/` and `Bindings/Systems/`.

**Managed side** (`Engine/Modules/ScriptCore/Source/`):

- `IGameScript` — interface all game scripts implement: `OnStart()`, `OnUpdate(float dt)`, `OnDestroy()`, `OnEditorInspect()`.
- `Engine.cs` (`EngineAPIBindings` struct + `Engine` static class) — mirrors `ScriptEngineAPI` on the C# side using `delegate* unmanaged<>` function pointers. Scripts call e.g. `Engine.Log(...)`, `Engine.Transform.GetTranslation(entity)`.
- `GameScriptALC` — collectible `AssemblyLoadContext` that isolates game script assemblies (loaded from memory, so the DLL is never locked). Routes `ScriptCore` references back to the already-loaded assembly. **Hot reload**: editing a `.cs` in the editor rebuilds on a worker thread, swaps the ALC and re-creates instances under the same handles with public fields restored (`IGameScript.OnReload`).
- `ScriptRegistry` — scans a loaded assembly for all non-abstract `IGameScript` implementations and keeps them in a sorted list.
- `Inspector.cs` — reflection-based ImGui field drawer for script instances; respects `[HideInInspector]` attribute.

**Build config:**

- Windows: set `Globals.DOTNET_Win64_Dir` in `Game.sharpmake.cs` to the `runtimes/win-x64/native` directory inside the installed `Microsoft.NETCore.App.Host.win-x64` pack (e.g. `C:\Program Files\dotnet\packs\Microsoft.NETCore.App.Host.win-x64\8.0.27\runtimes\win-x64\native`). The build system adds that path as an include/library path and copies `nethost.dll` to the output directory.
- Linux: generate inside `nix develop` — the flake sets `DOTNET_LINUX_NATIVE_DIR` (the host pack's `runtimes/linux-x64/native`), which defines `DEFINE_ME_DOTNET` and links `libnethost.so` with an rpath. Sharpmake can't make C# projects here, so the engine runs `dotnet build Project/Game.Script.csproj` (which builds `Engine/Modules/ScriptCore/ScriptCore.csproj`) into the exe dir on startup when sources are newer. Game builds only load the DLLs already there.
- The `ScriptCore` C# project (`Engine/Modules/ScriptCore/ScriptCore.sharpmake.cs`) builds as a `DotNetClassLibrary` targeting `net8.0` with unsafe blocks enabled (Windows/Visual Studio).
- `ScriptCore` (the C++ core) is engine-owned (`Engine::Scripts`): scripts start on Play after a physics sync, get `OnFixedUpdate` before each physics step, `OnUpdate` after the scene cores and `OnLateUpdate` after animation (before render prep), in `[ExecutionOrder]` then start order. Game cores order with `Priority` plus `RunsAfter`/`RunsBefore`; see the stage table in `Engine/Docs/Architecture.md`.

### Build Targets (Sharpmake / Make)

`Dementia` → `MitchEngine` → `Moonlight`, `ImGui`, `Havana`, `MitchGame` → `Game_EntryPoint`

`Dementia` is a core utility/reflection library that the engine depends on. All third-party libs live in `Engine/ThirdParty/`.

## Code Style

### Function Definitions in `.cpp` Files

Separate every function definition with **two blank lines**:

```cpp
void Foo::Bar()
{
    // ...
}


void Foo::Baz()
{
    // ...
}
```

## Optick Profiling

Captures are triggered at runtime with **F9** (records 10 frames). `--capture-startup` records the first 10 frames as `startup`. Files land in `.tmp/Captures/` (newest 5 F9 captures kept); on Linux the tracer writes Chrome Trace `.json` instead of `.opt`.

### Parsing `.opt` files with Python

The format: 8-byte header + **miniz-compressed** body of chunk records.

```python
import struct, zlib

with open("capture.opt", "rb") as f: raw = f.read()
magic, ver, flags = struct.unpack_from("<IHH", raw, 0)
# magic == 0xB50FB50F, flags & 2 == IsMiniz
body = zlib.decompress(raw[8:]) if (flags & 2) else raw[8:]

# Chunks: [u32 proto_ver=26][u32 size][u16 type][u16 app=0xB50F][<size> bytes]
# type 0=FrameDescriptionBoard, 1=EventFrame, 3=NullFrame, 258=SummaryPack, 259=FramesPack
```

**FrameDescriptionBoard** layout (chunk type 0):
```
u32 boardNumber | u64 freq_hz | u64 origin | u32 precision
i64 timeSlice.start | i64 timeSlice.finish
u32 threadCount, per thread: [u64 tid][u32 pid][str name][i32 maxDepth][i32 priority][u32 mask]
u32 fiberCount, per fiber: [u64 id]
i32 forcedMainThread
u32 descCount, per EventDescription: [str name][str file][u32 line][u32 filter][u32 color][f32 budget][u8 flags]
```

Key type gotchas: `ProcessID = uint32` (not uint64). `FrameType::Type` serializes as `i32` (4 bytes, not 1).

**EventFrame** layout (chunk type 1):
```
ScopeHeader: [u32 boardNum][i32 threadNum][i32 fiberNum][i64 start][i64 finish][i32 frameType]
u32 catCount, per cat: [i64 start][i64 finish][u32 descIdx]
u32 evtCount, per evt: [i64 start][i64 finish][u32 descIdx]
```

Timestamps are raw CPU ticks; convert with `ticks * 1000.0 / freq_hz` for milliseconds. On Linux the freq is 1 GHz (nanosecond ticks).

**Strings** are `u32 length` + UTF-8 bytes (no null terminator).

### Findings from first Linux capture (2026-05-11)

- Baseline: p50=4ms, p95=5ms — engine idles at ~240fps with minimal scene
- Only 4 event descriptions registered (CPU/GPU/Render Frame + `EditorApp::OnUpdate`) — most engine systems have no `OPTICK_EVENT` marks yet
- One 172ms spike traced to `EditorApp::OnUpdate` — likely a first-frame asset load; root cause invisible without deeper marks

## TODO / Revisit

- **`EntityID::Value()` hardcoded masks** (`Source/ECS/EntityID.h`): the bit masks `0xFFFFULL` (counter) and `0x0000FFFFFFFFFFFFULL` (index) are hardcoded rather than derived from `MITCH_ENTITY_ID_COUNTER_BIT_COUNT` (16) / `MITCH_ENTITY_ID_INDEX_BIT_COUNT` (48). If those bit-count macros ever change, the masks silently drift out of sync. Replace with masks computed from the macros (e.g. `((1ULL << N) - 1)`).
