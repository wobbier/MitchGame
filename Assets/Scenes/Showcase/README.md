# Showcase scenes

Manual QA scenes and screenshot-regression references for the engine's major systems.

| Scene | What it shows |
|-------|---------------|
| `Lighting.lvl` | PBR metallic / roughness sphere grid, textured exhibits, neon emissives with bloom, coloured point lights on bobbing orbs, a shadowed spot light, a fire with soft particles, SSAO, procedural sky ambient |
| `Playground.lvl` | Playable: third-person `CharacterController` (Move / Look / Jump / Sprint actions), orbit follow camera, crate stacks, a domino run, a kinematic sweeper in a ball pit, a wrecking ball on a distance joint, a camp fire with 3D audio, Synty props, and three `NavMeshAgent` chasers that path to the player |
| `Physics2D.lvl` | Box2D: a 55-box pyramid, a motorised windmill with balls dropping on it, a hinged rope bridge with crates; orthographic camera |

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

Captures run 480 frames at a fixed 1/60 s (`--frame-time`), so they are repeatable; diffs land in `.tmp/ScreenshotRegression/`. `PlaygroundFlows.edscript` checks the playground's gameplay scripts in the editor (`Havana --scene Assets/Scenes/Showcase/Playground.lvl --editor-exec Assets/Scenes/Showcase/PlaygroundFlows.edscript`).
