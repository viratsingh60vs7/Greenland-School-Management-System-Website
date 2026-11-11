with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'async function renderStudentsTab' in l:
        print(f"renderStudentsTab at line {i+1}")
        for j in range(i, i+50):
            print(lines[j], end='')
        break
