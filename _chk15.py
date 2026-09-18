import struct
b = open("common/params_pyx.so","rb").read()
for p in [0x16138, 0x16080, 0x160b0]:
    words = [struct.unpack_from("<I", b, p+4*k)[0] for k in range(3)]
    print(hex(p), " ".join("%08x" % w for w in words))
