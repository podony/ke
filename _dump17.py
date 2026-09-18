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
print("N =", N)
# pointer table = N 8-byte little-endian values == ptrs, contiguous, 8-aligned.
# Search for a base B (8-aligned) where data[B: B+8N] matches ptrs exactly.
# Use a sliding check with the first few and last few to narrow.
# Strategy: find all positions where data[pos] == ptrs[0] (8-aligned), then verify a window.
pat0 = struct.pack("<Q", ptrs[0])
cand = []
i = 0
while True:
    i = data.find(pat0, i)
    if i < 0: break
    if i % 8 == 0:
        cand.append(i)
    i += 1
print("base candidates (ptr0):", [hex(c) for c in cand][:10])
for B in cand[:10]:
    ok = 0
    for k in range(N):
        if struct.unpack_from("<Q", data, B+8*k)[0] == ptrs[k]:
            ok += 1
        else:
            break
    print("base", hex(B), "contiguous match:", ok)
