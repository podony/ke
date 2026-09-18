import capnp, importlib.util
spec = importlib.util.spec_from_file_location("custom_capnp_test", "x")
try:
    f = capnp.load("cereal/custom.capnp")
    print("CUSTOM CAPNP OK")
except Exception as e:
    print("CUSTOM CAPNP FAIL:", repr(e))
