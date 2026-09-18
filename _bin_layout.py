import json, struct

with open('_keysoffs.json') as f:
    keysoffs = json.load(f)

with open('common/params_pyx.so', 'rb') as f:
    so = f.read()

# Let's look at the exact byte layout around the first few keys
first_name, first_off = keysoffs[0]
second_name, second_off = keysoffs[1]
third_name, third_off = keysoffs[2]

print(f"Key 0: '{first_name}' at {first_off}")
print(f"Key 1: '{second_name}' at {second_off}")
print(f"Key 2: '{third_name}' at {third_off}")
print(f"Gap key0->key1: {second_off - first_off} (name_len={len(first_name)}, +null+type = {len(first_name)+1+4})")
print(f"Gap key1->key2: {third_off - second_off} (name_len={len(second_name)}, +null+type = {len(second_name)+1+4})")

# So the format is: [name\0][u32 type] and the offset points to the START of the name
# Let's verify: what's at first_off + len(first_name) + 1?
after0 = first_off + len(first_name) + 1
print(f"\nAfter key0 name+null (at {after0}): {so[after0:after0+4].hex()} = {struct.unpack_from('<I', so, after0)[0]:#x}")

# What's before first_off?
print(f"Before key0 (at {first_off-8} to {first_off}): {so[first_off-8:first_off].hex()}")
# That's 00 00 00 00 00 00 00 00 - padding/null

# The 30 (0x1e) we saw earlier at first_off-16 is at offset 254872
# 254872 = first_off - 8 = 254880 - 8
# Wait, first_off is 254880
# first_off - 16 = 254864: 21 00 00 00 = 33 (0x21)
# first_off - 8 = 254872: 00 00 00 00 00 00 00 00

# Hmm, let me look at a wider region
print(f"\nBytes from {first_off-32} to {first_off+100}:")
for i in range(0, 132, 16):
    addr = first_off - 32 + i
    hexs = ' '.join(f'{b:02x}' for b in so[addr:addr+16])
    ascii_ = ''.join(chr(b) if 32<=b<127 else '.' for b in so[addr:addr+16])
    print(f"  {addr:6d}: {hexs}  {ascii_}")
