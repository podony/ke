import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

e_shoff = struct.unpack_from('<Q', so, 40)[0]
e_shentsize = struct.unpack_from('<H', so, 58)[0]
e_shnum = struct.unpack_from('<H', so, 60)[0]
e_shstrndx = struct.unpack_from('<H', so, 62)[0]
print(f"e_shoff=0x{e_shoff:x} e_shentsize={e_shentsize} e_shnum={e_shnum} e_shstrndx={e_shstrndx}")

# Dump shstrtab raw
shstrtab_off = e_shoff + e_shstrndx * e_shentsize
print(f"shstrtab header at file offset 0x{shstrtab_off:x}")
for i in range(0, 64, 8):
    val = struct.unpack_from('<Q', so, shstrtab_off + i)[0]
    print(f"  +{i:2d}: 0x{val:016x}")
