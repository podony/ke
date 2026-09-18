import struct
data = open('common/params_pyx.so','rb').read()
i = data.find(b"WheeledBody")
# end of WheeledBody string incl NUL
e = i + len(b"WheeledBody") + 1
print("table end offset:", hex(e))
print("next 64 bytes after table end:", repr(data[e:e+64]))
# count NUL run after table end
n = 0
j = e
while j < len(data) and data[j] == 0:
    n += 1; j += 1
print("NUL run after table end:", n)
# total new key string bytes needed:
new = [b"dp_cam_decel", b"dp_cam_decel_mode", b"dp_cam_decel_start", b"dp_cam_decel_end",
       b"dp_cam_decel_bump_dist", b"dp_cam_decel_bump_speed", b"dp_cam_decel_safety_factor"]
need = sum(len(k)+1 for k in new)
print("bytes needed for new key strings:", need)
