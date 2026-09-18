import re,os
pat = re.compile(r'params\.(?:get|put|get_bool|remove)\(\s*["\'](\w+)["\']')
for k in ['CarParams','IMEI','Version','DongleId','uniqueID','error_description','carFingerprint']:
    hits = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            if not f.endswith('.py'): continue
            p = os.path.join(root,f)
            txt = open(p, encoding='utf-8', errors='ignore').read()
            for m in pat.finditer(txt):
                if m.group(1)==k:
                    hits.append(p)
    print(k, len(hits), hits[:5])
