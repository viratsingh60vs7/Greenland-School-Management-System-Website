with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'path == [\'"](/api/[^\'"]+)[\'"]', text)
user_endpoints = [m for m in matches if 'user' in m]
print('User endpoints in server.py:', user_endpoints)
