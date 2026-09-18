import re
data=open("common/params_pyx.so","rb").read()
# find long mangled symbols starting with _ZN that contain key-ish substrings
pat=re.compile(rb'_Z[0-9A-Za-z_]{4,120}')
seen={}
for m in pat.finditer(data):
    s=m.group()
    for key in [b'checkKey',b'getKeyType',b'allKeys',b'clearAll',b'std',b'unordered_map',b'keyType']:
        if key in s:
            seen[s]=seen.get(s,0)+1
for s in sorted(seen, key=lambda x:-seen[x])[:60]:
    print(seen[s], s.decode('latin1'))
