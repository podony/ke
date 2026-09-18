import struct,sys
d=open(chr(99)+chr(111)+chr(109)+chr(109)+chr(111)+chr(110)+chr(47)+chr(112)+chr(97)+chr(114)+chr(97)+chr(109)+chr(115)+chr(95)+chr(112)+chr(121)+chr(120)+chr(46)+chr(115)+chr(111),chr(98)+chr(114)).read()
e_shoff, = struct.unpack_from(chr(60)+chr(81), d, 0x28)
e_shentsize, e_shnum, e_shstrndx = struct.unpack_from(chr(60)+chr(72)+chr(72)+chr(72), d, 0x3A)
shstr = struct.unpack_from(chr(60)+chr(81), d, e_shoff + e_shstrndx*e_shentsize)[0]
def sname(off):
    i=d.index(b(chr(0)*0+b0, off+shstr) if False else b(chr(48)*0+b0, off+shstr))