with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+([a-zA-Z0-9_]*User[a-zA-Z0-9_]*)\s*\(', text)
print('User functions in app.js:', matches)

matches2 = re.findall(r'render[a-zA-Z0-9_]*User[a-zA-Z0-9_]*', text)
print('Render user occurrences:', set(matches2))
