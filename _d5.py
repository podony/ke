import struct
data = open('common/params_pyx.so','rb').read()
# allKeys @0x28d40, look for ADRP instructions (opcode mask 0x97ffff) that load addresses near the .rodata key table (0x3e3a0-0x3eec7) or .data (0x4a000+)
# ADRP: immlo [30:29], immhi [23:5], Rd [4:0]; offset = (immhi:immlo) << 12; PC-aligned.
def adrp_targets(start, n):
    out = []
    for off in range(start, start+n, 4):
        ins = struct.unpack_from("<I", data, off)[0]
        if (ins & 0x9f000000) == 0x90000000:
            rd = ins & 0x1f
            immlo = (ins >> 29) & 0x3
            immhi = (ins >> 5) & 0x7ffff
            imm = (immhi << 2) | immlo
            if imm & (1 << 20):
                imm -= (1 << 21)
            tgt = (off & ~0xfff) + (imm << 12)
            out.append((off, rd, tgt))
    return out
rows = adrp_targets(0x28d40, 368)
for off, rd, tgt in rows:
    marker = ""
    if 0x3e3a0 <= tgt <= 0x3eec7:
        marker = "  <-- .rodata key string table"
    elif 0x4a000 <= tgt < 0x4b230:
        marker = "  <-- .data"
    elif 0x46628 <= tgt < 0x47628:
        marker = "  <-- .data.rel.ro (pointer/type table?)"
    print("%08x  x%d -> %x%s" % (off, rd, tgt, marker))
