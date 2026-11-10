with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find('portal-login-view')
if pos != -1:
    print("Found portal-login-view at", pos)
    print(html[pos:pos+4000])
else:
    print("portal-login-view not found")
