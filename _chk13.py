import struct
b = open("common/params_pyx.so","rb").read()
ro = b[254880:257735]
parts = ro.split(b"\x00")
s = [p.decode("latin1") for p in parts if p]
print("total keys:", len(s))
print("min len:", min(len(x) for x in s), "max len:", max(len(x) for x in s))
# check for any key that is a prefix of another
pref = 0
for a in s:
    for c in s:
        if a != c and c.startswith(a):
            pref += 1
print("prefix collisions:", pref)
# check that no key is a substring of another key (for raw byte search)
sub = 0
for a in s:
    for c in s:
        if a != c and a in c:
            sub += 1
print("substring collisions:", sub)
