import struct
b = open("common/params_pyx.so","rb").read()
strtab_off = 0x2974c8
symtab_off = 0x28dce8
entsz = 24
n = (0x2974c8 - symtab_off)//entsz
hits = []
for k in range(n):
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", b, symtab_off+k*entsz)
    end = b.find(b"\x00", strtab_off+st_name)
    nm = b[strtab_off+st_name:end].decode("latin1")
    if "basic_string" in nm or "ssn" in nm.lower():
        if st_size != 0:
            hits.append((hex(st_value), st_size, nm))
for h in hits[:40]: print(h)
print("total:", len(hits))
