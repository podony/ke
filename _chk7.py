import struct, re
b = open("common/params_pyx.so","rb").read()
def insn(off): return struct.unpack_from("<I", b, off)[0]
i = 0x16060
while i < 0x270a0:
    v = insn(i)
    if (v & 0x9f000000) == 0x90000000:
        imm = ((v >> 21) & 0x7ffff)
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        v2 = insn(i+4)
        if (v2 & 0x7f000000) == 0x91000000:
            imm2 = (v2 >> 10) & 0xfff
            off2 = imm2 << 12 if v2 & 0x80000000 else imm2
            tgt = page + off2
            if 0x3ec00 <= tgt <= 0x3f000:
                print(f"i={hex(i)} tgt={hex(tgt)} adrp={v:08x} add={v2:08x}")
    i += 4
