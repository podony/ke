import struct

with open("common/params_pyx.so", "rb") as f:
    so = f.read()

# .data section: addr=0x0004a000 off=0x00049000 size=0x00001230
# .bss section: addr=0x0004b230 off=0x0004a230 size=0x00000950

# Key strings are in .rodata at file offsets ~254880-257752
# For a static unordered_map, the string literals are pointers in .data.rel.ro
# Let's search for the address of the first key string in .data.rel.ro

# First key "AccessToken" is at file offset 254880 = 0x3E3A0
# In .rodata: addr = 0x0003bf30 + (0x3E3A0 - 0x0003bf30) = 0x0003E3A0
first_key_vaddr = 0x0003E3A0
print(f"First key vaddr: 0x{first_key_vaddr:08x}")

# Search for this address in .data.rel.ro
data_rel_ro_offset = 0x00046628
data_rel_ro_size = 0x0001bb8
data_rel_ro = so[data_rel_ro_offset:data_rel_ro_offset+data_rel_ro_size]

# Search for the 8-byte little-endian representation of first_key_vaddr
target = struct.pack('<Q', first_key_vaddr)
print(f"Searching for {target.hex()} in .data.rel.ro ({data_rel_ro_size} bytes)...")

found = []
for i in range(len(data_rel_ro) - 7):
    if data_rel_ro[i:i+8] == target:
        found.append(i)
        print(f"  Found at .data.rel.ro offset {i} (file offset {data_rel_ro_offset+i})")

if not found:
    print("  Not found in .data.rel.ro")
    # Try .data
    data_offset = 0x00049000
    data_size = 0x00001230
    data = so[data_offset:data_offset+data_size]
    for i in range(len(data) - 7):
        if data[i:i+8] == target:
            found.append(data_offset + i)
            print(f"  Found in .data at file offset {data_offset+i}")

    if not found:
        print("  Not found in .data either")
        # The map might use RELATIVE addressing (ARM64)
        # Or the strings might be accessed differently
        # Let's check the .rela.dyn for relocations pointing to .rodata
        print("\nChecking relocations...")
