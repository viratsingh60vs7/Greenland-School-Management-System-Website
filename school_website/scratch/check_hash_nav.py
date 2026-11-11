with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function handleHashNavigation")
print(text[pos:pos+800])
