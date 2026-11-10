with open('school_website/server.py', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if '/api/lab/' in line:
            print(f"{i+1}: {line.strip()[:100]}")
