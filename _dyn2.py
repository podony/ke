import struct
d = open("common/params_pyx.so","rb").read()
e_shoff = struct.unpack_from("<Q", d, 0x28)[0]
e_shentsize = struct.unpack_from("<H", d, 0x3a)[0]
e_shnum = struct.unpack_from("<H", d, 0x3c)[0]
e_shstrndx = struct.unpack_from("<H", d, 0x3e)[0]
secs = []
for i in range(e_shnum):
    off = e_shoff + i*e_shentsize
    secs.append(struct.unpack_from("<IIQQQQIIQQ", d, off))
shstr = secs[e_shstrndx]
def secname(sh):
    n = sh[0]
    return d[shstr[4]:shstr[4]+shstr[5]][n:].split(b"\0")[0].decode()
dyn_off = dyn_sz = None
for sh in secs:
    if secname(sh) == ".dynamic":
        dyn_off, dyn_sz = sh[4], sh[5]
print("dynamic fileoff", hex(dyn_off), "size", dyn_sz)
print("first 60 bytes:", d[dyn_off:dyn_off+60].hex())
