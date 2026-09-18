b = open("common/params_pyx.so","rb").read()
# rodata file 254880 .. 257735
ro = b[254880:257735]
parts = ro.split(b"\x00")
print("num strings (split incl trailing):", len(parts))
s = [p.decode("latin1") for p in parts if p]
print("num nonempty:", len(s))
# find position of OPENPILOT_PREFIX
i = b.find(b"OPENPILOT_PREFIX")
print("OPENPILOT_PREFIX at", i)
# show the last 5 strings with file offsets
idx = 0
offs = []
for p in parts:
    offs.append(idx); idx += len(p)+1
pairs = list(zip([p.decode("latin1") for p in parts], offs))
pairs = [x for x in pairs if x[0]]
for p,o in pairs[-6:]:
    print(repr(p), "file", 254880+o)
