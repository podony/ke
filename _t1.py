import struct
data = open('common/params_pyx.so','rb').read()
acc = data.find(b"AccessToken")
last = b"dp_long_missing_lead_warning"
lend = data.find(last) + len(last) + 1
o = acc
strings = []
while o < lend:
    e = data.find(b"\x00", o)
    if e < 0 or e >= lend: break
    strings.append((o, data[o:e].decode("latin1")))
    o = e + 1
N = len(strings)
print("N =", N)
# The pointer table should be N 8-byte qwords == [s[0] for s in strings].
# Find its base: search for a run where data[base+8k] == string_offset_k for all k.
# Use the first and a few middle/last offsets to locate base.
targets = [strings[0][0], strings[1][0], strings[2][0], strings[N//2][0], strings[N-1][0]]
# The pointer table is contiguous; base = position where data[base]==t0, data[base+8]==t1, ...
# Find all 8-aligned positions where data[pos]==t0
t0 = strings[0][0]
pat0 = struct.pack("<Q", t0)
cand = []
i = 0
while True:
    i = data.find(pat0, i)
    if i < 0: break
    if i % 8 == 0:
        cand.append(i)
    i += 1
print("t0 candidates:", [hex(c) for c in cand])
for B in cand:
    ok = sum(1 for k,(off,_) in enumerate(strings) if struct.unpack_from("<Q", data, B+8*k)[0] == off)
    print("base", hex(B), "match", ok, "/", N)
