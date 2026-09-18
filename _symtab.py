import struct
data=open("common/params_pyx.so","rb").read()
e_shoff=struct.unpack_from("<Q",data,40)[0]
e_shentsize=struct.unpack_from("<H",data,52)[0]
e_shnum=struct.unpack_from("<H",data,54)[0]
e_shstrndx=struct.unpack_from("<H",data,56)[0]
sh=[]
for i in range(e_shnum):
    o=e_shoff+i*e_shentsize
    name,type_,flags,addr,offset,size=struct.unpack_from("<IIQQQQ",data,o)
    sh.append((name,type_,flags,addr,offset,size))
def secname(n):
    st=sh[e_shstrndx]
    return data[st[4]+n:st[4]+st[5]].split(b"\x00")[0].decode()
# print symtab, strtab, dynsym
for i,s in enumerate(sh):
    nm=secname(s[0])
    if nm in (".symtab",".strtab",".dynsym",".dynstr",".rodata",".text",".data.rel.ro"):
        print(i,nm,"type",s[1],"offset",s[4],"size",s[5],"addr",hex(s[3]))
