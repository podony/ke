import re
data = open("_so_build/params_pyx.so","rb").read()
txt = open("common/params.cc","rb").read().decode()
keys = re.findall(r'\{\s*"([a-zA-Z0-9_]+)"', txt)
keys = sorted(set(keys))
print("total unique keys:", len(keys))
missing = [k for k in keys if k.encode() not in data]
print("missing:", len(missing))
for k in missing: print("  MISSING:", k)
# the 15 specific
need = ["dp_cam_decel","dp_cam_decel_mode","dp_cam_decel_start","dp_cam_decel_end","dp_cam_decel_bump_dist","dp_cam_decel_bump_speed","dp_cam_decel_safety_factor","DoReboot","DongleId","IMEI","IsMetric","IsOnroad","carFingerprint","error_description","uniqueID"]
print("--- the 15 critical ---")
for k in need:
    print("  ", k, "OK" if k.encode() in data else "MISSING")
