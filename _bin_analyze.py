import json, struct

with open('_keysoffs.json') as f:
    keysoffs = json.load(f)

with open('common/params_pyx.so', 'rb') as f:
    so = f.read()

print(f"Total .so size: {len(so)}")

# Analyze the key table region
# Keys are stored as: [name_length:u32][name_bytes][type:u32]
# Let's trace through the table from the first key offset
first_key_name, first_key_off = keysoffs[0]
print(f"\nFirst key: '{first_key_name}' at offset {first_key_off}")

# The offset points to the key name in the .so
# Let's see what's before the first key (should be table start pointer or count)
# and trace the full table structure

# Try to find the table: look at what's at first_key_off
# The format is likely: u32 count, then array of {char* name, u32 type}
# OR: array of {u32 len, char name[], u32 type}

# Let's examine bytes around the first key
print(f"\nBytes at first key offset ({first_key_off}):")
chunk = so[first_key_off-16:first_key_off+64]
print("  hex:", chunk.hex())
print("  ascii:", ''.join(chr(b) if 32<=b<127 else '.' for b in chunk))

# Check if it's null-terminated or length-prefixed
# Look at the byte right before the key name
print(f"\nByte before first key name: {so[first_key_off-1]:#x} ({so[first_key_off-1]})")
print(f"Byte before that: {so[first_key_off-2]:#x} ({so[first_key_off-2]})")
print(f"Byte before that: {so[first_key_off-3]:#x} ({so[first_key_off-3]})")

# Check what comes after the first key name
name_len = len(first_key_name)
after_name = first_key_off + name_len
print(f"\nFirst key name ends at offset {after_name}")
print(f"Bytes after first key name: {so[after_name:after_name+8].hex()}")
