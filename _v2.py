import re
t=open('common/params.cc',encoding='utf-8').read()
keys=re.findall(r'\{"(.*?)", (\w+),', t)
print(len(keys), 'dp_cam_decel' in [k for k,_ in keys], 'CarParams' in [k for k,_ in keys])
