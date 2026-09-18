import re
src = open("common/params.cc","rb").read().decode()
keys = re.findall(r'\{"([^"]+)",', src)
print("total keys in params.cc:", len(keys))
data = open("common/params_pyx.so","rb").read()
missing = [k for k in keys if k.encode() not in data]
print("missing from .so:", len(missing))
for k in missing: print("  MISSING:", k)
