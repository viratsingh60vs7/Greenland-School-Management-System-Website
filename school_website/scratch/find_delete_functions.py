with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+([a-zA-Z0-9_]*delete[a-zA-Z0-9_]*)\s*\(', text, re.IGNORECASE)
print('Delete functions in app.js:', matches)
matches2 = re.findall(r'confirmDelete[a-zA-Z0-9_]*', text)
print('confirmDelete matches in app.js:', set(matches2))
