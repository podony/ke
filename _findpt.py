import struct
data = open('common/params_pyx.so','rb').read()
acc = data.find(b"AccessToken")
last = b"dp_long_missing_lead_warning"
lend = data.find(last) + len(last) + 1
o = acc
offs = []
while o < lend:
    e = data.find(b"\x00", o)
    if e < 0 or e >= lend: break
    if data[o:e]:
        offs.append(o)
    o = e + 1
N = len(offs)
print("N =", N)
# find base B (8-aligned) where data[B+8k]==offs[k] for all k
found = None
for B in range(0x28e000, 0x28e400, 8):
    ok = True
    for k in range(N):
        if struct.unpack_from("<Q", data, B+8*k)[0] != offs[k]:
            ok = False; break
    if ok:
        found = B; break
print("pointer table base:", hex(found) if found else "NOT in 0x28e000-0x28e400")
if not found:
    # widen
    for B in range(0x280000, 0x2a0000, 8):
        ok = True
        for k in range(N):
            if B+8*k+8 > len(data): break
            if struct.unpack_from("<Q", data, B+8*k)[0] != offs[k]:
                ok = False; break
        if ok:
            found = B; break
    print("wider search base:", hex(found) if found else "NOT FOUND")
