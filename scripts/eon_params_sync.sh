#!/usr/bin/env bash
# EON params split-brain sync.
#
# The fork's Python side (manager, control loops) stores params FLAT in
# /data/params/<key>, but the prebuilt C++ UI binary was built with the
# "/d" prefix: it reads and writes /data/params/d/<key> (verified by strace:
# the UI opens /data/params/d/dp_car_list, /data/params/d/dp_alka, ...).
# Consequences without this sync:
#   - the car-selection dropdown is always empty (manager writes dp_car_list
#     flat, the UI looks in d/ and finds nothing -> only [AUTO SELECT]),
#   - switch toggles made in the UI (mappy, camera decel, ...) land in d/
#     and never reach the Python processes that act on them,
#   - the UI shows defaults for params Python owns.
#
# Fix: bidirectional mtime-based sync. Newer file wins, in both directions.
# Run once at boot (before manager) and keep running (UI toggles happen at
# any time). --once mode for the boot pass; default mode loops forever.
#
# Usage: eon_params_sync.sh [--once] [INTERVAL_SECONDS]

FLAT=/data/params
D=$FLAT/d

sync_once() {
  [ -d "$D" ] || mkdir -p "$D" 2>/dev/null || return 0
  # d/ -> flat (UI switch toggles, UI-written params -> Python readers)
  for f in "$D"/*; do
    [ -f "$f" ] || continue
    b="$FLAT/$(basename "$f")"
    if [ ! -f "$b" ] || [ "$f" -nt "$b" ]; then
      cp -f "$f" "$b" 2>/dev/null
    fi
  done
  # flat -> d/ (manager-written params, dp_car_list -> UI readers)
  for f in "$FLAT"/*; do
    [ -f "$f" ] || continue   # skips the d/ directory itself
    d="$D/$(basename "$f")"
    if [ ! -f "$d" ] || [ "$f" -nt "$d" ]; then
      cp -f "$f" "$d" 2>/dev/null
    fi
  done
}

if [ "$1" = "--once" ]; then
  sync_once
  exit 0
fi

INTERVAL="${1:-5}"
while true; do
  sync_once
  sleep "$INTERVAL"
done
