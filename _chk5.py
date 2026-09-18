b = open("common/params_pyx.so","rb").read()
gap = b[0x270a0:0x28090]
print("gap nonzero:", any(gap))
# find all occurrences of dp_0813 (code refs)
import re
target = b"dp_0813"
i = 0
while True:
    i = b.find(target, i)
    if i < 0: break
    print("dp_0813 at file", i, "VA", hex(i))
    i += 1
