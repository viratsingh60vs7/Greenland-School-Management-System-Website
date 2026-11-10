with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="portal-container"')
print(text[pos:pos+1200])
