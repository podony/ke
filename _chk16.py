import struct
b = open("common/params_pyx.so","rb").read()
shoff=0x2a4e78; shnum=35; shstrndx=34
shentsize=64
def sec(n):
    off = shoff + n*shentsize
    sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack_from("<IIQQQQ", b, off)
    return sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size
# section names
shstr_name, shstr_type, shstr_flags, shstr_addr, shstr_off, shstr_size = sec(shstrndx)
def name(sh_name):
    end = b.find(b"\x00", shstr_off+sh_name)
    return b[shstr_off+sh_name:end].decode()
for n in range(shnum):
    nm, t, fl, a, o, s = sec(n)
    print(n, name(nm), "type", t, "addr", hex(a), "off", hex(o), "size", hex(s))
