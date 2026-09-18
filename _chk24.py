import struct
b = open("common/params_pyx.so","rb").read()
# check no relocations at 0x28eb0-0x28f1c exactly
off=0xe590; n=0x4b30//24
exact = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x28eb0 <= r_off < 0x28f1c:
        exact.append(hex(r_off))
print("relocs in orig fns:", exact)
# check bss region bytes zero
bss = b[0x4a230:0x4ab80]
print("bss nonzero:", any(bss))
# .data tail
print("data tail sample", b[0x49900:0x4a000].hex()[:80])
# .data rels in 0x4a700-0x4a230+? (end)
tail = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x4a700 <= r_off < 0x4a230:
        tail.append(hex(r_off))
print("data relocations 0x4a700-0x4b230:", tail)
# verify gap 0x270a0-0x28090 all zero and what's at 0x28090
print("gap zero:", not any(b[0x270a0:0x28090]))
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
for i in md.disasm(b[0x28090:0x28090+0x20], 0x28090):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
