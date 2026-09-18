import struct
d=open("common/params_pyx.so","rb").read()
shoff,shesize,shnum,shstrndx=struct.unpack_from("<QHHH",d,40)
print("shoff",shoff,"shesize",shesize,"shnum",shnum,"shstrndx",shstrndx)
strtab_off=strtab_size=0
# first pass to find .shstrtab: read header fields to locate section name strings
# shstrndx refers into a section; but we need shstrtab offset which is inside a section header.
# Iterate sections reading shstrndx after we have it.
sections=[]
for i in range(shnum):
    o=shoff+i*shesize
    name,sh_type,flags,addr,offset,size,link,info,align,entsize=struct.unpack_from("<IIQQQQIIQQ",d,o)
    sections.append((name,sh_type,flags,addr,offset,size,link,info,entsize))
# get shstrtab
sn,stype,sflags,saddr,ssoff,ssize,sl,sinfo,ses=sections[shstrndx]
names=b""
def nm(n):
    e=d.find(b"\x00",ssoff+n)
    return d[ssoff+n:e].decode()
# symtab and strtab and dynsym/dynstr
for i,s in enumerate(sections):
    n=nm(s[0])
    if n in (".symtab",".strtab",".dynsym",".dynstr"):
        print("sec",i,n,"off",s[4],"size",s[5],"entsize",s[8],"link",s[6])
def parse_syms(name,link):
    for i,s in enumerate(sections):
        if nm(s[0])==name:
            st,soff,ssize,entsize=s[4],s[4],s[5],s[8]
            strtab=None
            for j,t in enumerate(sections):
                if t[6]==link and nm(t[0]).endswith("strtab"):
                    strtab=t[4]
                    break
            cnt=ssize//entsize
            out=[]
            for k in range(cnt):
                st_name,info,st_other,st_shndx,sh_value,st_size=struct.unpack_from("<IBBHQQ",d,soff+k*entsize)
                if st_name:
                    e=d.find(b"\x00",strtab+st_name)
                    nmst=d[strtab+st_name:e].decode("latin1")
                    out.append((nmst,st_size,sh_value))
            return out
    return []
syms=parse_syms(".dynsym",0)
print("=== exported Params symbols (dynsym) ===")
for n,sz,val in syms:
    if "Params" in n:
        print("%6d %10x %s" % (sz,val,n))
print("=== all dynsym count:",len(syms))
