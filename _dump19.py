import struct
data = open('common/params_pyx.so','rb').read()
# Find the C string "checkKey" in the .rodata (the exception message) and the Params::checkKey symbol.
for name in [b"checkKey", b"UnknownKeyName", b"unknown key"]:
    i = data.find(name)
    print(name, "at", hex(i) if i>=0 else "NOT FOUND")
# Look for the Params::checkKey mangled symbol in .dynsym / symtab
i = data.find(b"_ZN6Params8checkKey")
print("Params::checkKey symbol at", hex(i) if i>=0 else "NOT FOUND")
# search for any symbol containing checkKey
import re
for m in re.finditer(rb"[A-Za-z_]\w{10,}checkKey\w*", data):
    print("sym:", m.group().decode("latin1"), hex(m.start()))
