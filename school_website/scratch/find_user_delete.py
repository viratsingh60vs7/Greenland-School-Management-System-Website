with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'DELETE FROM users', text, re.IGNORECASE)]
print("DELETE FROM users matches:", len(matches))
for m in matches:
    print(text[m-100:m+200])
    print("="*40)
