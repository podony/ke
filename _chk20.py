import struct
b = open("common/params_pyx.so","rb").read()
so = b[0x28eb0:0x28f18]
words = [struct.unpack_from("<I", so, k*4)[0] for k in range(len(so)//4)]
def dis(v, pc):
    op = v & 0x9f000000
    out = "%08x" % v
    return out
# just print hex words with offsets, we already have capstone; use it
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
for i in md.disasm(so, 0x28eb0):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
