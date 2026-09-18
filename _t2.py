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
# For each position p where data[p]==strings[0][0], count how many string offsets appear as 8-byte values in data[p : p + 8*4096]
def count_in_window(p):
    seg = data[p:p+8*4096]
    cnt = 0
    offs = set(o for o,_ in strings)
    for k in range(0, len(seg)-8, 8):
        v = struct.unpack_from("<Q", seg, k)[0]
        if v in offs:
            cnt += 1
    return cnt
t0 = strings[0][0]
pat0 = struct.pack("<Q", t0)
cand = []
i = 0
while True:
    i = data.find(pat0, i)
    if i < 0: break
    cand.append(i)
    i += 1
for B in cand:
    c = count_in_window(B)
    print("pos", hex(B), "aligned", B%8==0, "window-hit", c)
