#!/usr/bin/bash
# Rebuild common/params_pyx.so for Termux (ARM64, bionic).
# Run from the openpilot repo root on the EON device (Termux):
#   cd /data/openpilot && bash build_params_pyx.sh
#
# Root cause of the boot failure:
#   The prebuilt params_pyx.so in git is linked against glibc (libc.so.6),
#   which does not exist on Termux (bionic).  This script rebuilds the
#   Cython extension from source so it links against the local bionic.
#   It uses common/params_min.cc (no swaglog/zmq/capnp deps) so the build
#   does not require generated cereal headers.

set -e

BASEDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASEDIR"

echo "[1/4] Checking prerequisites..."
if ! python -c "import Cython" 2>/dev/null; then
  echo "  cython not found, installing..."
  pip install cython
fi
python -c "import Cython; print('  cython', Cython.__version__)"

echo "[2/4] Cythonizing params_pyx.pyx -> params_pyx.cpp"
python -m cython --cplus -3 \
  -o common/params_pyx.cpp \
  common/params_pyx.pyx
echo "  done: $(ls -lh common/params_pyx.cpp | awk '{print $5}')"

echo "[3/4] Compiling with g++ (bionic-linked ARM64)..."
# On bionic (Termux) undefined symbols in a dlopen'ed module must come from the
# global namespace or an explicit NEEDED entry. Link libpython explicitly so the
# Py* symbols (e.g. PyExc_SystemError from Cython runtime) always resolve.
PY_INCLUDE="$(python -c 'import sysconfig; print(sysconfig.get_path("include"))')"
PY_LIBDIR="$(python -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
PY_LIB="$(python -c 'import sysconfig; print(sysconfig.get_config_var("LDLIBRARY")) or sysconfig.get_config_var("LDLIBRARYSTDCXX") or ""')"
if [ -n "$PY_LIB" ] && [ -e "$PY_LIBDIR/$PY_LIB" ]; then
  echo "  linking against $PY_LIBDIR/$PY_LIB"
  PY_LINK="-L"$PY_LIBDIR" -l"$(basename "$PY_LIB" | sed 's/^lib//; s/\.so.*//')" -Wl,-rpath,"$PY_LIBDIR""
else
  echo "  (no shared libpython found; relying on global symbols)"
  PY_LINK=""
fi

g++ -shared -fPIC -std=c++17 \
  -O2 \
  -I "$BASEDIR" \
  -I "$PY_INCLUDE" \
  common/params_pyx.cpp \
  common/params_min.cc \
  $PY_LINK \
  -o common/params_pyx.so
echo "  done: $(ls -lh common/params_pyx.so | awk '{print $5}')"

echo "[4/4] Verifying..."
python -c "
import sys; sys.path.insert(0, '$BASEDIR')
from common.params_pyx import Params, UnknownKeyName
p = Params()
# Verify all dp_cam_decel keys are registered
for k in ['dp_cam_decel','dp_cam_decel_mode','dp_cam_decel_start',
          'dp_cam_decel_end','dp_cam_decel_bump_dist','dp_cam_decel_bump_speed',
          'dp_cam_decel_safety_factor']:
  assert p.check_key(k), f'MISSING: {k}'
print('  All dp_cam_decel keys OK')
try:
  p.check_key('NonExistentKey123')
  print('  ERROR: should have raised')
except UnknownKeyName:
  print('  UnknownKeyName raised correctly')
print('SUCCESS')
"
