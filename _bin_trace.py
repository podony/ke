import json, struct

with open('_keysoffs.json') as f:
    keysoffs = json.load(f)

with open('common/params_pyx.so', 'rb') as f:
    so = bytearray(f.read())

# Key table format:
# [u32 name_len][name_bytes (null-terminated)][u32 type]
# The table starts at some offset with u32 count, then the entries.

# Let's find the table start by looking before the first key
first_name, first_off = keysoffs[0]
# The first key name is at first_off
# Before it should be: u32 name_len (4 bytes), before that: u32 count (4 bytes)?
# Let's check:
count_off = first_off - 4  # this should be the name_len for first key
name_len_val = struct.unpack_from('<I', so, count_off)[0]
print(f"Value before first key name (at {count_off}): {name_len_val} (should be {len(first_name)})")

# Check if there's a count before that
table_start = count_off - 4
count_val = struct.unpack_from('<I', so, table_start)[0]
print(f"Value at table_start ({table_start}): {count_val} (should be {len(keysoffs)})")

# Now trace the full table to find where it ends
print(f"\nTracing table from {table_start}:")
pos = table_start + 4  # skip count
entries = []
for i in range(len(keysoffs)):
    name_len = struct.unpack_from('<I', so, pos)[0]
    pos += 4
    name = bytes(so[pos:pos+name_len]).decode('utf-8', errors='replace')
    # name is null-terminated, so next is null byte
    pos += name_len
    # skip null terminator
    if pos < len(so) and so[pos] == 0:
        pos += 1
    type_val = struct.unpack_from('<I', so, pos)[0]
    pos += 4
    entries.append((name, type_val))
    if i < 3 or i >= len(keysoffs)-3:
        print(f"  [{i}] '{name}' type={type_val:#x}")

print(f"  ... {len(entries)} entries total")
print(f"Table end offset: {pos}")
print(f"Bytes at table end: {so[pos:pos+16].hex()}")
print(f"Bytes after: {''.join(chr(b) if 32<=b<127 else '.' for b in so[pos:pos+32])}")
