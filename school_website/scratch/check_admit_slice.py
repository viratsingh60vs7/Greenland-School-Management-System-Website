with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(215, 335):
    print(lines[i], end='')
