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
print("n keys:", len(ptrs))
# find base B such that data[B + 8k] == ptrs[k] for all k
# ptrs[0] = acc. Find all 8-aligned positions where data[pos] == acc, then test each as candidate base.
pat0 = struct.pack("<Q", acc)
cand = []
i = 0
while True:
    i = data.find(pat0, i)
    if i < 0: break
    if i % 8 == 0:
        cand.append(i)
    i += 1
print("candidates for base (data==acc, 8-aligned):", [hex(c) for c in cand])
for B in cand:
    ok = sum(1 for k,p in enumerate(ptrs) if struct.unpack_from("<Q", data, B+8*k)[0] == p)
    print("base", hex(B), "matches", ok, "of", len(ptrs))
