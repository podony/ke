import os, re, sys
pat = re.compile(r'(?:params\.get_bool|params\.get|params\.put|params\.remove|params\.all_keys|params\.clear_all)\(\s*["\']([^"\']+)["\']')
cpat = re.compile(r'params\.(?:get_bool|get|put|remove|allKeys|checkKey|clearAll)\(\s*"([^"]+)"')
used = set()
skip_dirs = {'.git'}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
    for f in files:
        if not (f.endswith('.py') or f.endswith('.cc') or f.endswith('.cpp') or f.endswith('.h')):
            continue
        p = os.path.join(root, f)
        try:
            txt = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for m in pat.finditer(txt):
            used.add(m.group(1))
        for m in cpat.finditer(txt):
            used.add(m.group(1))
used = sorted(used)
print(len(used))
open('_used_keys.txt','w',encoding='utf-8').write('\n'.join(used))
