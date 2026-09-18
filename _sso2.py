import struct
from capstone import *
d=open("common/params_pyx.so","rb").read()
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True
def ins_list(va,n):
    return [ (i.mnemonic,i.op_str) for i in md.disasm(d[va:va+n], va) ]
# Disassemble a good chunk of the constructor and search for handling of "dp_long_missing_lead_warning"
# Find where the 30-char literal is referenced. In .rodata the string is at ~0x3e... but constructor builds on stack.
# Instead: find all 'strb' writing small size bytes and 'stur'/'str' pointer writes, look for a 0x1e (30) size.
# Let's dump constructor from 0x16060 to 0x17000 and grep for immediate 0x1e / 30.
chunk=d[0x16060:0x17200]
print("constructor length region, scanning for mov wX,#0x1e (30):")
for i in md.disasm(chunk,0x16060):
    if i.mnemonic in ("mov","movk","movz") and "w" in i.mnemonic:
        if "#0x1e" in i.op_str or ", #30" in i.op_str:
            print("  %x  %s %s" % (i.address,i.mnemonic,i.op_str))
# Also count occurrences of the byte 0x1e stored via strb near dp_ handling
print()
print("Search .rodata for the literal dp_long_missing_lead_warning to confirm it is a real static string:")
idx=d.find(b"dp_long_missing_lead_warning")
print("  found at file offset", idx, "-> VA", hex(idx) if idx>0 else None)
print("  surrounding bytes:", d[idx-4:idx+40].hex())
