import re
with open('common/params.cc') as f:
    content = f.read()
keys = re.findall(r'\{"(\w+)",\s*(\w+)\}', content)
print(f"total keys in params.cc: {len(keys)}")
dp = [k for k,t in keys if 'dp_cam' in k]
print(f"dp_cam keys ({len(dp)}): {dp}")
