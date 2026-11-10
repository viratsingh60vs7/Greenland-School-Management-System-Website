with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="portal-login-view"')
pos2 = text.find('id="portal-container"')
print(text[pos2-200:pos2+200])
