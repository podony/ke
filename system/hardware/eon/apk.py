import os
import subprocess
import glob
import hashlib
import shutil
import datetime
from openpilot.common.basedir import BASEDIR

android_packages = ("com.neokii.optool", )

# Known-good SHA256 of the committed MAPPY APK (apk/com.mnsoft.mappyobn.apk,
# 60515194 bytes). Used to verify integrity before the APK is ever pushed to
# the device, so a corrupted or placeholder APK is never silently installed.
MAPPY_PKG = "com.mnsoft.mappyobn"
MAPPY_SHA256 = "ea4e8cc0673ede332721985c7a5aae67f021c7230ae51e7aabeb17245ca1b1c7"
# Permissions that MUST end up granted for MAPPY to run silently in the
# background and share road/camera data over localhost. Re-checked (read back
# from dumpsys) after they are granted, as the final stage of double-verify.
MAPPY_REQUIRED_PERMS = ("ACCESS_FINE_LOCATION", "WAKE_LOCK", "INTERNET")

def get_installed_apks():
  dat = subprocess.check_output(["pm", "list", "packages", "-f"], encoding='utf8').strip().split("\n")
  ret = {}
  for x in dat:
    if x.startswith("package:"):
      v, k = x.split("package:")[1].split("=")
      ret[k] = v
  return ret

def install_apk(path):
  # can only install from a world readable path. On the Termux/bionic EON
  # /sdcard is not always present, so prefer /data/local/tmp and fall back.
  candidates = ["/data/local/tmp", "/sdcard"]
  for d in candidates:
    try:
      install_path = os.path.join(d, os.path.basename(path))
      shutil.copyfile(path, install_path)
      ret = subprocess.call(["pm", "install", "-r", install_path])
      try:
        os.remove(install_path)
      except OSError:
        pass
      if ret == 0:
        return True
      print("pm install failed (rc=%s) for %s via %s" % (ret, path, d))
    except Exception as e:
      print("install_apk: %s via %s: %s" % (path, d, e))
  return False

def start_offroad():
  set_package_permissions()
  system("am start -n ai.comma.plus.offroad/.MainActivity")

def set_package_permissions():
  try:
    output = subprocess.check_output(['dumpsys', 'package', 'ai.comma.plus.offroad'], encoding="utf-8")
    given_permissions = output.split("runtime permissions")[1]
  except Exception:
    given_permissions = ""

  wanted_permissions = ["ACCESS_FINE_LOCATION", "READ_PHONE_STATE", "READ_EXTERNAL_STORAGE"]
  for permission in wanted_permissions:
    if permission not in given_permissions:
      pm_grant("ai.comma.plus.offroad", "android.permission."+permission)

  appops_set("ai.comma.plus.offroad", "SU", "allow")
  appops_set("ai.comma.plus.offroad", "WIFI_SCAN", "allow")

def appops_set(package, op, mode):
  system(f"LD_LIBRARY_PATH= appops set {package} {op} {mode}")

def pm_grant(package, permission):
  system(f"pm grant {package} {permission}")

def system(cmd):
  try:
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
  except subprocess.CalledProcessError as e:
    pass

# *** external functions ***

def _apk_diag(msg):
  try:
    with open('/data/params/eon_apk_diag.txt', 'a') as f:
      f.write("%s %s\n" % (datetime.datetime.now().isoformat(), msg))
  except Exception:
    pass

# Permissions Mappy (com.mnsoft.mappyobn) needs to run silently in the
# background and share camera/road data over localhost. Grant them after
# install; failures are non-fatal.
def grant_mappy_permissions():
  for perm in ("ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "INTERNET",
               "ACCESS_NETWORK_STATE", "ACCESS_WIFI_STATE", "WAKE_LOCK",
               "READ_PHONE_STATE", "READ_EXTERNAL_STORAGE", "FOREGROUND_SERVICE"):
    system("pm grant com.mnsoft.mappyobn android.permission.%s" % perm)
  system("LD_LIBRARY_PATH= appops set com.mnsoft.mappyobn RUN_IN_BACKGROUND allow")

# Double-verification stages for the MAPPY install. Each stage returns a bool
# and logs a timestamped PASS/FAIL line to /data/params/eon_apk_diag.txt.
# Called from update_apks(); a stage never raises - failure is logged and
# reported to the caller, not fatal to the boot.

def _capture(cmd):
  # Like system(), but returns stdout as text (None on any error). Needed by
  # the double-verify stages, which parse command output.
  try:
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, encoding="utf-8")
  except Exception as e:
    _apk_diag("_capture(%s) error: %s" % (cmd, e))
    return None

def _sha256_file(path):
  h = hashlib.sha256()
  with open(path, 'rb') as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()

def verify_mappy_before_install(apk_path):
  # Stage 1: integrity of the repo APK BEFORE it is pushed to the device.
  try:
    digest = _sha256_file(apk_path)
  except Exception as e:
    _apk_diag("MAPPY verify-BEFORE FAIL: cannot hash repo APK %s: %s" % (apk_path, e))
    print("MAPPY pre-install integrity check FAILED: %s" % e, flush=True)
    return False
  ok = digest == MAPPY_SHA256
  _apk_diag("MAPPY verify-BEFORE %s (repo sha256 %s)" % ("PASS" if ok else "FAIL", digest))
  if not ok:
    print("MAPPY pre-install integrity check FAILED: got %s, want %s" % (digest, MAPPY_SHA256), flush=True)
  return ok

def verify_mappy_installed():
  # Stage 2: after pm install, re-hash the APK file(s) the device reports via
  # `pm path`. Only the installed bytes are trusted; there is NO fallback to
  # the repo hash. If none of the reported paths can be read, the stage FAILS.
  out = _capture("pm path %s" % MAPPY_PKG)
  if not out:
    _apk_diag("MAPPY verify-AFTER FAIL: pm path returned no output")
    print("MAPPY post-install check FAILED: pm path returned no output", flush=True)
    return False
  paths = []
  for line in out.splitlines():
    line = line.strip()
    if line.startswith("package:"):
      paths.append(line.split(":", 1)[1].strip())
  if not paths:
    _apk_diag("MAPPY verify-AFTER FAIL: pm path returned no package path")
    print("MAPPY post-install check FAILED: no package path", flush=True)
    return False
  for path in paths:
    try:
      digest = _sha256_file(path)
    except Exception as e:
      _apk_diag("MAPPY verify-AFTER: cannot read installed %s: %s" % (path, e))
      continue
    ok = digest == MAPPY_SHA256
    _apk_diag("MAPPY verify-AFTER %s (installed %s sha256 %s)" % ("PASS" if ok else "FAIL", path, digest))
    if not ok:
      print("MAPPY post-install check FAILED: %s sha256 %s" % (path, digest), flush=True)
    return ok
  _apk_diag("MAPPY verify-AFTER FAIL: no reported apk path readable (%s)" % ", ".join(paths))
  print("MAPPY post-install check FAILED: no reported apk path readable", flush=True)
  return False

def verify_mappy_permissions():
  # Stage 3: after grant_mappy_permissions(), read back the runtime permission
  # state from dumpsys and confirm every critical permission is granted=true.
  out = _capture("dumpsys package %s" % MAPPY_PKG)
  if not out:
    _apk_diag("MAPPY verify-PERMS FAIL: dumpsys returned nothing")
    print("MAPPY permission read-back FAILED: dumpsys returned nothing", flush=True)
    return False
  granted = set()
  for line in out.splitlines():
    # runtime permission lines look like:
    #   android.permission.WAKE_LOCK: granted=true
    key, sep, val = line.strip().partition(": granted=")
    if not sep:
      continue
    perm = key.rsplit(".", 1)[-1].strip()
    if val.strip().lower() == "true":
      granted.add(perm)
  missing = [p for p in MAPPY_REQUIRED_PERMS if p not in granted]
  ok = not missing
  _apk_diag("MAPPY verify-PERMS %s (missing: %s)" % ("PASS" if ok else "FAIL", ",".join(missing) or "none"))
  if not ok:
    print("MAPPY permission read-back FAILED, missing: %s" % ",".join(missing), flush=True)
  return ok

def update_apks():
  # install apks
  installed = get_installed_apks()

  install_apks = glob.glob(os.path.join(BASEDIR, "apk/*.apk"))
  _apk_diag("update_apks start, apks: %s" % str(install_apks))
  for apk in install_apks:
    app = os.path.basename(apk)[:-4]
    if app not in installed:
      installed[app] = None

  #cloudlog.info("installed apks %s" % (str(installed), ))

  mappy_ok = False
  for app in installed.keys():
    apk_path = os.path.join(BASEDIR, "apk/"+app+".apk")
    if not os.path.exists(apk_path):
      continue

    h1 = hashlib.sha1(open(apk_path, 'rb').read()).hexdigest()
    h2 = None
    if installed[app] is not None:
      try:
        h2 = hashlib.sha1(open(installed[app], 'rb').read()).hexdigest()
      except Exception as e:
        _apk_diag("cannot read installed apk %s: %s (will reinstall)" % (installed[app], e))
        h2 = None
      print("comparing version of %s  %s vs %s" % (app, h1, h2))

    if h2 is None or h1 != h2:
      print("installing %s" % app, flush=True)
      _apk_diag("installing %s" % app)

      if app == MAPPY_PKG:
        if not verify_mappy_before_install(apk_path):
          print("MAPPY install skipped: pre-install integrity check failed", flush=True)
          _apk_diag("MAPPY install skipped: pre-install integrity check failed")
          continue

      success = install_apk(apk_path)
      if not success:
        print("needing to uninstall %s" % app, flush=True)
        system("pm uninstall %s" % app)
        success = install_apk(apk_path)

      if not success:
        _apk_diag("APK install FAILED: " + apk_path)
        print("apk install failed, continuing: " + apk_path, flush=True)
      else:
        _apk_diag("APK install OK: " + apk_path)
        if app == MAPPY_PKG:
          mappy_ok = verify_mappy_installed()
    else:
      _apk_diag("APK already current: " + apk_path)
      if app == MAPPY_PKG:
        mappy_ok = verify_mappy_installed()

  if mappy_ok:
    grant_mappy_permissions()
    _apk_diag("mappy permissions granted")
    perms_ok = verify_mappy_permissions()
    _apk_diag("mappy perms stage: %s" % ("PASS" if perms_ok else "FAIL"))

def pm_apply_packages(cmd):
  for p in android_packages:
    system("pm %s %s" % (cmd, p))

if __name__ == "__main__":
  update_apks()

