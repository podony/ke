
import struct
d = open("common/params_pyx.so","rb").read()
print("magic", d[:4], "class", d[4], "data", d[5])
print("e_machine", hex(struct.unpack_from("<H", d, 18)[0]))
e_phoff = struct.unpack_from("<Q", d, 32)[0]
e_phentsize = struct.unpack_from("<H", d, 56)[0]
e_phnum = struct.unpack_from("<H", d, 58)[0]
print("phoff", e_phoff, "phentsize", e_phentsize, "phnum", e_phnum)
a0 = d.find(b"AccessToken")
end = d.find(b"dp_long_missing_lead_warning") + len(b"dp_long_missing_lead_warning") + 1
print("table file range", a0, end)
for n in range(e_phnum):
    off = e_phoff + n*e_phentsize
    p_type, p_flags = struct.unpack_from("<II", d, off)
    p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<QQQQQQ", d, off+8)
    if p_type == 1:  # PT_LOAD
        covers = (p_offset <= a0 < p_offset+p_filesz) and (p_offset <= end < p_offset+p_filesz)
        print("LOAD off=%x vaddr=%x filesz=%x memsz=%x flags=%x covers_table=%s" % (p_offset,p_vaddr,p_filesz,p_memsz,p_flags,covers))

