import re, json
t = open("common/params.cc", encoding="utf-8").read()
lines = t.split("\n")
in_table = False
keys = []
for line in lines:
    if "unordered_map<std::string, uint32_t> keys" in line:
        in_table = True
        continue
    if in_table:
        s = line.strip()
        if s.startswith("};"):
            break
        m = re.match(r'\{"([^"]+)", (\w+) \},', s)
        if m:
            keys.append((m.group(1), m.group(2)))
print("total keys in ke params.cc:", len(keys))
have = set(k for k, _ in keys)
so = set(x[0] for x in json.load(open("_keysoffs.json",encoding="utf-8")))
print("old .so keys missing:", len(so - have))
used = set(l.strip() for l in open("_used_keys.txt",encoding="utf-8") if l.strip())
print("used keys missing:", sorted(used - have))
need = ["dp_cam_decel","dp_cam_decel_mode","dp_cam_decel_start","dp_cam_decel_end","dp_cam_decel_bump_dist","dp_cam_decel_bump_speed","dp_cam_decel_safety_factor"]
print("dp_cam_decel missing:", [k for k in need if k not in have])
