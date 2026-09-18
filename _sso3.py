import struct
d=open("common/params_pyx.so","rb").read()
# The map is at VA 0x4b800 (file 0x4a800) - runtime constructed.
# The KEY STRINGS are static literals in .rodata (offset 254880-257735).
# For the injected check, I compare x1 (the key) against these static literals.
# But I must read the key's bytes from x1 per the std::string ABI.
# Determine SSO: examine a known short key like "IMEI" (4 chars) handling in constructor.
# Simpler: check the libc++ version string in .comment / debug.
print("=== .comment ===")
# .comment file off 0x4a230 size 0x15b
print(d[0x4a230:0x4a230+0x15b].decode("latin1","replace"))
# Find SSO threshold: libc++15+ uses 23; older 15/16/17. EON NDK ~ r21 => libc++ 13 => SSO 23.
# Determine actual: look at how a 1-char/short string node is built.
# Actually, let's find the __hash_node layout by locating the operator[] callee.
from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True
def dis(va,n,label):
    print("=== %s (0x%x, %d insns) ===" % (label,va,n))
    for i in md.disasm(d[va:va+n], va):
        print("  %x  %-8s %s" % (i.address,i.mnemonic,i.op_str))
# operator[] at 0x14f80 (called by getKeyType) - it's the unordered_map::operator[]
dis(0x14f80, 0x40, "operator[] callee")
