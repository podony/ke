import struct
data = open('common/params_pyx.so','rb').read()
last = b"dp_long_missing_lead_warning"
end = data.find(last) + len(last) + 1
print("table end:", hex(end))
print("bytes after:", repr(data[end:end+40]))
# find the full .rodata string pool extent: walk from 0x3e000 to see where the contiguous string pool ends
# Instead, find a large NUL run (padding) near the end of the file / after the string pool.
# Search for the pointer table: 8-byte aligned pointers in [0x3e000, 0x3f000] range
base_lo = 0x3e000
base_hi = 0x3f000
found = []
for base in range(0x3e000, 0x3f000, 8):
    ok = True
    cnt = 0
    for k in range(40):
        p = struct.unpack_from("<Q", data, base + 8*k)[0]
        if base_lo <= p < base_hi:
            cnt += 1
    if cnt >= 35:
        found.append((hex(base), cnt))
print("pointer table candidates:", found[:10])
