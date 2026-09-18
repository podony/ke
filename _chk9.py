import struct, re
b = open("common/params_pyx.so","rb").read()
def insn(off): return struct.unpack_from("<I", b, off)[0]
# search whole .text for any load of address within [0x3eb30,0x3eeab]
found = []
i = 0x16060
while i < 0x16060+0x25ecc:
    v = insn(i)
    cands = []
    if (v & 0x9f000000) == 0x90000000:  # adrp
        imm = ((v >> 21) & 0x7ffff)
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        v2 = insn(i+4)
        if (v2 & 0x7f000000) == 0x91000000:
            imm2 = (v2 >> 10) & 0xfff
            off2 = imm2 << 12 if v2 & 0x80000000 else imm2
            cands.append((page+off2, "adrp+add"))
        elif (v2 & 0x3b000000) == 0x39000000 or (v2 & 0x3b000000) == 0x39400000:
            cands.append((page, "adrp+ldur?"))
    if (v & 0x9f000000) == 0xf9400000:  # ldr x, [xN, #imm]
        pass
    for t,how in cands:
        if 0x3eb30 <= t <= 0x3eeab:
            found.append((i,t,how))
    i += 4
print("found:", len(found))
for f in found[:10]: print(f)
# also raw byte search for 'neko' mov pattern: 0x6e656b? mov w9,#0x6b6f => imm16 0x6b6f
pat = struct.pack("<I", 0x52806b6f)
i = b.find(pat)
print("mov w,#0x6b6f at", hex(i) if i>=0 else None)
# movk pattern for 'ne' 0x6e65 lsl16: 0x72a6e65? 0x72a00000 | 0x6e65<<5? movk w9,#0x6e65,lsl#16 => 0x72a6e650 + rt
pat2 = 0x72a6e650
# search
for off in range(0, 0x3b000, 4):
    v = insn(off)
    if (v & 0x7f800000) == 0x72a00000 and ((v>>5)&0xffff)==0x6e65 and ((v>>21)&3)==1:
        print("movk ne lsl16 at", hex(off))
