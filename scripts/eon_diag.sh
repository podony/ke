#!/system/bin/sh
# ============================================================================
# EON one-shot diagnostic: why is the car list empty / car not recognized,
# and is MAPPY actually installed+permitted. Read-only; safe to run anytime.
#
# Run ON THE DEVICE (Termux or adb shell):
#   sh /data/openpilot/scripts/eon_diag.sh
# Report is printed and saved to /data/params/eon_diag_report.txt
# ============================================================================
OUT=/data/params/eon_diag_report.txt
exec > "$OUT" 2>&1

echo "=== EON DIAG $(date) ==="

echo ""
echo "--- 1. PYTHON ENV (empty car list usually starts here) ---"
PY=""
for cand in python3 /system/comma/usr/bin/python3 /data/data/com.termux/files/usr/bin/python3; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done
echo "python: ${PY:-NONE}"
if [ -n "$PY" ]; then
  "$PY" -V 2>&1
  SITE=$("$PY" -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null)
  echo "site-packages: ${SITE:-UNRESOLVABLE}"
  echo "strenum import: $("$PY" -c 'import strenum; print("OK", strenum.__file__)' 2>&1 | head -1)"
  echo "cereal import:  $("$PY" -c 'import cereal; print("OK")' 2>&1 | head -1)"
  echo "numpy import:   $("$PY" -c 'import numpy; print("OK", numpy.__version__)' 2>&1 | head -1)"
  echo "gm brand import: $("$PY" -c 'import openpilot.selfdrive.car.gm.interface; print("OK")' 2>&1 | tail -1)"
  echo "car count: $("$PY" -c 'from openpilot.selfdrive.car.fingerprints import all_known_cars; print(len(all_known_cars()))' 2>&1 | tail -1)"
fi

echo ""
echo "--- 2. CARLIST DIAGNOSTICS (written by manager/interfaces) ---"
for f in /data/params/eon_carlist_diag.txt /tmp/car_list_diag.txt /data/params/eon_libs_diag.txt; do
  echo "[$f]"
  if [ -s "$f" ]; then tail -30 "$f"; else echo "(empty or missing)"; fi
done
echo "[dp_car_list param]"
if [ -s /data/params/d/dp_car_list ]; then
  echo "size=$(wc -c < /data/params/d/dp_car_list) first200:"
  head -c 200 /data/params/d/dp_car_list; echo ""
else
  echo "(missing or empty)"
fi

echo ""
echo "--- 3. MAPPY INSTALL STATE ---"
echo "package: $(pm list packages 2>/dev/null | grep mappyobn || echo NOT-INSTALLED)"
echo "[apk layer diag]"
if [ -s /data/params/eon_apk_diag.txt ]; then tail -40 /data/params/eon_apk_diag.txt; else echo "(empty or missing)"; fi
if pm list packages 2>/dev/null | grep -q mappyobn; then
  echo "required perms granted:"
  dumpsys package com.mnsoft.mappyobn 2>/dev/null | grep -E 'ACCESS_FINE_LOCATION|WAKE_LOCK|INTERNET' | grep -i 'granted=true' | head -5
  echo "version: $(dumpsys package com.mnsoft.mappyobn 2>/dev/null | grep -m1 versionName)"
fi

echo ""
echo "--- 4. PANDA / USB (car recognition needs this) ---"
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "no /dev/ttyUSB* or /dev/ttyACM*"
lsusb 2>/dev/null | grep -i 'comma\|panda\|16d0' || echo "no panda in lsusb (or lsusb missing)"

echo ""
echo "--- 5. PROCESSES ---"
ps 2>/dev/null | grep -E 'manager|controlsd|pandad|boardd|camerad|road_speed|ui' | grep -v grep || echo "(none found)"

echo ""
echo "--- 6. SSH STATE (why access dies after builds) ---"
echo "GithubSshKeys param: $(wc -c < /data/params/d/GithubSshKeys 2>/dev/null || echo MISSING) bytes"
for f in /data/data/com.termux/files/home/.ssh/authorized_keys /root/.ssh/authorized_keys; do
  echo "authkeys $f: $(wc -l < "$f" 2>/dev/null || echo MISSING) lines"
done
echo "hostkey store (/data/params/ssh_hostkeys):"
ls /data/params/ssh_hostkeys/ 2>/dev/null || echo "  (missing - host keys not persisted yet)"
for d in /data/data/com.termux/files/usr/etc/ssh /system/etc/ssh; do
  [ -d "$d" ] && echo "sshd etc $d:" && ls "$d"/ssh_host_*_key 2>/dev/null
done
echo "sshd listening 8022: $( (echo > /dev/tcp/127.0.0.1/8022) 2>/dev/null && echo YES || echo NO)"
echo "[ssh diag log tail]"
if [ -s /data/params/eon_ssh_diag.txt ]; then tail -15 /data/params/eon_ssh_diag.txt; else echo "(empty or missing)"; fi

echo ""
echo "--- 7. SYMLINK TREE (imports need openpilot/ -> .) ---"
ls -la /data/openpilot/openpilot 2>/dev/null | head -10 || echo "openpilot/ symlink tree MISSING"

echo ""
echo "--- 8. RECENT MANAGER OUTPUT ---"
for f in /data/params/eon_ssh_diag.txt /data/params/eon_log_upload.txt; do
  echo "[$f]"
  if [ -s "$f" ]; then tail -5 "$f"; else echo "(empty or missing)"; fi
done

echo ""
echo "=== DONE $(date) ==="
echo "report saved: $OUT"
