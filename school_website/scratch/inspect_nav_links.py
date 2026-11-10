with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('class="nav-links"')
print(text[pos:pos+1000])
