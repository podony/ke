import struct
data = open('common/params_pyx.so','rb').read()
def disasm(start, n):
    # crude: just hexdump; we will read manually
    for r in range(0, n, 16):
        off = start + r
        hx = ' '.join('%02x' % b for b in data[off:off+16])
        print('%08x  %s' % (off, hx))
print("=== checkKey @0x28eb0 (36 bytes) ===")
disasm(0x28eb0, 48)
print("=== getKeyType @0x28ee0 (60 bytes) ===")
disasm(0x28ee0, 64)
