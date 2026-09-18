from capstone import *
import struct
d=open("common/params_pyx.so","rb").read()
def v2f(va):
    # .text addr==offset for this build (verified earlier)
    return va
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True
def dis(va,n):
    for i in md.disasm(d[va:va+n], va):
        print("  %x  %-8s %s" % (i.address,i.mnemonic,i.op_str))
# getKeyType 0x28ee0-0x28f18: builds a temporary std::string into [sp, #8] from x1
print("=== getKeyType (builds temp std::string in [sp,#8]) ===")
dis(0x28ee0, 0x3c)
