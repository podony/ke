import json

with open('_keysoffs.json') as f:
    keysoffs = json.load(f)

print(f"Type: {type(keysoffs)}")
print(f"Keys in .so: {len(keysoffs)}")
print(f"First 5: {keysoffs[:5]}")
print(f"Last 5: {keysoffs[-5:]}")

with open('common/params_pyx.so', 'rb') as f:
    so = f.read()
print(f"\n.so size: {len(so)} bytes")
