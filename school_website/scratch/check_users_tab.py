with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'submitCreateUser' in line or 'openEditCredentialsModal' in line:
            print(f"{i+1}: {line.strip()[:90]}")
