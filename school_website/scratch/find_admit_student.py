with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'function submitAdmitStudent' in line:
            print(f"Line {i+1}: {line.strip()}")
            for j in range(i, i+35):
                print(lines[j], end='')
            break
