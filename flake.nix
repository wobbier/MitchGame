{
  description = "MitchGame dev environment (SDL2 + BGFX + GL/EGL)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in
      {
        # ----------------------------------------------------------
        # MitchGame Dev Shell
        #
        # NOTES FOR FUTURE MITCH:
        # - bgfx loads GL/EGL dynamically with dlopen()
        # - Mesa + libglvnd MUST be in LD_LIBRARY_PATH so bgfx finds
        #   64-bit libEGL.so.1 instead of Steam’s 32-bit version.
        # - ALWAYS enter this shell with:  nix develop
        # ----------------------------------------------------------
        devShells.default = pkgs.mkShell {
          name = "mitchgame-devshell";

          buildInputs = with pkgs; [
            # Core build tools
            gcc
            gdb
            gnumake
            cmake
            pkg-config

            # SDL2 from Nix
            SDL2

            # GL/EGL libs
            mesa        # GL + EGL + DRI drivers
            libglvnd    # GL/Vulkan dispatch loader

            # Optional Vulkan support for bgfx
            # vulkan-loader
          ];

          # Provide GL/EGL so bgfx’s dlopen("libEGL.so.1") succeeds.
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.libglvnd
            pkgs.mesa
            pkgs.SDL2
          ];

          shellHook = ''
            echo "🔧 MitchGame dev shell active!"
            echo "  Build: make -f MitchGame.make Havana config=editor_debug"
            echo "  Run:   ./.build/Editor_Debug/Havana"
            echo "  Optional: SDL_VIDEODRIVER=wayland ..."
            echo ""
            echo "LD_LIBRARY_PATH set for correct 64-bit EGL → bgfx friendliness 😎"
          '';
        };
      });
}