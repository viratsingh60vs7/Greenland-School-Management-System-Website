with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if i >= 3031 and i < 3060 and "elif path == '/api/users/create':" in line:
        skip = True
    if skip and "elif path == '/api/admissions/inquire':" in line:
        skip = False
    if not skip:
        new_lines.append(line)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned older duplicate /api/users/create")
