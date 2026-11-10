with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
pos = html.find('id="login"')
if pos != -1:
    print("Found id='login' at", pos)
    print(html[pos:pos+3000])
else:
    print("id='login' not found")
