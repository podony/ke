import os
import subprocess
import glob
import hashlib
import shutil
import datetime
from openpilot.common.basedir import BASEDIR

android_packages = ("com.neokii.optool", )

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
        if app == "com.mnsoft.mappyobn":
          mappy_ok = True
    else:
      _apk_diag("APK already current: " + apk_path)
      if app == "com.mnsoft.mappyobn":
        mappy_ok = True

  if mappy_ok:
    grant_mappy_permissions()
    _apk_diag("mappy permissions granted")

def pm_apply_packages(cmd):
  for p in android_packages:
    system("pm %s %s" % (cmd, p))

if __name__ == "__main__":
  update_apks()

