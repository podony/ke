import re
t=open('common/params.cc',encoding='utf-8').read()
i=t.find('dp_cam_decel')
print(repr(t[i-5:i+20]))
keys=re.findall(r'\{ "(.*?)", (\w+)\}', t)
print(len(keys))
