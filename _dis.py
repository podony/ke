from capstone import *
import struct
d=open("common/params_pyx.so","rb").read()
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
md.detail=True
def disat(va, size, label):
    print("=== %s at VA %x (size %d) ===" % (label, va, size))
    for i in md.disasm(d[va-0x0:][:size] if False else b"", va):
        pass
# need to map VA -> file offset. .text sh_addr=0x16060 sh_offset=0x16060 (same). Actually check.
# From sections: .text off 0x16060 size 0x25ecc addr 0x16060  -> addr==offset, so file offset == vaddr for .text
for va,size,label in [(0x28eb0,36,"checkKey"),(0x28ee0,60,"getKeyType")]:
    print("=== %s VA %x size %d ===" % (label,va,size))
    code=d[va:va+size]
    for i in md.disasm(code, va):
        print("  %x  %-10s %s" % (i.address, i.mnemonic, i.op_str))
