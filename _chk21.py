import struct
b = open("common/params_pyx.so","rb").read()
so = b[0x28ee0:0x28f1c]
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
for i in md.disasm(so, 0x28ee0):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
print("=== find callee 0x15f50 ===")
so2 = b[0x15f50:0x15f50+0x80]
for i in md.disasm(so2, 0x15f50):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
