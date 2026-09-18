
src = r"""import re, os
keys = set()
pat1 = r"(?:params|p)\s*\.\s*(?:get|get_bool|put|put_bool|remove|check_key|get_param_path|all_keys)\(\s*[q]([A-Za-z0-9_]+)"
pat2 = r"put(?:_bool)?_nonblocking\(\s*[q]([A-Za-z0-9_]+)"
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
    for f in files:
        if f.endswith((".py", ".pyx", ".cc", ".cpp", ".h")):
            p = os.path.join(root, f)
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for pat in (pat1, pat2):
                for m in re.finditer(pat, txt):
                    keys.add(m.group(1))
mp = open("selfdrive/manager/manager.py", encoding="utf-8").read()
for m in re.finditer(r"^\s*\(\s*[q]([A-Za-z0-9_]+)[q]\s*,", mp, re.M):
    keys.add(m.group(1))
print("referenced:", len(keys))
data = open("common/params_pyx.so", "rb").read()
i = data.find(b"AccessToken")
j = data.find(b"OPENPILOT_PREFIX")
inso = set()
o = i
while o < j:
    e = data.find(b"\0", o)
    inso.add(data[o:e].decode())
    o = e + 1
print("in .so table:", len(inso))
missing = sorted(k for k in keys if k not in inso)
print("MISSING:", len(missing))
for k in missing:
    print("  " + k)
"""
# replace placeholder [q] with a char class matching both quote types
src = src.replace("[q]", "[\x27\"]")
open("_scankeys.py", "w", newline="").write(src)
print("written")

