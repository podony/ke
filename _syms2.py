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
strtaboff=None
for i,s in enumerate(sections):
    n=nm(s[0])
    if n==".strtab":
        strtaboff=s[4]
print("sections:")
for i,s in enumerate(sections):
    print(i,nm(s[0]),"off",hex(s[4]),"size",hex(s[5]),"addr",hex(s[3]),"entsize",s[8],"link",s[6])
def read_dynstr(off):
    e=d.find(b"\x00",off)
    return d[off:e].decode("latin1")
print("=== .dynsym entries containing Params or checkKey ===")
for i,s in enumerate(sections):
    if nm(s[0])==".dynsym":
        soff,ssize,entsize,link=s[4],s[5],s[8],s[6]
        # link section is dynstr
        dynstr_off=sections[link][4]
        cnt=ssize//entsize
        for k in range(cnt):
            st_name,info,st_other,st_shndx,sh_value,st_size=struct.unpack_from("<IBBHQQ",d,soff+k*entsize)
            if st_name:
                name=read_dynstr(dynstr_off+st_name)
                if "Params" in name or "checkKey" in name:
                    print("%d %6d %10x sh=%d %s" % (k,st_size,sh_value,st_shndx,name))
print("=== full .symtab (if present) checkKey/getKeyType ===")
for i,s in enumerate(sections):
    if nm(s[0])==".symtab":
        soff,ssize,entsize,link=s[4],s[5],s[8],s[6]
        cnt=ssize//entsize
        for k in range(cnt):
            st_name,info,st_other,st_shndx,sh_value,st_size=struct.unpack_from("<IBBHQQ",d,soff+k*entsize)
            if st_name:
                e=d.find(b"\x00",strtaboff+st_name)
                name=d[strtaboff+st_name:e].decode("latin1")
                if "Params" in name and ("checkKey" in name or "getKeyType" in name or "allKeys" in name or "clearAll" in name):
                    print("%6d %10x sh=%d %s" % (st_size,sh_value,st_shndx,name))
