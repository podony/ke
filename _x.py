import struct
f = open(r"common\params_pyx.so","rb").read()
def ins_at(a): return struct.unpack_from("<I", f, a)[0]
def note(ins, a):
    if (ins & 0x7F800000) == 0x11000000: return "ADD imm=0x%x" % ((ins>>12)&0xFFF)
    if (ins & 0x7FC00000) == 0x31000000: return "ADDW imm=0x%x" % ((ins>>12)&0xFFF)
    if (ins & 0xFF800000) == 0xD2800000: return "MOV imm=0x%x" % ((ins>>10)&0xFFF)
    if (ins & 0xFFC00000) == 0xF9400000: return "LDR imm=0x%x" % (((ins>>10)&0xFFF)*8)
    if (ins & 0xFFC00000) == 0xF8400000: return "LDR imm=0x%x" % ((ins>>10)&0xFFF)
    if (ins & 0xFFC00000) == 0xF9000000: return "STR imm=0x%x" % (((ins>>10)&0xFFF)*8)
    if (ins & 0x9F000000) == 0x90000000:
        immlo=(ins>>29)&3; immhi=(ins>>5)&0x7FFFF; imm=(immhi<<2)|immlo
        if imm&(1<<20): imm-=(1<<21)
        return "ADRP page=0x%x" % ((a & ~0xFFF)+(imm<<12))
    if (ins & 0xFC000000) == 0xD63F0000: return "BL 0x%x" % (a + ((ins&0x3FFFFFF)*4))
    if (ins & 0x7FC00000) == 0x54000000: return "B.cond 0x%x" % (a + (((ins&0x3FFFFFF)>>2)*4))
    if ins == 0xD65F03C0: return "RET"
    if (ins & 0xFF000000) == 0xD1000000: return "SUB imm=0x%x" % (((ins>>10)&0xFFF)*8)
    if (ins & 0xFF000000) == 0x91000000: return "ADD imm=0x%x" % (((ins>>10)&0xFFF)*8)
    if (ins & 0xFFC00000) == 0xF1000000: return "CMP imm=0x%x" % (((ins>>10)&0xFFF)*8)
    if (ins & 0xFFC00000) == 0xFB000000: return "SUBS reg"
    if (ins & 0xFFE00000) == 0x11000000: return "ADD(sub)"
    return ""
# The constructor is 10652 bytes = 2663 instr. Look for the ADRP+LDR/ADD pattern that
# loads the key-table. The map is built from a static array of (key, type) pairs.
# Find all ADRP instructions in the constructor that target the .rodata page 0x3e000
# (where the key strings live) and note the ADD that follows (offset into string).
import itertools
adrps=[]
for a in range(0x16060, 0x16060+10652, 4):
    i=ins_at(a)
    if (i & 0x9F000000)==0x90000000:
        immlo=(i>>29)&3; immhi=(i>>5)&0x7FFFF; imm=(immhi<<2)|immlo
        if imm&(1<<20): imm-=(1<<21)
        pg=(a & ~0xFFF)+(imm<<12)
        rd=i&0x1F
        # next instr: ADD reg, reg, #imm?
        nxt=ins_at(a+4)
        off = None
        if (nxt & 0x7F800000)==0x11000000 and ((nxt>>5)&0x1F)==rd:
            off=(nxt>>12)&0xFFF
        adrps.append((a, pg, rd, off))
# print those targeting 0x3e000
print("ADRP to 0x3e000 in constructor:", sum(1 for a,pg,rd,off in adrps if pg==0x3e000))
for a,pg,rd,off in adrps:
    if pg==0x3e000:
        print("  addr 0x%x rd=%d addoff=0x%x" % (a,rd,off if off is not None else -1))
PYEOF2=None
