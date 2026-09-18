import struct
data = open('common/params_pyx.so','rb').read()
# locate the checkKey string constant near 0x3eec7-0x3eed0; find code referencing the .rodata pointer.
# The pointer table is an array of (const char*, uint32_t) pairs, 16 bytes each, in .rodata.
# Let's find it: search for 16-byte aligned blocks where the first qword points into [0x3e000,0x3f000] and second dword is a small int.
# Better: the C++ table is an array of pairs, so pointers are contiguous 8-byte words.
# The strings start around 0x3e000 (AccessToken). Let's find the first pointer (AccessToken) and the pattern.
acc = data.find(b"AccessToken")
print("AccessToken at", hex(acc))
# pointer table should be at some address P where data[P] = acc (or acc + offset).
# Search the whole file for 8-byte little-endian value == acc
targets = [acc]
# also try a window
for v in targets:
    pat = struct.pack("<Q", v)
    i = 0
    hits = []
    while True:
        i = data.find(pat, i)
        if i < 0: break
        hits.append(hex(i))
        i += 1
    print("pointer to AccessToken found at:", hits[:20])
