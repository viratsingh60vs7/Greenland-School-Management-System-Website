with open('school_website/server.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'def init_db(' in l or 'CREATE TABLE IF NOT EXISTS' in l:
            print(f"{i+1}: {l.strip()[:90]}")
