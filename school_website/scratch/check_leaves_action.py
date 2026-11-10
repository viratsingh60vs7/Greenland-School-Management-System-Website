with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "path == '/api/leaves/action':" in l:
        for j in range(i, i+35):
            print(f"{j+1}: {lines[j]}", end='')
        break
