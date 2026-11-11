with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(715, 765):
    print(lines[i], end='')
