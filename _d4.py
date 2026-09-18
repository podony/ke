import struct
data = open('common/params_pyx.so','rb').read()
# allKeys @0x28d40 size 368 - dump it to find the count and table pointer
def dump(label, start, n):
    print("=== %s @%x (%d bytes) ===" % (label, start, n))
    for r in range(0, n, 16):
        off = start + r
        raw = data[off:off+16]
        qs = [struct.unpack_from("<Q", raw, k*8)[0] for k in range(len(raw)//8)]
        print('%08x  %s' % (off, ' '.join('%016x' % q for q in qs)))
dump("allKeys", 0x28d40, 368)
