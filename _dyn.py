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
# collect dynamic string table
for sh in secs:
    n = secname(sh)
    if n == ".dynstr":
        dstr, dstr_sz = sh[4], sh[5]
    if n == ".dynsym":
        dsym_off, dsym_sz, dsym_entsz = sh[4], sh[5], sh[8]
    if n == ".dynamic":
        dyn_off, dyn_sz = sh[4], sh[5]
strtab = d[dstr:dstr+dstr_sz]
def dstr(i):
    j = strtab.find(b"\0", i)
    return strtab[i:j].decode(errors="replace")
# dynamic symbols: SHT_DYNSYM is 11 -> entsize 24
import collections
def dynstrname(st_name):
    return dstr(st_name)
needed, soname, symbols = [], None, []
for k in range(dsym_sz // 24):
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", d, dsym_off + k*24)
    if st_name:
        symbols.append(dstr(st_name))
for k in range(dyn_sz//8):
    tag, val = struct.unpack_from("<II", d, dyn_off + k*8)
    if tag == 0: break
    if tag == 1: needed.append(dstr(val))
    if tag == 0x1e: soname = dstr(val)
print("SONAME:", soname)
print("NEEDED:", needed)
print("dynsym count:", len(symbols))
print("some symbols:", symbols[:15])
