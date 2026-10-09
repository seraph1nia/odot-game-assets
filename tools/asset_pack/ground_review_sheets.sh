#!/usr/bin/env bash
# Assemble only authored/legacy-model renders; never copy supplied references.
set -euo pipefail
cd "$(dirname "$0")/../.."
renders=docs/detailed-ground/renders
out=docs/detailed-ground
families=(legacy moss grass dirt leaf_litter pine_duff)
pieces=(straight turn_120 turn_60 end)
floors=(); close=(); overlays=(); neighbors=(); stacks=(); occupied=()
for family in "${families[@]}"; do
    floors+=("$renders/floor_$family.png")
    close+=("$renders/close_$family.png")
done
for family in path river; do
    for piece in "${pieces[@]}"; do
        overlays+=("$renders/${family}_$piece.png")
        neighbors+=("$renders/neighbors_${family}_$piece.png")
    done
done
for family in path river; do
    for base in moss grass dirt leaf_litter pine_duff; do
        stacks+=("$renders/stack_${base}_$family.png")
    done
done
for role in tree building unit; do occupied+=("$renders/occupied_$role.png"); done
sheet() {
    local name=$1 tile=$2 geometry=$3; shift 3
    magick montage -font DejaVu-Sans -pointsize 12 -background '#edeade' -fill '#262d25' \
        -label '%t' "$@" -tile "$tile" -geometry "$geometry" -depth 8 "$out/$name.png"
}
sheet floors-close 6x2 256x256+4+4 "${floors[@]}" "${close[@]}"
sheet tile-scale 6x1 160x160+4+4 "${floors[@]}"
sheet overlays 4x2 256x256+4+4 "${overlays[@]}"
sheet neighbors 4x2 384x264+4+4 "${neighbors[@]}"
sheet stacks 5x2 224x224+4+4 "${stacks[@]}"
sheet occupied 3x1 320x320+4+4 "${occupied[@]}"
