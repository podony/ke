import re
t = open('common/params.cc', encoding='utf-8').read()
m = re.search(r'std::unordered_map<std::string, uint32_t> keys = \{(.*?)\n\};', t, re.S)
body = m.group(1)
entries = re.findall(r'\{ "([^"]+)", (\w+) \}', body)
print("total keys in params.cc:", len(entries))

need = ['dp_cam_decel','dp_cam_decel_mode','dp_cam_decel_start','dp_cam_decel_end','dp_cam_decel_bump_dist','dp_cam_decel_bump_speed','dp_cam_decel_safety_factor']
have = {k for k,_ in entries}
missing = [k for k in need if k not in have]
print("dp_cam_decel missing:", missing)

import json
so_keys = set(x[0] for x in json.load(open('_keysoffs.json', encoding='utf-8')))
so_missing = [k for k in so_keys if k not in have]
print("old .so keys missing from params.cc:", len(so_missing), so_missing[:10])

# Also check all used keys are present
used_keys = set(l.strip() for l in open('_used_keys.txt', encoding='utf-8') if l.strip())
used_missing = [k for k in used_keys if k not in have]
print("used keys missing:", used_missing)
