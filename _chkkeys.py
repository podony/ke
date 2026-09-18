import json
ks = json.load(open("_keysoffs.json"))
names = [k[0] if isinstance(k, list) else k for k in ks]
names = sorted(set(n.lower() for n in names))
need = ["dp_cam_decel","dp_cam_decel_mode","dp_cam_decel_start","dp_cam_decel_end","dp_cam_decel_bump_dist","dp_cam_decel_bump_speed","dp_cam_decel_safety_factor"]
print("count:", len(ks))
print("missing from so:", [n for n in need if n not in names])
