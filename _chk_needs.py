with open('common/params_pyx.so','rb') as f:
    data = f.read()
for name in [b'libzmq', b'libjson', b'libstdc++', b'libc++', b'libpython', b'libpthread', b'libm.so', b'libc.so', b'libz.so']:
    if name in data:
        print(f"Found: {name.decode()}")
    else:
        print(f"Not found: {name.decode()}")
