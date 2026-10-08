#!/usr/bin/env bash
# Run a command inside this repo's flake dev environment, regardless of the
# environment VS Code itself was started with (`code .` reuses an already
# running instance, which keeps that instance's original environment).
# The shellHook banner is discarded so gdb's MI output stays clean.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
eval "$(nix print-dev-env "$ROOT")" >/dev/null
exec "$@"
