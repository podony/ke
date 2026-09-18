import json, struct
d = open("common/params_pyx.so","rb").read()
ks = json.load(open("_keysoffs.json"))  # [name, fileoff]
# find dp_cam string offsets in boltpilot params.cc constructor style: we just need to place new strings
# Locate the key-string block start/end
offs = sorted(int(o,16) if isinstance(o,str) else o for _,o in ks)
print("first", hex(offs[0]), "last end approx")
# check what is at end of string block: read bytes after last string until 0x46000
last_name, last_off = ks[-1]
lo = int(last_off,16) if isinstance(last_off,str) else last_off
end = lo + len(last_name) + 1
print("block end", hex(end))
# check .data.rel.ro region content 0x46628..: is it the map static? keys map at 0x4a800 (in .bss? bss starts 0x4a230 yes)
# Check .rodata tail after 0x3bf30+0x3df1=0x3fD21
ro_end = 0x3bf30+0x3df1
print("rodata end", hex(ro_end))
print(d[end:end+200].hex())
