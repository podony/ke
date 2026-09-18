import re
with open("common/params.cc") as f:
    content = f.read()
# Find the full map definition
m = re.search(r'(std::(unordered_)?map<[^>]+>\s+\w+\s*=\s*\{.*?\};)', content, re.DOTALL)
if m:
    print(m.group(0)[:2000])
    print("...")
else:
    print("No map found, searching for checkKey")
    idx = content.find("checkKey")
    print(content[idx:idx+500])
