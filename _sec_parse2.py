import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

e_shoff = struct.unpack_from('<Q', so, 40)[0]
e_shentsize = struct.unpack_from('<H', so, 58)[0]
e_shnum = struct.unpack_from('<H', so, 60)[0]
e_shstrndx = struct.unpack_from('<H', so, 62)[0]

# Get section name string table
shstrtab_off = e_shoff + e_shstrndx * e_shentsize
shstrtab_offset = struct.unpack_from('<Q', so, shstrtab_off + 24)[0]
shstrtab_size = struct.unpack_from('<Q', so, shstrtab_off + 40)[0]
print(f"shstrtab: offset=0x{shstrtab_offset:x} size=0x{shstrtab_size:x}")

def get_name(sh_off):
    sh_name = struct.unpack_from('<I', so, sh_off + 4)[0]
    if sh_name + shstrtab_offset >= len(so):
        return "?"
    end = sh_name
    while end < sh_name + shstrtab_size and so[shstrtab_offset + end] != 0:
        end += 1
    return so[shstrtab_offset + sh_name:end].decode('ascii', errors='replace')

# Find .rodata, .data.rel.ro, .data, .bss
key_offset = 254880  # 0x3e3a0
print(f"\nKey table at file offset 0x{key_offset:x}")
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    name = get_name(off)
    sh_type = struct.unpack_from('<I', so, off + 8)[0]
    sh_flags = struct.unpack_from('<Q', so, off + 16)[0]
    sh_addr = struct.unpack_from('<Q', so, off + 24)[0]
    sh_offset = struct.unpack_from('<Q', so, off + 32)[0]
    sh_size = struct.unpack_from('<Q', so, off + 40)[0]
    if sh_type == 1 and sh_size > 0:  # PROGBITS
        flags_str = ""
        if sh_flags & 2: flags_str += "W"
        if sh_flags & 4: flags_str += "A"
        if sh_flags & 8: flags_str += "X"
        if sh_flags & 0x20: flags_str += "M"
        contains_key = "<<< KEY TABLE" if sh_offset <= key_offset < sh_offset + sh_size else ""
        if name in ['.rodata', '.data', '.data.rel.ro', '.bss', '.text', '.rodata.str1.1', '.dynstr', '.symtab'] or contains_key:
            print(f"  [{i:2d}] {name:25s} flags={flags_str:4s} addr=0x{sh_addr:08x} off=0x{sh_offset:08x} size=0x{sh_size:08x} {contains_key}")
