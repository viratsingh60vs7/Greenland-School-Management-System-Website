with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find('portal-login-view')
print(html[pos+2000:pos+4500])
