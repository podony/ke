import struct
b = open("common/params_pyx.so","rb").read()
e_phoff = struct.unpack_from("<Q", b, 0x20)[0]
e_phnum = struct.unpack_from("<H", b, 0x38)[0]
for k in range(e_phnum):
    off = e_phoff + k*56
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<IIQQQQQQ", b, off)
    print(k, "type", p_type, "flags", p_flags, "off", hex(p_offset), "vaddr", hex(p_vaddr), "filesz", hex(p_filesz), "memsz", hex(p_memsz))
