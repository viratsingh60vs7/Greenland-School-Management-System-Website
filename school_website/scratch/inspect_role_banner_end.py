with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos2 = text.find('SUPER ADMIN PORTAL')
print(text[pos2:pos2+800])
