import struct
data = open('common/params_pyx.so','rb').read()
# parse ELF program headers
e_phoff = struct.unpack_from("<Q", data, 32)[0]
e_phentsize = struct.unpack_from("<H", data, 56)[0]
e_phnum = struct.unpack_from("<H", data, 58)[0]
segments = []
for n in range(e_phnum):
    off = e_phoff + n * e_phentsize
    p_type, p_flags = struct.unpack_from("<II", data, off)
    p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<QQQQQQ", data, off + 8)
    segments.append((p_type, p_flags, p_offset, p_vaddr, p_filesz, p_memsz))
    print("seg type=%d flags=%d off=%x vaddr=%x filesz=%x memsz=%x" % (p_type, p_flags, p_offset, p_vaddr, p_filesz, p_memsz))
# find PT_LOAD segment covering 0x28e1d0
for (t, f, o, v, fs, ms) in segments:
    if t == 1 and o <= 0x28e1d0 < o + fs:
        print("0x28e1d0 in LOAD vaddr=%x off=%x -> file2vaddr delta = %x" % (v, o, v - o))
