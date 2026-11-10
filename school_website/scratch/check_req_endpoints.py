with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'path == [\'\"](/api/[^\'\"]+)[\'\"]', text)
for m in matches:
    if any(k in m for k in ['leave', 'lab', 'credential', 'request']):
        print(m)
