data = open("common/params_pyx.so","rb").read()
# parse sections quickly
import struct
assert data[:4] == b"\x7fELF"
e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
e_shentsize = struct.unpack_from("<H", data, 0x3a)[0]
e_shnum = struct.unpack_from("<H", data, 0x3c)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x3e)[0]
secs = []
for i in range(e_shnum):
    off = e_shoff + i*e_shentsize
    sh = struct.unpack_from("<IIQQQQIIQQ", data, off)
    secs.append(sh)
shstr = secs[e_shstrndx]
def name(sh):
    n = sh[0]
    return data[shstr[4]:shstr[4]+shstr[5]][n:].split(b"\0")[0].decode()
for sh in secs:
    n = name(sh)
    if n in (".rodata",".data.rel.ro",".data",".bss",".text",".init_array"):
        print(n, hex(sh[4]), hex(sh[5]))
# find free space in .rodata: strings start 0x3e3a0. Check content around end of rodata
