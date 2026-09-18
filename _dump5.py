data = open('common/params_pyx.so','rb').read()
i0 = data.find(b"AccessToken")
i1 = data.find(b"WheeledBody")
seg = data[i0-1:i1+10]
keys = [k.decode("latin1") for k in seg.split(b"\x00")]
keys = [k for k in keys if k]
print("count from AccessToken..WheeledBody:", len(keys))
print("first:", keys[:5])
print("last:", keys[-5:])
