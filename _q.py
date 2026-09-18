import struct
d=open('common/params_pyx.so','rb').read()
# Find "checkKey" mangled symbol
for name in [b'checkKey', b'checkkey', b'Params']:
    i=0
    while True:
        i=d.find(name, i)
        if i<0: break
        # check if it looks like a symbol name (null terminated, ascii)
        j=i
        while j<len(d) and d[j] not in (0,):
            j+=1
        sym=d[i:j]
        if all(32<=c<127 for c in sym) and 4<len(sym)<200:
            print(name.decode(), 'at', hex(i), '->', sym.decode())
        i+=1
