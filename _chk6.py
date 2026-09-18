import struct
b = open("common/params_pyx.so","rb").read()
def insn(off): return struct.unpack_from("<I", b, off)[0]
def dis(v):
    op = v & 0x9f000000
    return op
# scan constructor region 0x16060 .. 0x270a0 looking for pairs: adrp xN,#0x3e000
cnt = 0
i = 0x16060
while i < 0x27090 and cnt < 200:
    v = insn(i)
    if (v & 0x9f000000) == 0x90000000:  # adrp
        imm = ((v >> 21) & 0x7ffff)
        # sign extend 21
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        v2 = insn(i+4)
        if (v2 & 0x7f000000) == 0x91000000:  # add imm
            imm2 = (v2 >> 10) & 0xfff
            off2 = imm2 << 12 if v2 & 0x80000000 else imm2
            tgt = page + off2
            if 0x3eb00 <= tgt <= 0x3ec00:
                cnt += 1
                if cnt <= 8 or cnt >= 153:
                    keyoff = b.find(b"dp_0813")
                    print(f"i={hex(i)} tgt={hex(tgt)}")
                    print(f"  adrp: {v:08x} add: {v2:08x}")
    i += 4
print("total adrp/add->rodata pairs found:", cnt)
