with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find('portal-login-view')
print(html[pos:pos+4500])
