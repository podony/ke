import struct
b = open("common/params_pyx.so","rb").read()
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
so = b[0x2b840:0x2b840+0x60]
for i in md.disasm(so, 0x2b840):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
