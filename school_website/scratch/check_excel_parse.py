with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(357, 428):
    print(lines[i], end='')
