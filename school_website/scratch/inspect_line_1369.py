with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1360, 1385):
    print(f"{i+1}: {repr(lines[i])}")
