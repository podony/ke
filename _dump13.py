import struct
data = open('common/params_pyx.so','rb').read()
P = 0x28e1d0
# dump raw 512 bytes around P as hex + ascii
seg = data[P-0x20:P+0x200]
for r in range(0, len(seg), 16):
    off = P-0x20+r
    hx = ' '.join('%02x' % b for b in seg[r:r+16])
    asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in seg[r:r+16])
    print('%08x  %s  %s' % (off, hx, asc))
