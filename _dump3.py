import re
data = open('_ke_params.so','rb').read()
i = data.find(b"WheeledBody")
j = data.find(b"dp_vag_timebomb_bypass")
seg = data[i:j+25]
keys = [k.decode() for k in seg.split(b"\x00") if k]
print(len(keys))
print(keys)
