import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

# Parse ELF header
assert so[:4] == b'\x7fELF'
ei_class = so[4]  # 1=32bit, 2=64bit
print(f"ELF class: {ei_class} (2=64-bit)")
e_phoff = struct.unpack_from('<Q', so, 32)[0]
e_phentsize = struct.unpack_from('<H', so, 54)[0]
e_phnum = struct.unpack_from('<H', so, 56)[0]
print(f"Program headers: {e_phnum}, offset={e_phoff}, size={e_phentsize}")

# Parse program headers
sections = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    p_type = struct.unpack_from('<I', so, off)[0]
    p_flags = struct.unpack_from('<I', so, off+4)[0]
    p_offset = struct.unpack_from('<Q', so, off+8)[0]
    p_vaddr = struct.unpack_from('<Q', so, off+16)[0]
    p_paddr = struct.unpack_from('<Q', so, off+24)[0]
    p_filesz = struct.unpack_from('<Q', so, off+32)[0]
    p_memsz = struct.unpack_from('<Q', so, off+40)[0]
    p_align = struct.unpack_from('<Q', so, off+48)[0]
    sections.append((p_type, p_flags, p_offset, p_vaddr, p_filesz, p_memsz, p_align))
    tnames = {1:"LOAD", 2:"DYNAMIC", 3:"INTERP", 4:"NOTE", 6:"PHDR", 0x6474e551:"GNU_PROPERTY", 0x6474e552:"GNU_RELRO"}
    tname = tnames.get(p_type, f"0x{p_type:x}")
    fname = {4:"R", 2:"W", 1:"X"}
    fstr = "".join(fname.get(b, "") for b in [1,2,4] if p_flags & b)
    print(f"  {tname:12s} flags={fstr:3s} off=0x{p_offset:06x} vaddr=0x{p_vaddr:06x} filesz=0x{p_filesz:06x} memsz=0x{p_memsz:06x}")

# Find the section containing our key table at offset 254880
key_offset = 254880
for i, (p_type, p_flags, p_offset, p_vaddr, p_filesz, p_memsz, p_align) in enumerate(sections):
    if p_type == 1:  # LOAD
        if p_offset <= key_offset < p_offset + p_filesz:
            print(f"\nKey table in segment {i}: vaddr offset within segment = 0x{key_offset - p_offset:x}")
            print(f"  Segment file range: 0x{p_offset:x} - 0x{p_offset + p_filesz:x}")
            print(f"  Segment mem range:  0x{p_offset} + {p_memsz} = 0x{p_memsz:x} bytes in memory")
            print(f"  File size: 0x{p_filesz:x}, Mem size: 0x{p_memsz:x}")
            print(f"  Extra memory (BSS): 0x{p_memsz - p_filesz:x}")
            break
