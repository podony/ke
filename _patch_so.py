
import struct, sys

SO = "common/params_pyx.so"
NEW_KEYS = [
    b"dp_cam_decel",
    b"dp_cam_decel_mode",
    b"dp_cam_decel_start",
    b"dp_cam_decel_end",
    b"dp_cam_decel_bump_dist",
    b"dp_cam_decel_bump_speed",
    b"dp_cam_decel_safety_factor",
]

data = bytearray(open(SO, "rb").read())

# sanity: ELF header
assert data[:4] == b"\x7fELF", "not an ELF"
assert data[4] == 2, "not 64-bit"
assert data[18:22] == b"\x03\x00\x00\x00", "not x86-64/arm? check"
print("EI_CLASS", data[4], "EI_DATA", data[5], "e_machine", hex(struct.unpack_from("<H", data, 18)[0]))

# parse program headers to find PT_LOAD segments
e_phoff = struct.unpack_from("<Q", data, 32)[0]
e_phentsize = struct.unpack_from("<H", data, 56)[0]
e_phnum = struct.unpack_from("<H", data, 58)[0]
print("phoff", e_phoff, "phnum", e_phnum)
PT_LOAD = 1
segments = []
for n in range(e_phnum):
    off = e_phoff + n * e_phentsize
    p_type, p_flags = struct.unpack_from("<II", data, off)
    p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<QQQQQQ", data, off + 8)
    if p_type == PT_LOAD:
        segments.append((p_offset, p_filesz, p_vaddr, p_flags))
        print("LOAD off=%x size=%x vaddr=%x flags=%x" % (p_offset, p_filesz, p_vaddr, p_flags))

# locate the key table: string "dp_0813" ... "dp_long_missing_lead_warning"
s0 = data.find(b"dp_0813")
s_last = data.find(b"dp_long_missing_lead_warning")
assert s0 > 0 and s_last > s0
end_of_table = s_last + len(b"dp_long_missing_lead_warning") + 1  # include NUL
print("table strings region:", s0, end_of_table)

# which segment holds it?
seg = None
for (o, sz, v, fl) in segments:
    if o <= s0 < o + sz and o <= end_of_table < o + sz:
        seg = (o, sz, v, fl)
        break
assert seg is not None, "table not inside a single LOAD segment"
print("segment holding table: off=%x size=%x vaddr=%x flags=%x" % seg)

# count existing key strings in table [AccessToken .. end_of_table)
a0 = data.find(b"AccessToken")
assert 0 < a0 < s0
n = 0
o = a0
while o < end_of_table:
    e = data.find(b"\x00", o)
    assert e < end_of_table
    n += 1
    o = e + 1
print("existing keys:", n)

# find the type array: after OPENPILOT_PREFIX string, look for a 4-byte count n
# The C++ table is typically: static const pair<const char*, ParamKeyType> table[] with size known by array size (no count in binary).
# So NO count field exists; the array length is baked into code (bounds check). We must therefore also patch the code or use a different strategy.
# Strategy check: look for the type array (should be n 4-byte values of 0x02 mostly, near .rodata)
# Search for a run of n*4 bytes near the table where most values are 0x02 00 00 00
found_type_array = None
for base in range(s0 - 4096, end_of_table + 4096):
    ok = True
    cnt2 = 0
    for k in range(n):
        v = struct.unpack_from("<I", data, base + 4 * k)[0]
        if v in (0x02, 0x04, 0x08, 0x10, 0x20, 0x02 | 0x20):
            cnt2 += 1
    if cnt2 >= n * 3 // 4:
        found_type_array = base
        print("type array candidate at", base, "match", cnt2)
        if base > s0 - 2048:  # plausible location
            break

if found_type_array is not None:
    vals = [struct.unpack_from("<I", data, found_type_array + 4 * k)[0] for k in range(n)]
    print("first 20 type values:", vals[:20])
    print("distinct:", sorted(set(vals)))

