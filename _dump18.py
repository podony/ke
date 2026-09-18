import struct
data = open('common/params_pyx.so','rb').read()
acc = data.find(b"AccessToken")
last = b"dp_long_missing_lead_warning"
lend = data.find(last) + len(last) + 1
o = acc
ptrs = []
while o < lend:
    e = data.find(b"\x00", o)
    if e < 0 or e >= lend: break
    if data[o:e]:
        ptrs.append(o)
    o = e + 1
N = len(ptrs)
# type table: N uint32 values (mostly 0x02 PERSISTENT, some 0x20 DONT_LOG).
# Search for a 4-aligned base T where data[T+4k] is in the allowed set for >= N-2 entries.
allowed = {0, 2, 4, 8, 16, 32, 34, 36, 38}
best = []
T0 = ptrs[0]
for T in range(T0 - 0x4000, T0 + 0x4000, 4):
    ok = 0
    for k in range(N):
        if T + 4*k + 4 > len(data): break
        v = struct.unpack_from("<I", data, T+4*k)[0]
        if v in allowed:
            ok += 1
        else:
            break
    if ok >= N - 2:
        best.append((T, ok))
print("type table candidates:", [(hex(t), ok) for t, ok in best][:20])
for T, ok in best[:3]:
    vals = [struct.unpack_from("<I", data, T+4*k)[0] for k in range(N)]
    print("T", hex(T), "distinct:", sorted(set(vals)))
    print("  first 10:", vals[:10])
    print("  last 10:", vals[-10:])
