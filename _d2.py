import struct
data = open('common/params_pyx.so','rb').read()
# 0x3efbf = "ApiCache_DriveStats"? Let's check what string is at 0x3efbf
def s_at(o, n=48):
    return data[o:o+n].split(b"\x00")[0].decode("latin1","replace")
print("0x3efbf ->", repr(s_at(0x3efbf)))
print("0x3e3a0 ->", repr(s_at(0x3e3a0)))
# The pointer table is contiguous pairs (ptr, type). ptr0=0x3e3a0 at 0x28e1d0.
# So pairs are 16 bytes each. But my earlier 16-stride dump gave garbage for entry1.
# Let me re-dump with 16-byte stride carefully.
P = 0x28e1d0
rows = []
for k in range(6):
    off = P + 16*k
    ptr = struct.unpack_from("<Q", data, off)[0]
    typ = struct.unpack_from("<I", data, off+8)[0]
    s = s_at(ptr) if 0x3e000 <= ptr < 0x3f000 else "?"
    rows.append((k, hex(ptr), hex(typ), s))
for r in rows:
    print(r)
