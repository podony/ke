import struct
b = open("common/params_pyx.so","rb").read()
strtab_off = 0x2974c8; symtab_off = 0x28dce8
entsz = 24
n = (0x2974c8 - symtab_off)//entsz
for k in range(n):
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", b, symtab_off+k*entsz)
    if 0x27000 <= st_value <= 0x28100 and st_size>0:
        end = b.find(b"\x00", strtab_off+st_name)
        nm = b[strtab_off+st_name:end].decode("latin1")
        print(hex(st_value), st_size, nm[:80])
