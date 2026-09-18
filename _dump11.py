import struct
data = open('common/params_pyx.so','rb').read()
P = 0x28e1d0
# dump 40 entries: (ptr, type)
for k in range(42):
    off = P + 16*k
    ptr = struct.unpack_from("<Q", data, off)[0]
    typ = struct.unpack_from("<I", data, off+8)[0]
    s = data[ptr:ptr+40].split(b"\x00")[0].decode("latin1", "replace") if 0 < ptr < len(data) else "?"
    print(k, hex(ptr), hex(typ), s)
