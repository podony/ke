import struct
data = open('common/params_pyx.so','rb').read()
def s_at(o, n=48):
    return data[o:o+n].split(b"\x00")[0].decode("latin1","replace")
# Dump 0x28e1c8 .. 0x28e218 as 16-byte rows, and interpret as 8-byte qwords.
base = 0x28e1c8
for r in range(0, 96, 16):
    off = base + r
    raw = data[off:off+16]
    q1 = struct.unpack_from("<Q", raw, 0)[0]
    q2 = struct.unpack_from("<Q", raw, 8)[0]
    print('%08x  %016x %016x' % (off, q1, q2))
