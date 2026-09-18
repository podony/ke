from capstone import *
d=open("common/params_pyx.so","rb").read()
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True
# The constructor 0x16060 builds std::string objects on stack. For libc++8:
#   short (<=22): word0 low byte = size, bit 31 of word0? Actually libc++8:
#   size_t __size_; char __data_[16+1] (or long ptr)
#   If long: __data_[0] holds pointer.
# Let's find the string size getter: look for `and wX, wY, #0x3f` or a check of bit.
# Scan constructor for the pattern used to compute string length for hashing.
start=0x16060; end=0x16060+0x800
found=[]
for i in md.disasm(d[start:end], start):
    m=i.mnemonic
    if m in ("and","ubfx","lsr","lsl") and ("#0x3f" in i.op_str or "#0x1f" in i.op_str or "#31" in i.op_str or "lsl" in i.op_str and "#1" in i.op_str):
        found.append((i.address,m,i.op_str))
print("candidate length-extract instructions in constructor:")
for a,m,o in found[:30]:
    print("  %x  %s %s" % (a,m,o))
