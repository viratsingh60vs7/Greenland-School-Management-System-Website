with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'DOMContentLoaded', text)]
for m in matches:
    print("DOMContentLoaded at", m)
    print(text[m:m+500])
    print("="*40)
