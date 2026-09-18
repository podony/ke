import struct
d=open("common/params_pyx.so","rb").read()
# .init_array file off 0x46608 size 0x10, addr 0x47608
init=struct.unpack_from("<Q",d,0x46608)[0]
print("init_array[0] =", hex(init), "(VA of static init function)")
# Map VA->file
shoff,shesize,shnum,shstrndx=0x2a4e78,64,35,34
sections=[]
for i in range(shnum):
    o=shoff+i*shesize
    name,sh_type,flags,addr,offset,size,link,info,align,entsize=struct.unpack_from("<IIQQQQIIQQ",d,o)
    sections.append((name,sh_type,flags,addr,offset,size,link,info,entsize))
ssoff=sections[shstrndx][4]
def nm(n):
    e=d.find(b"\x00",ssoff+n); return d[ssoff+n:e].decode("latin1")
def v2f(va):
    for s in sections:
        if s[1]==0 or s[3]==0: continue
        if s[3]<=va<s[3]+max(s[5],1): return s[4]+(va-s[3])
    return None
init_file=v2f(init)
print("init function at file", hex(init_file) if init_file else None)
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
# disassemble ~120 bytes of the init function
start=init
code=d[init_file:init_file+256]
print("=== static init function (first ~40 insns) ===")
for j,i in enumerate(md.disasm(code, start)):
    print("  %x  %-10s %s" % (i.address,i.mnemonic,i.op_str))
    if j>40: break
