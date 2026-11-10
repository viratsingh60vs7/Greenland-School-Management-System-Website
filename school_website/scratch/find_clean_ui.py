with open('school_website/index.html', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if any(w in l.lower() for w in ['clean', 'clear', 'reset', 'seed']):
            print(f"{i+1}: {l.strip()[:100]}")
