import re
old = open('_old_params_full.cc', encoding='utf-8').read()
m = re.search(r'std::unordered_map<std::string, uint32_t> keys = \{(.*?)\n\};', old, re.S)
body = m.group(1)
oldkeys = re.findall(r'\{\s*"(.*?)",\s*(\w+)\s*\}', body)
print(len(oldkeys))
newkeys = [l.strip() for l in open('_so_keys.txt', encoding='utf-8') if l.strip()]
print(len(newkeys))
oldset = {k for k,_ in oldkeys}
missing = [k for k in newkeys if k not in oldset]
print('missing in old source:', missing)
removed = [k for k in oldset if k not in newkeys]
print('removed from so:', removed)
