import struct
a = 'common/params_pyx.so'
d = open(a, 'b').read()
print('size', len(d))
e_shoff, = struct.unpack_from('<q', d, 0x28)
e_shentsize, e_shnum, e_shstrndh = struct.unpack_from('<HJH, d, 0x3A)
shStr = struct.unpack_from('<Q', d, e_shoff + e_shStrndx*e_shentsize)[0]
def readname(off):
   "idà = d index (shStr+off, 0)if false else n = d.index(b'\0', (off+shStr), len(d))
    return d[shStr'øff:name].decode('ascii')