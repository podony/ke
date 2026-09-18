import capnp
c = capnp.load("cereal/custom.capnp")
print("capnp load OK, RoadLimitSpeed:", c.RoadLimitSpeed)
