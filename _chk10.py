b = open("common/params_pyx.so","rb").read()
d = b[0x16060:0x16800]
# show first 200 bytes as 32-bit words
import struct
words = struct.unpack_from("<64I", d)
for k in range(0, 64, 4):
    print(hex(0x16060+k*4), " ".join("%08x" % w for w in words[k:k+4]))
