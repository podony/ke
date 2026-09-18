import struct
data = open('common/params_pyx.so','rb').read()
last = b"dp_vag_timebomb_bypass"
e = data.find(last) + len(last) + 1
print("table end offset:", hex(e))
print("next 80 bytes after table end:", repr(data[e:e+80]))
n = 0
j = e
while j < len(data) and data[j] == 0:
    n += 1; j += 1
print("NUL run after table end:", n, "-> next data at", hex(j))
new = [b"dp_cam_decel", b"dp_cam_decel_mode", b"dp_cam_decel_start", b"dp_cam_decel_end",
       b"dp_cam_decel_bump_dist", b"dp_cam_decel_bump_speed", b"dp_cam_decel_safety_factor"]
need = sum(len(k)+1 for k in new)
print("bytes needed:", need, "available NUL:", n)
