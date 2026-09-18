import re
data = open('common/params_pyx.so','rb').read()
i = data.find(b"WheeledBody")
j = data.find(b"dp_vag_timebomb_bypass")
seg = data[i:j+25]
keys = seg.split(b"\x00")
keys = [k.decode() for k in keys if k]
print(len(keys))
print(keys)
print('offset i:', hex(i), 'end:', hex(j+25))
