import struct
d=open("common/params_pyx.so","rb").read()
print("len",len(d))
e_shoff=struct.unpack_from("<Q",d,0x28)[0]
e_shentsize=struct.unpack_from("<H",d,0x3A)[0]
e_shnum=struct.unpack_from("<H",d,0x3C)[0]
e_shstrndx=struct.unpack_from("<H",d,0x3E)[0]
print("e_shoff",hex(e_shoff),"e_shentsize",e_shentsize,"e_shnum",e_shnum,"e_shstrndx",e_shstrndx)
# program headers
e_phoff=struct.unpack_from("<Q",d,0x20)[0]
e_phentsize=struct.unpack_from("<H",d,0x36)[0]
e_phnum=struct.unpack_from("<H",d,0x38)[0]
print("e_phoff",hex(e_phoff),"e_phentsize",e_phentsize,"e_phnum",e_phnum)
# check tail
print("tail bytes:", d[-64:].hex())
