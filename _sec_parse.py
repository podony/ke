import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

# Parse section headers
e_shoff = struct.unpack_from('<Q', so, 40)[0]
e_shentsize = struct.unpack_from('<H', so, 58)[0]
e_shnum = struct.unpack_from('<H', so, 60)[0]
e_shstrndx = struct.unpack_from('<H', so, 62)[0]

print(f"Section headers: {e_shnum} at offset 0x{e_shoff:x}")

# Get section name string table
shstrtab_off = e_shoff + e_shstrndx * e_shentsize
shstrtab_offset = struct.unpack_from('<Q', so, shstrtab_off + 24)[0]

def get_name(sh_off):
    sh_name = struct.unpack_from('<I', so, sh_off + 4)[0]
    end = so.index(b'\x00', shstrtab_offset + sh_name)
    return so[shstrtab_offset + sh_name:end].decode()

# Print all sections
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    sh_name = struct.unpack_from('<I', so, off + 4)[0]
    end = so.index(b'\x00', shstrtab_offset + sh_name)
    name = so[shstrtab_offset + sh_name:end].decode()
    sh_type = struct.unpack_from('<I', so, off + 8)[0]
    sh_flags = struct.unpack_from('<Q', so, off + 16)[0]
    sh_addr = struct.unpack_from('<Q', so, off + 24)[0]
    sh_offset = struct.unpack_from('<Q', so, off + 32)[0]
    sh_size = struct.unpack_from('<Q', so, off + 40)[0]
    flags_str = ""
    if sh_flags & 2: flags_str += "W"
    if sh_flags & 4: flags_str += "A"
    if sh_flags & 8: flags_str += "X"
    if sh_flags & 0x20: flags_str += "M"
    print(f"  [{i:2d}] {name:25s} type={sh_type:2d} flags={flags_str:4s} addr=0x{sh_addr:08x} off=0x{sh_offset:08x} size=0x{sh_size:08x}")
