#!/usr/bin/env bash
# Toggle fork-only switches that the prebuilt UI has no menu item for.
# (Verified via strings on selfdrive/ui/_ui: it ships toggles for dp_mapd,
# dp_alka, etc. but NOT for dp_curve_decel / dp_cam_decel.)
#
# Writes BOTH param locations (flat + d/) so the C++ UI, the sync loop and
# the Python side all agree immediately.
#
# Usage (on the EON, or via: bash ssh_eon.sh 'sh /data/openpilot/scripts/eon_switch.sh ...')
#   sh /data/openpilot/scripts/eon_switch.sh list
#   sh /data/openpilot/scripts/eon_switch.sh curve 1     # curve auto-decel
#   sh /data/openpilot/scripts/eon_switch.sh cam 1       # Mappy speed-limit decel
#   sh /data/openpilot/scripts/eon_switch.sh mapd 1      # MapD (OSM road name/limit display)
#
# Notes:
#   - dp_curve_decel: read live by controlsd every cycle -> takes effect now.
#   - dp_cam_decel:   controlsd reads it ONCE at startup -> controlsd restarts
#                     automatically at the next onroad transition; force it with
#                     `pkill -f controlsd.py` while offroad.
#   - dp_mapd:        mapd/gpxd start onroad when set; the osm server tarball
#                     is installed by launch_chffrplus.sh at boot when set.

P=/data/params
case "$1" in
  curve) K=dp_curve_decel ;;
  cam)   K=dp_cam_decel ;;
  mapd)  K=dp_mapd ;;
  list)
    for k in dp_curve_decel dp_cam_decel dp_mapd dp_cam_decel_mode; do
      printf '%-24s flat=%s d/=%s\n' "$k" "$(cat $P/$k 2>/dev/null)" "$(cat $P/d/$k 2>/dev/null)"
    done
    exit 0 ;;
  *) echo "usage: $0 [curve|cam|mapd] [0|1] | $0 list"; exit 1 ;;
esac
case "$2" in
  0|1) V="$2" ;;
  *) echo "value must be 0 or 1"; exit 1 ;;
esac
mkdir -p "$P/d"
printf '%s' "$V" > "$P/$K"
printf '%s' "$V" > "$P/d/$K"
echo "$K=$V (flat + d/)"
