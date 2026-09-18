b = open("common/params_pyx.so","rb").read()
for name,va,size in [("checkKey",0x28eb0,36),("getKeyType",0x28ee0,60)]:
    seg = b[va:va+size]
    print(name, seg.hex())
