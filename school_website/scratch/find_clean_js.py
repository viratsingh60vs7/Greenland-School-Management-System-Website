with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if any(w in l.lower() for w in ['confirmcleantestdata', 'clean_test_data', 'seedfaculty', 'reset']):
            if any(w in l for w in ['function', 'button', 'fetch', 'api']):
                print(f"{i+1}: {l.strip()[:100]}")
