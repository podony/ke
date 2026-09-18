import re
data=open("common/params_pyx.so","rb").read()
for sym in [b"checkKey",b"getKeyType",b"allKeys",b"clearAll",b"check_key",b"UnknownKeyName",b"params_do_exit",b"ensure_params_path",b"OPENPILOT_PREFIX",b"dp_0813",b"dp_cam_decel"]:
    cnt=len(re.findall(re.escape(sym),data))
    idxs=[m.start() for m in re.finditer(re.escape(sym),data)][:6]
    print("%-20s count=%d first=%s" % (sym.decode(), cnt, idxs))
