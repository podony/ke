import struct
b = open("common/params_pyx.so","rb").read()
e_phoff = struct.unpack_from("<Q", b, 0x20)[0]
e_phnum = struct.unpack_from("<H", b, 0x38)[0]
for k in range(e_phnum):
    off = e_phoff + k*56
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<IIQQQQQQ", b, off)
    if p_vaddr <= 0x4b9b8 < p_vaddr + p_memsz:
        print("segment covering 0x4b9b8: type", p_type, "flags", p_flags, "vaddr", hex(p_vaddr), "memsz", hex(p_memsz))
# file bytes at bss region
seg = b[0x4a9b8:0x4aa00]
print("file bytes at 0x4b9b8 (VA):", seg.hex())
print("all zero:", not any(seg))
# check relocations in bss
off=0xe590; n=0x4b30//24
hits = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x4b9b8 <= r_off < 0x4bb80:
        hits.append((hex(r_off), r_info & 0xffffffff, hex(r_add)))
print("relocs in 0x4b9b8-0x4bb80:", hits)
# check if .bss is in a loadable segment with write permission
print("e_type:", struct.unpack_from("<H", b, 0x10)[0])
