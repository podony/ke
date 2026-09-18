import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

# Manually parse section headers
e_shoff = struct.unpack_from('<Q', so, 40)[0]  # 0x2a4e78
e_shentsize = struct.unpack_from('<H', so, 58)[0]  # 64
e_shnum = struct.unpack_from('<H', so, 60)[0]  # 35
e_shstrndx = struct.unpack_from('<H', so, 62)[0]  # 34

# shstrtab is section index 34
shstr_idx = e_shstrndx
shstr_hdr = e_shoff + shstr_idx * e_shentsize
# Elf64_Shdr: sh_name(4) sh_type(4) sh_flags(8) sh_addr(8) sh_offset(8) sh_size(8) sh_link(4) sh_info(4) sh_addralign(8) sh_entsize(8)
shstr_offset = struct.unpack_from('<Q', so, shstr_hdr + 24)[0]
shstr_size = struct.unpack_from('<Q', so, shstr_hdr + 32)[0]
print(f"shstrtab: file_offset=0x{shstr_offset:x} size=0x{shstr_size:x}")

shstr = so[shstr_offset:shstr_offset+shstr_size]
print(f"shstrtab content (first 100 bytes): {shstr[:100]}")

# Now parse all sections
def sec_name(idx):
    hdr = e_shoff + idx * e_shentsize
    name_off = struct.unpack_from('<I', so, hdr + 0)[0]
    end = shstr.index(b'\x00', name_off)
    return shstr[name_off:end].decode('ascii', errors='replace')

print(f"\n{'idx':>3} {'name':<25} {'type':>4} {'flags':>5} {'addr':>10} {'offset':>10} {'size':>10}")
print("-" * 80)
for i in range(e_shnum):
    hdr = e_shoff + i * e_shentsize
    name = sec_name(i)
    sh_type = struct.unpack_from('<I', so, hdr + 4)[0]
    sh_flags = struct.unpack_from('<Q', so, hdr + 8)[0]
    sh_addr = struct.unpack_from('<Q', so, hdr + 16)[0]
    sh_offset = struct.unpack_from('<Q', so, hdr + 24)[0]
    sh_size = struct.unpack_from('<Q', so, hdr + 32)[0]
    flags_str = ""
    if sh_flags & 2: flags_str += "W"
    if sh_flags & 4: flags_str += "A"
    if sh_flags & 8: flags_str += "X"
    if sh_flags & 0x20: flags_str += "M"
    if sh_flags & 0x40: flags_str += "I"
    marker = ""
    if 254880 >= sh_offset and 254880 < sh_offset + sh_size:
        marker = " <<< KEY TABLE HERE"
    if sh_size > 0 or i in [0, 34]:
        print(f"{i:3d} {name:<25} {sh_type:>4} {flags_str:>5} 0x{sh_addr:08x} 0x{sh_offset:08x} 0x{sh_size:08x}{marker}")
