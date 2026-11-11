with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if i >= 4538 and 'elif path == \'/api/credentials/requests\':' in line:
        skip = True
    if skip and 'elif path == \'/api/settings\':' in line:
        skip = False
    if not skip:
        new_lines.append(line)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Cleaned duplicate /api/credentials/requests from do_POST")
