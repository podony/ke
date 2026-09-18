
import re, struct
data = open("common/params_pyx.so", "rb").read()
i = data.find(b"dp_0813")
# extend backwards while previous 8 bytes are printable NUL-terminated
off = i
while off > 0:
    e = data.rfind(b"\0", max(0, off-64), off)
    s = data[e+1:off]
    if not s or len(s) > 64 or not all(32 <= b < 127 for b in s):
        break
    off = e + 1
print("table str start", off, "dp_0813 at", i, "n dp keys so far", (i-off))
keys = []
o = off
while True:
    e = data.find(b"\0", o)
    s = data[o:e]
    if not s:
        break
    keys.append((o, s.decode()))
    o = e + 1
    if o - off > 20000:
        break
print("total keys", len(keys))
for o, s in keys:
    print(o, s)

