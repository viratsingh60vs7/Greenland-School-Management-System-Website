with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'fillLogin', js)]
for m in matches:
    print("Match at", m)
    print(js[max(0, m-200):min(len(js), m+600)])
    print("="*50)
