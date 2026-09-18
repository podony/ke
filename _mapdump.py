import struct
d=open("common/params_pyx.so","rb").read()
base=0x4a800  # file offset of map object
def u32(o): return struct.unpack_from("<I",d,o)[0]
def u64(o): return struct.unpack_from("<Q",d,o)[0]
print("map object at file 0x4a800, dump 0x40 bytes:")
for i in range(0,0x40,8):
    va=base+i
    print("  +0x%02x va=%x : %s  (u64=%x, u32 lo=%x)" % (i, va+0x1000, d[va:va+8].hex(), u64(va), u32(va)))
# The libc++ hash_table first member is __bucket_list_begin (a node ptr, offset 0)
# Let's interpret
print()
print("Interpretation (libc++ __hash_table):")
print("  [0x00] _M_begin_before_first (bucket head node ptr):", hex(u64(base)))
# __hash_table layout: 
# struct __hash_table { __hash_table_data { __bucket_list_begin; __begin_node; __bucket_count; __one_bucket; ... } ; __hash; __equal; }
# Actually order: __bucket_list_begin (offset 0), __begin_node (offset 8), __bucket_count (offset 16), 
# __one_bucket / __bucket_array ptr (offset 24), then __hash (32), __equal (40)
print("  [0x08] __begin_node ptr:", hex(u64(base+8)))
print("  [0x10] __bucket_count:", u64(base+0x10))
print("  [0x18] __one_bucket/buckets ptr:", hex(u64(base+0x18)))
print("  [0x20] __hash obj (func ptr):", hex(u64(base+0x20)))
print("  [0x28] __equal obj (func ptr):", hex(u64(base+0x28)))
print()
print("Note: getKeyType reads [x0,#0x28] where x0 is the *node* returned by operator[] (not the map). So 0x28 is node's value offset, not map offset.")
