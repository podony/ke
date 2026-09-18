import struct
b = open("common/params_pyx.so","rb").read()
off=0xe590; size=0x4b30
n = size//24
in_range = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x270a0 <= r_off <= 0x28ee0 or 0x4a000 <= r_off <= 0x4b230:
        in_range.append((hex(r_off), hex(r_add)))
print("relocations in .text gap / .data:", in_range)
# check relocations near 0x28eb0 (checkKey) and 0x28ee0 (getKeyType)
near = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x28000 <= r_off <= 0x2a000:
        near.append((hex(r_off), hex(r_add)))
print("relocations in 0x28000-0x2a000:", near)
# .bss
bss = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x4b230 <= r_off < 0x4b230+0x950:
        bss.append((hex(r_off), hex(r_add)))
print("relocations in .bss:", bss)
