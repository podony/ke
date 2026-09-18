import re
old = open('_old_params_full.cc', encoding='utf-8').read()
# extract everything before the keys table and everything after
m = re.search(r'(std::unordered_map<std::string, uint32_t> keys = \{)(.*?)(\n\};)', old, re.S)
pre, table, post = m.group(1), m.group(2), m.group(3)
prefix = old[:m.start(1)]
suffix = old[m.end(3):]

entries = re.findall(r'\{\s*"((?:[^"\\]|\\.)*)",\s*(\w+)\s*\}', table)
oldset = {k for k,_ in entries}
import json
so = set(x[0] for x in json.load(open('_keysoffs.json',encoding='utf-8')))
used = set(l.strip() for l in open('_used_keys.txt', encoding='utf-8') if l.strip())

# keys to include: all in .so (156) + used keys + a few known-needed
include = so | used
# also keep keys present in old source that are core (used by params code/tests)
extra = {'CarParams','carFingerprint','uniqueID','error_description','DoReboot','IsMetric','IsOnroad','IsTakingSnapshot','Version','TrainingVersion','DongleId','IMEI'}
include |= extra

# keep type from old entries if available, else PERSISTENT
typemap = dict(entries)
newentries = []
for k in sorted(include):
    t = typemap.get(k, 'PERSISTENT')
    newentries.append('    {"%s", %s},' % (k, t))

newtable = '\n' + '\n'.join(newentries) + '\n'
out = prefix + pre + newtable + post + suffix
open('common/params.cc','w',encoding='utf-8').write(out)
print('total keys:', len(newentries))
