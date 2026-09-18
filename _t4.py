import struct
data = open('common/params_pyx.so','rb').read()
e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
e_shentsize = struct.unpack_from("<H", data, 0x3a)[0]
e_shnum = struct.unpack_from("<H", data, 0x3c)[0]
sections = []
for n in range(e_shnum):
    off = e_shoff + n*e_shentsize
    name, sh_type, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIQQQQIIQQ", data, off)
    sections.append(dict(name=name, sh_type=sh_type, addr=addr, offset=offset, size=size, link=link, info=info, entsize=entsize))
symtab = sections[33]; strtab = sections[34]
# verify names
print("symtab entsize", symtab['entsize'], "count", symtab['size']//symtab['entsize'], "strtab off", hex(strtab['offset']), "size", hex(strtab['size']))
def getname(no):
    e = data.find(b"\x00", strtab['offset']+no)
    return data[strtab['offset']+no:e].decode("latin1","replace")
symcount = symtab['size']//symtab['entsize']
out = []
for k in range(symcount):
    o = symtab['offset'] + k*symtab['entsize']
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", data, o)
    nm = getname(st_name)
    out.append((nm, st_value, st_size))
# print symbols related to Params
for nm, v, s in out:
    if "Params" in nm or "checkKey" in nm or "allKeys" in nm or "getKeyType" in nm:
        print(nm, hex(v), s)
open('_syms.txt','w').write('\n'.join('%s %x %d' % t for t in out))
print("total syms:", len(out))
