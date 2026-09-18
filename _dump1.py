data = open('common/params_pyx.so','rb').read()
i = data.find(b"dp_alka")
print(hex(i))
print(repr(data[i-200:i+80]))
