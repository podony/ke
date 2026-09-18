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
    e=d.find(b"\x00",ssoff+n); return d[ssoff+n:e].decode("latin1")
strtaboff=None
for i,s in enumerate(sections):
    if nm(s[0])==".strtab": strtaboff=s[4]
def dynstr():
    for i,s in enumerate(sections):
        if nm(s[0])==".dynstr": return s[4]
ds=dynstr()
def rname(off):
    e=d.find(b"\x00",off); return d[off:e].decode()
# .rela.plt gives PLT entries: r_offset = VA, info sym, addend=0
for i,s in enumerate(sections):
    if nm(s[0])==".rela.plt":
        soff,ssize,entsize=s[4],s[5],s[8]; cnt=ssize//entsize
        for k in range(cnt):
            off,info,add=struct.unpack_from("<QIQ",d,soff+k*entsize)
            sym=info>>32
            # dynsym
            dsym=sections[3]; dsymoff=dsym[4]; dsymes=dsym[8]
            st_name,info2,st_other,st_shndx,sh_value,st_size=struct.unpack_from("<IBBHQQ",d,dsymoff+sym*dsymes)
            print("PLT VA 0x%x  %s  (dynsym shval 0x%x)" % (off, rname(ds+st_name), sh_value))
