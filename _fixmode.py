with open('common/params.cc', 'r') as f:
    lines = f.readlines()
# Insert dp_cam_decel_mode after line 215 (index 214)
insert_idx = 215
lines.insert(insert_idx, '    {"dp_cam_decel_mode", PERSISTENT},\n')
with open('common/params.cc', 'w') as f:
    f.writelines(lines)
print('done')
