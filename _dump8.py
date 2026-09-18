import struct
data = open('common/params_pyx.so','rb').read()
start = data.find(b"dp_0813")
# walk forward from start, following null-separated strings, until a non-string byte appears
o = start
keys = []
while True:
    e = data.find(b"\x00", o)
    if e < 0: break
    s = data[o:e]
    if not s or any(c not in b"abcdefghijklmnopqrstuvwxyz0123456789_" for c in s):
        break
    keys.append(s.decode("latin1"))
    o = e + 1
    if o > start + 4000:
        break
end = o
print("dp_ contiguous keys:", len(keys))
print("last:", keys[-3:])
print("region end:", hex(end))
print("bytes after end:", repr(data[end:end+48]))
n=0; j=end
while j < len(data) and data[j]==0:
    n+=1; j+=1
print("NUL run after region end:", n)
