with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "path == '/api/users/create':" in l:
        print(f"Line {i+1}: {l}")
        for j in range(i, i+45):
            print(f"{j+1}: {lines[j]}", end='')
        break
