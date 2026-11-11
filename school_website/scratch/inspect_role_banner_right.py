with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos2 = text.find('class="role-switcher-banner')
print(text[pos2+400:pos2+1200])
