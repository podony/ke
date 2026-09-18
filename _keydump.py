import re
data = open('common/params_pyx.so','rb').read()
idents = re.findall(rb'[A-Za-z][A-Za-z0-9_]{2,40}', data)
uniq = sorted(set(i.decode() for i in idents))
open('_all_ids.txt','w').write('\n'.join(uniq))
print(len(uniq))
print([k for k in uniq if k.startswith('dp_')])
