import struct
d=open(chr(99)+chr(111)+chr(109)+chr(109)+chr(111)+chr(110)+chr(47)+chr(112)+chr(97)+chr(114)+chr(97)+chr(109)+chr(115)+chr(95)+chr(112)+chr(121)+chr(120)+chr(46)+chr(115)+chr(111),chr(98)+chr(114)).read()
fmt = chr(60)+chr(81)
e_shoff, = struct.unpack_from(fmt, d, 0x28)
e_shentsize, e_shnum, e_shstrndx = struct.unpack_from(chr(60)+3*chr(72), d, 0x3A)
shstr = struct.unpack_from(fmt, d, e_shoff+e_shstrndx*e_shentsize)[0]
NLB = bytes([0])
def nm(o):
    seg = d[shstr+o:]
    e = seg.index(NLB)
    return seg[:e].decode()
res=[]
for i in range(e_shnum):
    o=e_shoff+i*e_shentsize
    no,ty,fl,ad,off,sz = struct.unpack_from(chr(60)+2*chr(73)+4*chr(81), d, o)
    if ty in (1,8,9,11):
        res.append((nm(no),ty,ad,off,sz))
for r in res:
    print(r[0], r[1], hex(r[2]), hex(r[3]), hex(r[4]))