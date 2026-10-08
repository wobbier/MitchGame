#!/usr/bin/env bash
# gdb inside the flake dev environment (see nix-env.sh).
exec "$(dirname "${BASH_SOURCE[0]}")/nix-env.sh" gdb "$@"
