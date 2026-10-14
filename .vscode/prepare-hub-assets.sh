#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

for asset in Engine/Tools/HUB/Assets/*.png; do
    if [[ ! -f "$asset.dds" || "$asset" -nt "$asset.dds" || "$asset.meta" -nt "$asset.dds" ]]; then
        Engine/Tools/RunTextureCompiler.sh -f "$asset" -o "$asset.dds" -t RGBA8 -m
    fi
done
