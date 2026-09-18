import struct
b = open("common/params_pyx.so","rb").read()
off=0xe590; size=0x4b30
n = size//24
types = {}
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    t = r_info & 0xffffffff
    types[t] = types.get(t,0)+1
print("dyn reloc types:", types)
# count relocations whose offset is inside .text (0x16060-0x3bf30)
tc = 0
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x16060 <= r_off < 0x3bf30:
        tc += 1
print("relocations inside .text:", tc)
# plt relocs
p = 0
for k in range(0, 0x1c80//24):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, 0x130c0+k*24)
    p += 1
print("plt reloc count", p)
# check .rodata end 0x3fb21 and OPENPILOT_PREFIX content
print(b[257735:257735+20])
