[![Build status](https://ci.appveyor.com/api/projects/status/uwttukf4i7x87g4y?svg=true)](https://ci.appveyor.com/project/wobbier/mitchgame)
![license](https://img.shields.io/github/license/wobbier/mitchgame.svg)
======
This is an example project to get you started making games in the [MitchEngine][2].

Getting Started
-----------------------

1. Pull the repo and run `Project/GenerateSolution.bat` (Windows) or `Project/GenerateSolution.command` (macOS), after setting the project name as shown below
2. Run Engine/ThirdParty/GenerateSolutions.bat (Until I figure out a good way to remove this step)
3. Open the generated solution in the root folder
4. Build & Celebrate

Linux builds
------------

Open the project in VS Code and press F5 with Nix and the C/C++ extension installed. Build tasks enter the engine-owned environment and regenerate the makefiles automatically. For a terminal, run `Engine/Tools/DevShell.sh`. Editor configs are `editor_debug`, `editor_release`, and `editor_retail`; game configs are `game_linux_debug`, `game_linux_release`, and `game_linux_retail`.

```bash
make -f MitchGame.make Havana config=editor_release -j"$(nproc)"
make -f MitchGame.make Game_EntryPoint config=game_linux_retail -j"$(nproc)"
```

Run the binaries inside `Engine/Tools/DevShell.sh` too. From a regular terminal at the project root, use:

```bash
Engine/Tools/NixEnv.sh ./.build/Editor_Release/Havana
Engine/Tools/NixEnv.sh ./.build/Game_linux_Retail/Game_EntryPoint_x64
```

The engine owns the package lock and shared environment. Optional private project dependencies go in `devshell.nix`; see [the environment guide](Engine/Docs/Development-Environment.md). The development shell supplies the shared-library paths for Wayland, SDL2 and the graphics loaders. Launching the executable directly outside that shell can fail with a missing-library error. VS Code's launch configurations already run through the Nix environment.

VS Code's build tasks and Run and Debug menu include Debug, Release, and Retail for Havana, MitchGame, and ME HUB. The Release and Retail game tasks also compile the C# scripts into the corresponding output folder. When building the Retail game directly with make, build its scripts separately before running it; see [the build-system guide](Engine/Docs/Build-System.md#generating-and-building).

Release retains development tools and debug symbols. Retail disables engine debug-symbol generation and profiling, and omits game development tools. These are local builds; distribution packaging and a portable Linux toolchain are separate steps.

Editing the project name
-----------------------

Set `Name` in `Game.sharpmake.cs` (both the project and the solution class) to your game's name. Generation writes it to `Project/Game.meproj` and names the solution and makefile after it (`<Name>.sln`, `<Name>.make`). The `Game` and `Game_EntryPoint` folders keep their names.

Contact me
----------

   * Website: [http://wobbier.com][1]
   * Twitter: [http://www.twitter.com/wobbier][3]
   
[1]: https://www.wobbier.com "My Portfolio"
[2]: https://github.com/wobbier/MitchEngine "MitchEngine Source"
[3]: https://www.twitter.com/wobbier "Twitter"
