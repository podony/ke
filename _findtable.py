
import struct
data = open("common/params_pyx.so", "rb").read()
a0 = data.find(b"AccessToken")
s0 = data.find(b"dp_0813")
end = data.find(b"dp_long_missing_lead_warning") + len(b"dp_long_missing_lead_warning") + 1
n = 0
o = a0
while o < end:
    e = data.find(b"\x00", o)
    n += 1
    o = e + 1
print("keys:", n)

# 1) find 8-byte LE values in a wide window that equal a0, s0, or any key offset
key_offsets = []
o = a0
while o < end:
    key_offsets.append(o)
    e = data.find(b"\x00", o)
    o = e + 1

hits_by_key = {ko: [] for ko in key_offsets}
W = 4096
for ko in key_offsets:
    for k in range(ko - W, ko + W):
        if 0 <= k <= len(data) - 8:
            v = struct.unpack_from("<Q", data, k)[0]
            if v == ko:
                hits_by_key[ko].append(k)

for ko in key_offsets:
    if hits_by_key[ko]:
        print("key at", ko, "-> pointers at", hits_by_key[ko][:6])

