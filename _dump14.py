import struct
data = open('common/params_pyx.so','rb').read()
acc = data.find(b"AccessToken")
# walk the sorted table: start at AccessToken, follow null-terminated strings
# The table is sorted by (len, value). AccessToken is first (len 11? A c c e s s T o k e n = 11).
# Let's verify sort order and count.
o = acc
keys = []
while True:
    e = data.find(b"\x00", o)
    if e < 0: break
    s = data[o:e]
    if not s: break
    keys.append(s.decode("latin1"))
    o = e + 1
    # stop if next string looks like it's not a param key (e.g. contains non-ascii or too long)
    if len(keys) > 400: break
print("count:", len(keys))
print("first 5:", keys[:5])
print("last 5:", keys[-5:])
# check sorted by (len, val)
def keyf(k): return (len(k), k)
is_sorted = all(keyf(keys[i]) <= keyf(keys[i+1]) for i in range(len(keys)-1))
print("sorted by (len,val):", is_sorted)
# where does it break?
for i in range(len(keys)-1):
    if keyf(keys[i]) > keyf(keys[i+1]):
        print("break at", i, keys[i], "->", keys[i+1])
        break
