with open('school_website/server.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'def do_GET' in l or (i < 2700 and 'elif path ==' in l):
            print(f"{i+1}: {l.strip()[:90]}")
