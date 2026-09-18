d = open("common/params_pyx.so","rb").read()
for pat in [b"Py_LIMITED_API", b"_PyObject_GC_New", b"PyModule_Create", b"Python-3", b"libpython", b"libc++", b"libstdc++", b"__gxx_personality", b"_ZTVN10__cxxabiv1", b"__cxa_personality", b"PyUnicode"]:
    print(pat, d.find(pat))
# DT_NEEDED
import struct
def find_needed(data):
    i = data.find(b"DT_NEEDED")
    return i
print("first DT_NEEDED marker:", find_needed(d))
