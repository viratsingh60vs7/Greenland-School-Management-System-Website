with open('school_website/server.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if "elif path == '/api/users/create':" in line:
            print(f"Line {i+1}: {line.strip()}")
