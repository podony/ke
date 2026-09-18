import struct
data = open('common/params_pyx.so','rb').read()
e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
e_shentsize = struct.unpack_from("<H", data, 0x3a)[0]
e_shnum = struct.unpack_from("<H", data, 0x3c)[0]
sections = []
for n in range(e_shnum):
    off = e_shoff + n*e_shentsize
    fields = struct.unpack_from("<IIQQQQIIQQ", data, off)
    sections.append(fields)
# find symtab (sh_type==2) and its strtab link
for i,s in enumerate(sections):
    if s[1] == 2:
        st_idx = i
sym = sections[st_idx]
st_offset, st_size, st_link, st_entsize = sym[4], sym[5], sym[6], sym[9]
print("symtab off", hex(st_offset), "size", hex(st_size), "link", st_link, "entsize", st_entsize)
strsec = sections[st_link]
str_off, str_size = strsec[4], strsec[5]
count = st_size // st_entsize
def getname(no):
    e = data.find(b"\x00", str_off+no)
    return data[str_off+no:e].decode("latin1","replace")
out = []
for k in range(count):
    o = st_offset + k*st_entsize
    st_name, st_info, st_other, st_shndx, st_value, st_size2 = struct.unpack_from("<IBBHQQ", data, o)
    out.append((getname(st_name), st_value, st_size2))
for nm, v, s in out:
    if "checkKey" in nm or "allKeys" in nm or "getKeyType" in nm or ("Params" in nm and s > 0 and v != 0):
        print(nm, hex(v), s)
open('_syms.txt','w').write('\n'.join('%s %x %d' % t for t in out))
print("total syms:", len(out))
