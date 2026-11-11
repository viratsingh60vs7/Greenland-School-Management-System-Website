import re

def search_file(path):
    print(f"=== SEARCHING {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if any(k in line.lower() for k in ['excel', 'upload', 'import_student', 'bulk', 'aadhaar']):
                print(f"{i+1}: {line.strip()[:100]}")

search_file('school_website/server.py')
search_file('school_website/js/app.js')
search_file('school_website/index.html')
