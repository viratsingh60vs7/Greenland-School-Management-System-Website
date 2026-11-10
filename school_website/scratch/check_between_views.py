with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="portal-login-view"')
pos_container = text.find('id="portal-container"')
print("Between login view and container:")
print(text[pos_container-300:pos_container+50])
