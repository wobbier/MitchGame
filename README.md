[![Build status](https://ci.appveyor.com/api/projects/status/uwttukf4i7x87g4y?svg=true)](https://ci.appveyor.com/project/wobbier/mitchgame)
![license](https://img.shields.io/github/license/wobbier/mitchgame.svg)
======
This is an example project to get you started making games in the [MitchEngine][2].

Getting Started
-----------------------

1. Pull the repo and run GenerateSolution.bat or edit the project name using the methods shown below
2. Run Engine/ThirdParty/GenerateSolutions.bat (Until I figure out a good way to remove this step)
3. Open the generated solution in the root folder
4. Build & Celebrate

Linux builds
------------

Enter `nix develop`, then run `Project/GenerateSolution.sh` to generate the makefiles. Editor configs are `editor_debug`, `editor_release`, and `editor_retail`; game configs are `game_linux_debug`, `game_linux_release`, and `game_linux_retail`.

```bash
make -f MitchGame.make Havana config=editor_release -j"$(nproc)"
make -f MitchGame.make Game_EntryPoint config=game_linux_retail -j"$(nproc)"
```

Run the binaries inside `nix develop` too. From a regular terminal at the project root, use:

```bash
nix develop --command ./.build/Editor_Release/Havana
nix develop --command ./.build/Game_linux_Retail/Game_EntryPoint_x64
```

The development shell supplies the shared-library paths for fontconfig, Wayland, Ultralight's GTK dependencies, and the graphics loaders. Launching the executable directly outside that shell can fail with `libfontconfig.so.1: cannot open shared object file` or another missing-library error. VS Code's launch configurations already run through the Nix environment.

VS Code's build tasks and Run and Debug menu include Debug, Release, and Retail for Havana, MitchGame, and ME HUB. The Release and Retail game tasks also compile the C# scripts into the corresponding output folder. When building the Retail game directly with make, build its scripts separately before running it; see [the build-system guide](Engine/Docs/Build-System.md#generating-and-building).

Release retains development tools and debug symbols. Retail disables engine debug-symbol generation and profiling, and omits game development tools. These are local builds; distribution packaging and a portable Linux toolchain are separate steps.

Editing the project name
-----------------------

Edit the GenerateSolution.bat file and change the --project-name property with your desired name.
This is important since it will be used when searching for project files.

Replace the word MitchGame on the folders MitchGame and MitchGame_EntryPoint with the same name as the --project-name. EX TestGame and TestGame_EntryPoint

Contact me
----------

   * Website: [http://wobbier.com][1]
   * Twitter: [http://www.twitter.com/wobbier][3]
   
[1]: https://www.wobbier.com "My Portfolio"
[2]: https://github.com/wobbier/MitchEngine "MitchEngine Source"
[3]: https://www.twitter.com/wobbier "Twitter"
