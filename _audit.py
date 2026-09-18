import capnp
c = capnp.load("cereal/custom.capnp")
assert c.RoadLimitSpeed, "no RoadLimitSpeed"
data = open("common/params_pyx.so","rb").read()
need = ["dp_cam_decel","dp_cam_decel_mode","dp_cam_decel_start","dp_cam_decel_end","dp_cam_decel_bump_dist","dp_cam_decel_bump_speed","dp_cam_decel_safety_factor"]
missing = [k for k in need if k.encode() not in data]
print("capnp OK; RoadLimitSpeed present; dp key missing:", missing)
# ELF check
print("ELF:", data[0:4]==b"\x7fELF", "class", data[4], "machine 0x%02x%02x" % (data[18], data[17]))
