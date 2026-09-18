# Extract all key entries from the new params.cc
import re
t = open('common/params.cc', encoding='utf-8').read()
m = re.search(r'std::unordered_map<std::string, uint32_t> keys = \{(.*?)\n\};', t, re.S)
body = m.group(1)
entries = re.findall(r'\{ "(.*?)", (\w+) \},', body)
print("total keys in params.cc:", len(entries))

# Verify all 7 dp_cam_decel keys are present
need = ['dp_cam_decel','dp_cam_decel_mode','dp_cam_decel_start','dp_cam_decel_end','dp_cam_decel_bump_dist','dp_cam_decel_bump_speed','dp_cam_decel_safety_factor']
have = {k for k,_ in entries}
missing = [k for k in need if k not in have]
print("dp_cam_decel missing:", missing)

# Verify all 156 keys from the old .so are present
import json
so_keys = set(x[0] for x in json.load(open('_keysoffs.json', encoding='utf-8')))
so_missing = [k for k in so_keys if k not in have]
print("old .so keys missing from params.cc:", so_missing)
