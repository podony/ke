import re, json
t = open('common/params.cc', encoding='utf-8').read()
m = re.search(r'std::unordered_map<std::string, uint32_t> keys = \{(.*?)\n\};', t, re.S)
print("match:", bool(m))
if m:
    body = m.group(1)
    entries = re.findall(r'\{ "([^"]+)", (\w+) \}', body)
    print("total keys:", len(entries))
    need = ['dp_cam_decel','dp_cam_decel_mode','dp_cam_decel_start','dp_cam_decel_end','dp_cam_decel_bump_dist','dp_cam_decel_bump_speed','dp_cam_decel_safety_factor']
    have = {k for k,_ in entries}
    print("dp_cam_decel missing:", [k for k in need if k not in have])
    so_keys = set(x[0] for x in json.load(open('_keysoffs.json', encoding='utf-8')))
    print("old .so keys missing:", len(so_keys - have))
    used_keys = set(l.strip() for l in open('_used_keys.txt', encoding='utf-8') if l.strip())
    print("used keys missing:", [k for k in used_keys if k not in have])
else:
    print("table not found")
