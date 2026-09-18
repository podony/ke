import struct
d=open("common/params_pyx.so","rb").read()
shoff,shesize,shnum,shstrndx=0x2a4e78,64,35,34
sections=[]
for i in range(shnum):
    o=shoff+i*shesize
    name,sh_type,flags,addr,offset,size,link,info,align,entsize=struct.unpack_from("<IIQQQQIIQQ",d,o)
    sections.append((name,sh_type,flags,addr,offset,size,link,info,entsize))
ssoff=sections[shstrndx][4]
def nm(n):
    e=d.find(b"\x00",ssoff+n)
    return d[ssoff+n:e].decode("latin1")
def v2f(va):
    for s in sections:
        if s[1]==0 or s[3]==0: continue
        if s[3]<=va<s[3]+max(s[5],1):
            return s[4]+(va-s[3])
    return None
for va in [0x4b800,0x4b000,0x3e000]:
    print("VA %x -> file %s" % (va, hex(v2f(va)) if v2f(va) is not None else None))
print()
print("sections covering .data.rel.ro / .data / .bss:")
for i,s in enumerate(sections):
    if nm(s[0]) in (".data.rel.ro",".data",".bss"):
        print(i,nm(s[0]),"addr",hex(s[3]),"off",hex(s[4]),"size",hex(s[5]),"flags",s[2])
