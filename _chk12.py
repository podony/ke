import struct
b = open("common/params_pyx.so","rb").read()
def insn(off): return struct.unpack_from("<I", b, off)[0]
# find "dp_0813" literal VA = 0x3eb82; scan for references
found = []
base = 0x16060; end = base+0x25ecc
i = base
while i < end:
    v = insn(i)
    if (v & 0x9f000000) == 0x90000000:
        imm = ((v >> 21) & 0x7ffff)
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        if 0x3e000 <= page < 0x40000:
            v2 = insn(i+4)
            if (v2 & 0x7f000000) == 0x91000000:
                imm2 = (v2 >> 10) & 0xfff
                off2 = imm2 << 12 if v2 & 0x80000000 else imm2
                t = page + off2
                if 0x3eb30 <= t <= 0x3eeab:
                    found.append((i, t, hex(v), hex(v2)))
    i += 4
print("found:", len(found))
for f in found[:6]: print(f)
