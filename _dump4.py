data = open('common/params_pyx.so','rb').read()
print('dp_cam_decel in so:', b"dp_cam_decel" in data)
# full key table: find the start. The keys region starts well before WheeledBody. Find the beginning of the C string array by scanning for the first uppercase param name.
i0 = data.find(b"WheeledBody")
# walk backwards over null-separated strings to find array start
start = i0
while True:
    prev = data.rfind(b"\x00", 0, start)
    if prev < 0: break
    start = prev
# now data[start:] up to end of region. Instead, extract maximal run of null-separated short strings around the region.
i1 = data.find(b"dp_vag_timebomb_bypass") + len(b"dp_vag_timebomb_bypass")
seg = data[start:i1+1]
keys = [k.decode('latin1') for k in seg.split(b"\x00")]
print('total keys in table:', len([k for k in keys if k]))
