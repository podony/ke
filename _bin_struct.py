import json, struct

with open('_keysoffs.json') as f:
    keysoffs = json.load(f)

with open('common/params_pyx.so', 'rb') as f:
    so = bytearray(f.read())

# The format is: [u32 count][u32 total_data_size][key_name\0 repeated]
# Let's trace the actual table
# keysoffs gives [name, offset_of_name_start]

# First key at 254880, let's find count and size fields before it
# 254848: 31 00 00 00 = 49
# 254856: 25 00 00 00 = 37  
# 254864: 21 00 00 00 = 33
# 254872: 1e 00 00 00 = 30
# 254880: 'AccessToken\0'

# Wait - these u32 values (49, 37, 33, 30) don't look like a count of 156
# They look like... offsets? Or sizes of preceding data?
# Let me check: maybe the table is in a different format

# Let's find ALL the key names in the .rodata section
# and figure out where the type values are

# Check: are type values stored separately?
# In params.cc, the table is:
#   static const std::unordered_map<std::string, ParamKeyType> params_keymap = {
#     {"key", PERSISTENT}, ...
#   };
# 
# In compiled ARM64, std::unordered_map stores entries in a separate bucket array.
# The key strings are in .rodata, but the map structure (pointers, types) is in .data.rel.ro

# Let me look for the type values (0x02 = PERSISTENT) near the key strings
# Actually, let me look at what the Cython wrapper expects

# The pyx calls: p.checkKey(key) which calls C++ Params::checkKey
# checkKey does: return params_keymap.find(key) != params_keymap.end()

# So the map is a global static. In ARM64, static data goes in .data.rel.ro or .bss
# Let's search for the pattern of type values

# For now, let's try a different approach: find where in .rodata the keys end
# and see if there's room to add new keys right after

last_name, last_off = keysoffs[-1]
last_end = last_off + len(last_name) + 1  # + null terminator
print(f"Last key: '{last_name}' at {last_off}, ends at {last_end}")
print(f"Bytes after last key: {so[last_end:last_end+32].hex()}")
print(f"ASCII: {''.join(chr(b) if 32<=b<127 else '.' for b in so[last_end:last_end+32])}")

# Find the first key
first_name, first_off = keysoffs[0]
print(f"\nFirst key: '{first_name}' at {first_off}")

# Total span of key data
total_span = last_end - first_off
print(f"Total key data span: {total_span} bytes (from {first_off} to {last_end})")

# New keys to add
new_keys = [
    "dp_cam_decel",
    "dp_cam_decel_mode", 
    "dp_cam_decel_start",
    "dp_cam_decel_end",
    "dp_cam_decel_bump_dist",
    "dp_cam_decel_bump_speed",
    "dp_cam_decel_safety_factor",
]
new_data = b""
for k in new_keys:
    new_data += k.encode() + b'\x00'
print(f"\nNew data to insert: {len(new_data)} bytes")
print(f"New keys: {new_keys}")

# Check if the .rodata section has enough space after the keys
# or if we need to find free space elsewhere
