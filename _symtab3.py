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
def symtab():
    for i,s in enumerate(sections):
        if nm(s[0])==".symtab":
            soff,ssize,entsize=s[4],s[5],s[8]; cnt=ssize//entsize
            for k in range(cnt):
                st_name,info,st_other,st_shndx,sh_value,st_size=struct.unpack_from("<IBBHQQ",d,soff+k*entsize)
                if st_name:
                    e=d.find(b"\x00",strtaboff+st_name)
                    name=d[strtaboff+st_name:e].decode("latin1")
                    yield name,int(sh_value),int(st_size),st_shndx
syms=[s for s in symtab()]
print("total syms:",len(syms))
for target in [0x15f50,0x14f80,0x28730,0x293f0]:
    for name,val,size,shx in syms:
        if val==target:
            print("VA 0x%x -> size 0x%x  %s" % (target,size,name))
ts=sorted([(val,name,size) for name,val,size,shx in syms if shx==10 and val>0])
print("num .text syms:",len(ts))
prev_end=None; prev_name=None
for val,name,size in ts:
    if prev_end and val-prev_end>0x80:
        print("GAP 0x%x - 0x%x (len 0x%x) after %s" % (prev_end, val, val-prev_end, prev_name))
    prev_end=val+size; prev_name=name
