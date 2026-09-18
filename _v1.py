import re
t=open('common/params.cc',encoding='utf-8').read()
keys=re.findall(r'\{ "(.*?)", ', t)
print(len(keys), 'dp_cam_decel' in keys, 'CarParams' in keys)
