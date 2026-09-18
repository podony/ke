import struct
data = open('common/params_pyx.so','rb').read()
e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
e_shentsize = struct.unpack_from("<H", data, 0x3a)[0]
e_shnum = struct.unpack_from("<H", data, 0x3c)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x3e)[0]
print("shoff", hex(e_shoff), "shnum", e_shnum, "shstrndx", e_shstrndx)
shstr_off = None
sections = []
for n in range(e_shnum):
    off = e_shoff + n*e_shentsize
    name, sh_type, flags, addr, offset, size = struct.unpack_from("<IIQQQQ", data, off)
    sections.append((name, sh_type, flags, addr, offset, size))
# shstr
so, ss = sections[e_shstrndx][4], sections[e_shstrndx][5]
names = data[so:so+ss]
def nm(n):
    e = names.find(b"\x00", n)
    return names[n:e].decode("latin1","replace")
for s in sections:
    print(s[1], hex(s[3]), hex(s[4]), hex(s[5]), nm(s[0]))
