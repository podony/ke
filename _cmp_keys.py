import re
cc = open(chr(99)+chr(111)+chr(109)+chr(109)+chr(111)+chr(110)+chr(47)+chr(112)+chr(97)+chr(114)+chr(97)+chr(109)+chr(115)+chr(46)+chr(99)+chr(99), encoding=chr(117)+chr(116)+chr(102)+chr(45)+chr(56)).read()
cc_keys = set()
i = 0
while True:
    s = cc.find(chr(123), i)
    if s < 0:
        break
    q1 = cc.find(chr(34), s)
    if q1 < 0:
        break
    q2 = cc.find(chr(34), q1+1)
    if q2 < 0:
        break
    cc_keys.add(cc[q1+1:q2])
    i = q2 + 1
so = open(chr(99)+chr(111)+chr(109)+chr(109)+chr(111)+chr(110)+chr(47)+chr(112)+chr(97)+chr(114)+chr(97)+chr(109)+chr(115)+chr(95)+chr(112)+chr(121)+chr(120)+chr(46)+chr(115)+chr(111), chr(114)+chr(98)).read()
idx = so.find(bytes([65,99,99,101,115,115,84,111,107,101,110])+bytes([0]))
print(chr(98)+chr(108)+chr(111)+chr(98), chr(115)+chr(116)+chr(97)+chr(114)+chr(116), hex(idx))
seg = so[idx-4: idx+6000]
out = []
cur = bytes([0])[:0]
for b in seg:
    if b == 0:
        if len(cur) >= 3:
            out.append(cur.decode(chr(117)+chr(116)+chr(102)+chr(45)+chr(56), chr(114)+chr(101)+chr(112)+chr(108)+chr(97)+chr(99)+chr(101)))
        cur = bytes([0])[:0]
    else:
        cur = cur + bytes([b])
if len(cur) >= 3:
    out.append(cur.decode(chr(117)+chr(116)+chr(102)+chr(45)+chr(56), chr(114)+chr(101)+chr(112)+chr(108)+chr(97)+chr(99)+chr(101)))
so_keys = set(out)
print(chr(99)+chr(99), chr(107)+chr(101)+chr(121)+chr(115), len(cc_keys), len(so_keys))
missing = cc_keys - so_keys
print(chr(77)+chr(73)+chr(83)+chr(83)+chr(73)+chr(78)+chr(71), len(missing))
for k in sorted(missing):
    print(k)
