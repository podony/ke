import struct
b = open("common/params_pyx.so","rb").read()
base=0x16060; end=base+0x25ecc
pairs = []
i = base
while i < end:
    v = struct.unpack_from("<I", b, i)[0]
    if (v & 0x9f000000) == 0x90000000:
        imm = ((v >> 21) & 0x7ffff)
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        v2 = struct.unpack_from("<I", b, i+4)[0]
        if (v2 & 0x7f000000) == 0x91000000:
            imm2 = (v2 >> 10) & 0xfff
            off2 = imm2 << 12 if v2 & 0x80000000 else imm2
            pairs.append((i, page+off2))
    i += 4
lo = min(t for _,t in pairs); hi = max(t for _,t in pairs)
print("num pairs:", len(pairs), "range", hex(lo), hex(hi))
cnt_rodata = sum(1 for _,t in pairs if 0x3bf30 <= t < 0x40000)
print("targets into .rodata range:", cnt_rodata)
import collections
pages = collections.Counter(t & ~0xfff for _,t in pairs)
print("top pages:", pages.most_common(8))
