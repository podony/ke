import struct, re
data = open('common/params_pyx.so','rb').read()
P = 0x28e1d0
# find the largest aligned base such that all 236 (ptr,type) entries have ptr in [0x3e000,0x3f000]
N = 236
best = None
for base in range(P - 0x800, P + 0x100, 8):
    ok = True
    cnt = 0
    for k in range(N):
        off = base + 16*k
        if off + 16 > len(data): break
        ptr = struct.unpack_from("<Q", data, off)[0]
        typ = struct.unpack_from("<I", data, off+8)[0]
        if 0x3e000 <= ptr < 0x3f000 and typ in (0,2,4,8,16,34,36,38):
            cnt += 1
    if cnt > 230:
        best = (base, cnt)
print("best base:", best)
base = best[0]
keys = []
for k in range(N):
    off = base + 16*k
    ptr = struct.unpack_from("<Q", data, off)[0]
    typ = struct.unpack_from("<I", data, off+8)[0]
    s = data[ptr:ptr+40].split(b"\x00")[0].decode("latin1","replace")
    keys.append((k, hex(ptr), hex(typ), s))
open('_table.txt','w').write('\n'.join('%d %s %s %s' % t for t in keys))
print("first:", keys[0])
print("last:", keys[-1])
dp = [t for t in keys if t[3].startswith('dp_')]
print("dp_ entries:", len(dp))
print("last 3 dp:", dp[-3:])
