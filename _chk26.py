import struct
b = open("common/params_pyx.so","rb").read()
# gap region and just after
seg = b[0x270a0-0x20:0x28100]
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
print("--- around 0x27080 (before gap) ---")
for i in md.disasm(b[0x27080:0x270a0], 0x27080):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
print("--- 0x28090-0x280f0 ---")
for i in md.disasm(b[0x28090:0x280f0], 0x28090):
    print("%x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
