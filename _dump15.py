import struct
data = open('common/params_pyx.so','rb').read()
acc = data.find(b"AccessToken")
last = b"dp_long_missing_lead_warning"
lend = data.find(last) + len(last) + 1
# extract every null-terminated string in [acc, lend)
o = acc
keys = []
while o < lend:
    e = data.find(b"\x00", o)
    if e < 0 or e >= lend: break
    s = data[o:e]
    if s:
        keys.append(s.decode("latin1"))
    o = e + 1
print("param key count:", len(keys))
print("last 8:", keys[-8:])
# verify sorted by (len,val)
def keyf(k): return (len(k), k)
bad = [(i, keys[i], keys[i+1]) for i in range(len(keys)-1) if keyf(keys[i]) > keyf(keys[i+1])]
print("sort violations:", bad[:5])
# how many keys of each length for the dp_cam_decel family (all len>11)
for k in ["dp_cam_decel","dp_cam_decel_mode","dp_cam_decel_start","dp_cam_decel_end","dp_cam_decel_bump_dist","dp_cam_decel_bump_speed","dp_cam_decel_safety_factor"]:
    print(len(k), k, "present:", k in keys)
