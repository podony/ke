import struct
b = open("common/params_pyx.so","rb").read()
# 1. relocations targeting [0x4b900, 0x4bb80)
off=0xe590; n=0x4b30//24
hits = []
for k in range(n):
    r_off, r_info, r_add = struct.unpack_from("<QQq", b, off+k*24)
    if 0x4b900 <= r_off < 0x4bb80:
        hits.append((hex(r_off), r_info & 0xffffffff, hex(r_add)))
print("relocs in 0x4b900-0x4bb80:", hits)
# 2. adrp/add in .text targeting 0x4b900-0x4bb80
found = []
i = 0x16060
while i < 0x3bf30:
    v = struct.unpack_from("<I", b, i)[0]
    if (v & 0x9f000000) == 0x90000000:
        imm = ((v >> 21) & 0x7ffff)
        if imm & 0x100000: imm -= 0x200000
        page = (i & ~0xfff) + (imm << 12)
        v2 = struct.unpack_from("<I", b, i+4)[0]
        if (v2 & 0x7f000000) == 0x91000000:
            imm2 = (v2 >> 10) & 0xfff
            t = page + (imm2 << 12 if v2 & 0x80000000 else imm2)
            if 0x4b900 <= t < 0x4bb80:
                found.append((i,t))
    i += 4
print("code refs to 0x4b900-0x4bb80:", found)
# 3. bss zero check 0x4b900-0x4bb80
seg = b[0x4a900:0x4ab80]
print("bss 0x4b900-0x4bb80 all zero:", not any(seg))
# 4. e_type
print("e_type", struct.unpack_from("<H", b, 0x10)[0])
# 5. confirm 0x4b230 is start of bss and 0x4b800 map - any symbol at 0x4b230?
strtab_off = 0x2974c8; symtab_off = 0x28dce8
n2 = (0x2974c8 - symtab_off)//24
for k in range(n2):
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", b, symtab_off+k*24)
    if 0x4b230 <= st_value < 0x4bb80:
        end = b.find(b"\x00", strtab_off+st_name)
        nm = b[strtab_off+st_name:end].decode("latin1")
        print("bss symbol:", hex(st_value), st_size, nm[:60])
