with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function submitCreateUser")
print(text[pos:pos+900])
