so = set(l.strip() for l in open('_so_keys.txt', encoding='utf-8') if l.strip())
used = set(l.strip() for l in open('_used_keys.txt', encoding='utf-8') if l.strip())
print("used but not in so:", sorted(used - so))
print("in so but not used:", len(so - used))
