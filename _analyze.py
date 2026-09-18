
import struct
data = open("common/params_pyx.so","rb").read()
i = data.find(b"dp_0813")
j = data.find(b"OPENPILOT_PREFIX")
print("strblock start", i, "end", j)
# Find 8-byte values that point into the string block region [i-8000, j+400]
lo, hi = i - 8000, j + 400
hits = []
for k in range(0, len(data)-8, 8):
    v = struct.unpack_from("<Q", data, k)[0]
    if lo <= v <= hi:
        hits.append((k, v))
print("pointer-sized hits:", len(hits))
for k, v in hits[:80]:
    # what string is at v?
    e = data.find(b"\0", v)
    s = data[v:e]
    tag = s[:40].decode("latin1") if s and all(32<=b<127 for b in s) else repr(data[v:v+12])
    print(k, hex(v), v-i, tag)

