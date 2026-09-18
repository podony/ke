import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

# Parse .symtab to find the params key map symbol
e_shoff = struct.unpack_from('<Q', so, 40)[0]
e_shentsize = struct.unpack_from('<H', so, 58)[0]
e_shnum = struct.unpack_from('<H', so, 60)[0]

# .symtab is at index 32, .strtab at index 33
symtab_hdr = e_shoff + 32 * e_shentsize
strtab_hdr = e_shoff + 33 * e_shentsize

symtab_offset = struct.unpack_from('<Q', so, symtab_hdr + 24)[0]
symtab_size = struct.unpack_from('<Q', so, symtab_hdr + 32)[0]
strtab_offset = struct.unpack_from('<Q', so, strtab_hdr + 24)[0]
strtab_size = struct.unpack_from('<Q', so, strtab_hdr + 32)[0]
strtab = so[strtab_offset:strtab_offset+strtab_size]

# Elf64_Sym: st_name(4) st_info(1) st_other(1) st_shndx(2) st_value(8) st_size(8) = 24 bytes
nsyms = symtab_size // 24
print(f"Total symbols: {nsyms}")

# Search for symbols related to params
for i in range(nsyms):
    off = symtab_offset + i * 24
    st_name = struct.unpack_from('<I', so, off)[0]
    st_info = so[off+4]
    st_shndx = struct.unpack_from('<H', so, off+6)[0]
    st_value = struct.unpack_from('<Q', so, off+8)[0]
    st_size = struct.unpack_from('<Q', so, off+16)[0]
    
    end = st_name
    while end < len(strtab) and strtab[end] != 0:
        end += 1
    name = strtab[st_name:end].decode('ascii', errors='replace')
    
    if 'param' in name.lower() or 'keys' in name.lower() or 'checkKey' in name:
        print(f"  [{i}] {name:40s} shndx={st_shndx} value=0x{st_value:08x} size=0x{st_size:x}")
