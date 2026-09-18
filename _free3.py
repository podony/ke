d = open("common/params_pyx.so","rb").read()
def is_ascii(s):
    return all(32 <= c < 127 for c in s)
# strings from 0x3e3a0, sorted storage; find each string's end and any gaps
import json
ks = json.load(open("_keysoffs.json"))
items = [(int(o,16) if isinstance(o,str) else o, n) for n,o in ks]
items.sort()
prev = 0x3e3a0
free = []
for off,n in items:
    if off > prev:
        free.append((prev, off, d[prev:off]))
    end = off + len(n) + 1
    if end > prev: prev = end
if prev < 0x46000:
    free.append((prev, 0x46000, d[prev:0x46000]))
for a,b,s in free[:20]:
    print(hex(a),hex(b), b, s[:40])
print("total free before 0x46000:", sum(b-a for a,b,_ in free))
