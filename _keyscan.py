
import re, os
keys = set()
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
    for f in files:
        if f.endswith((".py", ".pyx", ".cc", ".cpp", ".h")):
            p = os.path.join(root, f)
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for m in re.finditer(r"(?:params|p|Params)\s*\.\s*(?:get|get_bool|put|put_bool|remove|check_key|get_param_path|all_keys)\(\s*[\x27\"]([A-Za-z0-9_]+)", txt):
                keys.add(m.group(1))
            for m in re.finditer(r"put(?:_bool)?_nonblocking\(\s*[\x27\"]([A-Za-z0-9_]+)", txt):
                keys.add(m.group(1))
print(len(keys))
print(" ".join(sorted(keys)))


data = open("common/params_pyx.so", "rb").read()
i = data.find(b"AccessToken")
j = data.find(b"dp_0813")
inso = []
o = i
while o < j:
    e = data.find(b"\0", o)
    inso.append(data[o:e].decode())
    o = e + 1
missing = sorted(k for k in keys if k not in inso)
print("in .so:", len(inso))
print("MISSING from .so table:")
for k in missing:
    print(" ", k)

