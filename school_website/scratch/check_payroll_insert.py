with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(5310, 5360):
    print(lines[j], end='')
