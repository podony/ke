with open("common/params.cc") as f:
    content = f.read()
# print the map definition section
lines = content.split("\n")
for i, l in enumerate(lines):
    if "params_keymap" in l or "unordered_map" in l or "std::map" in l:
        for j in range(max(0,i-2), min(len(lines), i+5)):
            print(f"{j+1}: {lines[j]}")
        print("...")
        break
